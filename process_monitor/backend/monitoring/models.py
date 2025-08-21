from django.db import models
from django.utils import timezone


class Host(models.Model):
    """Model to store host/machine information"""
    hostname = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    os_info = models.CharField(max_length=255, null=True, blank=True)
    cpu_cores = models.IntegerField(null=True, blank=True)
    cpu_frequency = models.CharField(max_length=50, null=True, blank=True)
    total_memory_gb = models.FloatField(null=True, blank=True)
    disk_total_gb = models.FloatField(null=True, blank=True)
    disk_free_gb = models.FloatField(null=True, blank=True)
    disk_usage_percent = models.FloatField(null=True, blank=True)
    uptime = models.CharField(max_length=50, null=True, blank=True)
    first_seen = models.DateTimeField(default=timezone.now)
    last_seen = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.hostname
    
    class Meta:
        ordering = ['hostname']


class ProcessSnapshot(models.Model):
    """Model to store process snapshot data"""
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='snapshots')
    timestamp = models.DateTimeField(default=timezone.now)
    total_processes = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.host.hostname} - {self.timestamp}"
    
    class Meta:
        ordering = ['-timestamp']


class Process(models.Model):
    """Model to store individual process information"""
    snapshot = models.ForeignKey(ProcessSnapshot, on_delete=models.CASCADE, related_name='processes')
    pid = models.IntegerField()
    name = models.CharField(max_length=255)
    cmdline = models.TextField(null=True, blank=True)
    parent_pid = models.IntegerField(null=True, blank=True)
    cpu_percent = models.FloatField(default=0.0)
    memory_percent = models.FloatField(default=0.0)
    memory_rss = models.BigIntegerField(default=0)  # Resident Set Size in bytes
    memory_vms = models.BigIntegerField(default=0)  # Virtual Memory Size in bytes
    status = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=255, null=True, blank=True)
    create_time = models.FloatField(null=True, blank=True)  # Process creation time (timestamp)
    
    def __str__(self):
        return f"{self.name} (PID: {self.pid})"
    
    class Meta:
        ordering = ['pid']
        indexes = [
            models.Index(fields=['snapshot', 'parent_pid']),
            models.Index(fields=['snapshot', 'pid']),
        ]
    
    @property
    def children(self):
        """Get child processes"""
        return Process.objects.filter(snapshot=self.snapshot, parent_pid=self.pid)
    
    @property
    def parent(self):
        """Get parent process"""
        if self.parent_pid:
            try:
                return Process.objects.get(snapshot=self.snapshot, pid=self.parent_pid)
            except Process.DoesNotExist:
                return None
        return None
