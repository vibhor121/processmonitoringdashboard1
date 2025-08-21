from rest_framework import serializers
from .models import Host, ProcessSnapshot, Process


class ProcessSerializer(serializers.ModelSerializer):
    """Serializer for Process model"""
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Process
        fields = [
            'id', 'pid', 'name', 'cmdline', 'parent_pid', 'cpu_percent',
            'memory_percent', 'memory_rss', 'memory_vms', 'status',
            'username', 'create_time', 'children'
        ]
    
    def get_children(self, obj):
        """Get child processes recursively"""
        children = Process.objects.filter(snapshot=obj.snapshot, parent_pid=obj.pid)
        return ProcessTreeSerializer(children, many=True).data


class ProcessTreeSerializer(serializers.ModelSerializer):
    """Simplified serializer for process tree structure"""
    class Meta:
        model = Process
        fields = [
            'id', 'pid', 'name', 'cmdline', 'parent_pid', 'cpu_percent',
            'memory_percent', 'memory_rss', 'memory_vms', 'status', 'username'
        ]


class ProcessSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for ProcessSnapshot model"""
    processes = ProcessTreeSerializer(many=True, read_only=True)
    hostname = serializers.CharField(source='host.hostname', read_only=True)
    
    class Meta:
        model = ProcessSnapshot
        fields = ['id', 'hostname', 'timestamp', 'total_processes', 'processes']


class HostSerializer(serializers.ModelSerializer):
    """Serializer for Host model"""
    latest_snapshot = serializers.SerializerMethodField()
    
    class Meta:
        model = Host
        fields = [
            'id', 'hostname', 'ip_address', 'os_info', 'cpu_cores', 'cpu_frequency',
            'total_memory_gb', 'disk_total_gb', 'disk_free_gb', 'disk_usage_percent',
            'uptime', 'first_seen', 'last_seen', 'latest_snapshot'
        ]
    
    def get_latest_snapshot(self, obj):
        """Get the latest snapshot for this host"""
        latest = obj.snapshots.first()
        if latest:
            return ProcessSnapshotSerializer(latest).data
        return None


class ProcessDataSerializer(serializers.Serializer):
    """Serializer for incoming process data from agent"""
    hostname = serializers.CharField(max_length=255)
    ip_address = serializers.IPAddressField(required=False, allow_null=True)
    os_info = serializers.CharField(max_length=255, required=False, allow_null=True)
    cpu_cores = serializers.IntegerField(required=False, allow_null=True)
    cpu_frequency = serializers.CharField(max_length=50, required=False, allow_null=True)
    total_memory_gb = serializers.FloatField(required=False, allow_null=True)
    disk_total_gb = serializers.FloatField(required=False, allow_null=True)
    disk_free_gb = serializers.FloatField(required=False, allow_null=True)
    disk_usage_percent = serializers.FloatField(required=False, allow_null=True)
    uptime = serializers.CharField(max_length=50, required=False, allow_null=True)
    processes = serializers.ListField(
        child=serializers.DictField(),
        allow_empty=True
    )
    
    def validate_processes(self, value):
        """Validate process data structure"""
        required_fields = ['pid', 'name']
        for process in value:
            for field in required_fields:
                if field not in process:
                    raise serializers.ValidationError(f"Process missing required field: {field}")
        return value 