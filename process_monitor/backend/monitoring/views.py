from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import render
from django.http import JsonResponse
from .models import Host, ProcessSnapshot, Process
from .serializers import (
    HostSerializer, ProcessSnapshotSerializer, ProcessSerializer,
    ProcessDataSerializer
)


class HostListView(generics.ListAPIView):
    """API view to list all hosts"""
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    permission_classes = [AllowAny]


class ProcessSnapshotListView(generics.ListAPIView):
    """API view to list process snapshots for a specific host"""
    serializer_class = ProcessSnapshotSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        hostname = self.kwargs.get('hostname')
        if hostname:
            return ProcessSnapshot.objects.filter(host__hostname=hostname)[:10]  # Last 10 snapshots
        return ProcessSnapshot.objects.all()[:10]


class LatestProcessesView(generics.RetrieveAPIView):
    """API view to get the latest processes for a specific host"""
    serializer_class = ProcessSnapshotSerializer
    permission_classes = [AllowAny]
    
    def get_object(self):
        hostname = self.kwargs.get('hostname')
        try:
            host = Host.objects.get(hostname=hostname)
            return host.snapshots.first()
        except Host.DoesNotExist:
            return None


@api_view(['POST'])
def submit_process_data(request):
    """
    API endpoint for agents to submit process data
    """
    serializer = ProcessDataSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            {'error': 'Invalid data format', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = serializer.validated_data
    
    try:
        # Get or create host
        host, created = Host.objects.get_or_create(
            hostname=data['hostname'],
            defaults={
                'ip_address': data.get('ip_address'),
                'os_info': data.get('os_info'),
                'cpu_cores': data.get('cpu_cores'),
                'cpu_frequency': data.get('cpu_frequency'),
                'total_memory_gb': data.get('total_memory_gb'),
                'disk_total_gb': data.get('disk_total_gb'),
                'disk_free_gb': data.get('disk_free_gb'),
                'disk_usage_percent': data.get('disk_usage_percent'),
                'uptime': data.get('uptime'),
            }
        )
        
        # Update host last_seen timestamp and other fields
        host.last_seen = timezone.now()
        if data.get('ip_address'):
            host.ip_address = data['ip_address']
        if data.get('os_info'):
            host.os_info = data['os_info']
        if data.get('cpu_cores'):
            host.cpu_cores = data['cpu_cores']
        if data.get('cpu_frequency'):
            host.cpu_frequency = data['cpu_frequency']
        if data.get('total_memory_gb'):
            host.total_memory_gb = data['total_memory_gb']
        if data.get('disk_total_gb'):
            host.disk_total_gb = data['disk_total_gb']
        if data.get('disk_free_gb'):
            host.disk_free_gb = data['disk_free_gb']
        if data.get('disk_usage_percent'):
            host.disk_usage_percent = data['disk_usage_percent']
        if data.get('uptime'):
            host.uptime = data['uptime']
        host.save()
        
        # Create process snapshot
        snapshot = ProcessSnapshot.objects.create(
            host=host,
            total_processes=len(data['processes'])
        )
        
        # Create process records
        processes_created = 0
        for process_data in data['processes']:
            try:
                Process.objects.create(
                    snapshot=snapshot,
                    pid=process_data.get('pid'),
                    name=process_data.get('name', 'Unknown'),
                    cmdline=process_data.get('cmdline', ''),
                    parent_pid=process_data.get('parent_pid'),
                    cpu_percent=process_data.get('cpu_percent', 0.0),
                    memory_percent=process_data.get('memory_percent', 0.0),
                    memory_rss=process_data.get('memory_rss', 0),
                    memory_vms=process_data.get('memory_vms', 0),
                    status=process_data.get('status', ''),
                    username=process_data.get('username', ''),
                    create_time=process_data.get('create_time'),
                )
                processes_created += 1
            except Exception as e:
                # Log the error but continue processing other processes
                print(f"Error creating process record: {e}")
                continue
        
        return Response({
            'message': 'Process data received successfully',
            'host': host.hostname,
            'snapshot_id': snapshot.id,
            'processes_created': processes_created,
            'timestamp': snapshot.timestamp
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': 'Failed to process data', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_process_tree(request, hostname):
    """
    API endpoint to get process tree for a specific host
    """
    try:
        host = Host.objects.get(hostname=hostname)
        latest_snapshot = host.snapshots.first()
        
        if not latest_snapshot:
            return Response(
                {'error': 'No process data found for this host'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get root processes (processes with no parent or parent not in snapshot)
        all_processes = latest_snapshot.processes.all()
        pids_in_snapshot = set(p.pid for p in all_processes)
        
        root_processes = []
        for process in all_processes:
            if not process.parent_pid or process.parent_pid not in pids_in_snapshot:
                root_processes.append(process)
        
        # Build process tree
        def build_tree(processes):
            tree = []
            for process in processes:
                children = all_processes.filter(parent_pid=process.pid)
                process_data = {
                    'id': process.id,
                    'pid': process.pid,
                    'name': process.name,
                    'cmdline': process.cmdline,
                    'cpu_percent': process.cpu_percent,
                    'memory_percent': process.memory_percent,
                    'memory_rss': process.memory_rss,
                    'memory_vms': process.memory_vms,
                    'status': process.status,
                    'username': process.username,
                    'children': build_tree(children) if children.exists() else []
                }
                tree.append(process_data)
            return tree
        
        tree = build_tree(root_processes)
        
        return Response({
            'hostname': hostname,
            'timestamp': latest_snapshot.timestamp,
            'total_processes': latest_snapshot.total_processes,
            'process_tree': tree
        })
        
    except Host.DoesNotExist:
        return Response(
            {'error': 'Host not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve process tree', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_system_resources(request, hostname):
    """
    API endpoint to get system resource information for a specific host
    """
    try:
        host = Host.objects.get(hostname=hostname)
        latest_snapshot = host.snapshots.first()
        
        if not latest_snapshot:
            return Response(
                {'error': 'No process data found for this host'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate system resource usage from process data
        processes = latest_snapshot.processes.all()
        
        # Calculate total CPU and memory usage
        total_cpu = sum(p.cpu_percent for p in processes if p.cpu_percent)
        total_memory_rss = sum(p.memory_rss for p in processes if p.memory_rss)
        total_memory_vms = sum(p.memory_vms for p in processes if p.memory_vms)
        
        # Count processes by status
        status_counts = {}
        for process in processes:
            status = process.status or 'unknown'
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Get top processes by CPU and memory
        top_cpu_processes = sorted(
            processes, 
            key=lambda x: x.cpu_percent or 0, 
            reverse=True
        )[:5]
        
        top_memory_processes = sorted(
            processes, 
            key=lambda x: x.memory_rss or 0, 
            reverse=True
        )[:5]
        
        return Response({
            'hostname': hostname,
            'timestamp': latest_snapshot.timestamp,
            'total_processes': latest_snapshot.total_processes,
            'system_resources': {
                'total_cpu_percent': round(total_cpu, 2),
                'total_memory_rss': total_memory_rss,
                'total_memory_vms': total_memory_vms,
                'process_status_counts': status_counts,
                'top_cpu_processes': [
                    {
                        'name': p.name,
                        'pid': p.pid,
                        'cpu_percent': p.cpu_percent or 0,
                        'memory_percent': p.memory_percent or 0
                    } for p in top_cpu_processes
                ],
                'top_memory_processes': [
                    {
                        'name': p.name,
                        'pid': p.pid,
                        'memory_rss': p.memory_rss or 0,
                        'memory_percent': p.memory_percent or 0
                    } for p in top_memory_processes
                ]
            }
        })
        
    except Host.DoesNotExist:
        return Response(
            {'error': 'Host not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve system resources', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def frontend_view(request):
    """
    Render the frontend HTML page
    """
    return render(request, 'frontend/index.html')
