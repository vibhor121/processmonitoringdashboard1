from django.contrib import admin
from .models import Host, ProcessSnapshot, Process


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ['hostname', 'ip_address', 'os_info', 'first_seen', 'last_seen']
    list_filter = ['first_seen', 'last_seen']
    search_fields = ['hostname', 'ip_address']
    readonly_fields = ['first_seen']


@admin.register(ProcessSnapshot)
class ProcessSnapshotAdmin(admin.ModelAdmin):
    list_display = ['host', 'timestamp', 'total_processes']
    list_filter = ['timestamp', 'host']
    readonly_fields = ['timestamp']


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ['name', 'pid', 'parent_pid', 'cpu_percent', 'memory_percent', 'status', 'username']
    list_filter = ['status', 'username', 'snapshot__host']
    search_fields = ['name', 'pid', 'cmdline']
    readonly_fields = ['snapshot']
