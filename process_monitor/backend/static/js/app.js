class ProcessMonitor {
    constructor() {
        this.currentHost = null;
        this.processData = null;
        this.autoRefreshInterval = null;
        this.searchTerm = '';
        this.showSystemProcesses = true;
        this.showUserProcesses = true;
        
        this.initializeElements();
        this.bindEvents();
        this.loadHosts();
    }
    
    initializeElements() {
        this.hostSelect = document.getElementById('hostSelect');
        this.refreshBtn = document.getElementById('refreshBtn');
        this.autoRefreshCheckbox = document.getElementById('autoRefresh');
        this.searchInput = document.getElementById('searchInput');
        this.showSystemCheckbox = document.getElementById('showSystemProcesses');
        this.showUserCheckbox = document.getElementById('showUserProcesses');
        this.expandAllBtn = document.getElementById('expandAllBtn');
        this.collapseAllBtn = document.getElementById('collapseAllBtn');
        
        this.hostDetails = document.getElementById('hostDetails');
        this.processStats = document.getElementById('processStats');
        this.processTree = document.getElementById('processTree');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.errorMessage = document.getElementById('errorMessage');
        this.errorText = document.getElementById('errorText');
    }
    
    bindEvents() {
        this.hostSelect.addEventListener('change', (e) => {
            this.selectHost(e.target.value);
        });
        
        this.refreshBtn.addEventListener('click', () => {
            this.refreshData();
        });
        
        this.autoRefreshCheckbox.addEventListener('change', (e) => {
            this.toggleAutoRefresh(e.target.checked);
        });
        
        this.searchInput.addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.filterAndRenderProcesses();
        });
        
        this.showSystemCheckbox.addEventListener('change', (e) => {
            this.showSystemProcesses = e.target.checked;
            this.filterAndRenderProcesses();
        });
        
        this.showUserCheckbox.addEventListener('change', (e) => {
            this.showUserProcesses = e.target.checked;
            this.filterAndRenderProcesses();
        });
        
        this.expandAllBtn.addEventListener('click', () => {
            this.expandAllProcesses();
        });
        
        this.collapseAllBtn.addEventListener('click', () => {
            this.collapseAllProcesses();
        });
    }
    
    async loadHosts() {
        try {
            const response = await fetch('/api/hosts/');
            const hosts = await response.json();
            
            this.hostSelect.innerHTML = '<option value="">Select a host...</option>';
            hosts.forEach(host => {
                const option = document.createElement('option');
                option.value = host.hostname;
                option.textContent = `${host.hostname} (${host.os_info || 'Unknown OS'})`;
                this.hostSelect.appendChild(option);
            });
            
        } catch (error) {
            console.error('Failed to load hosts:', error);
            this.showError('Failed to load hosts');
        }
    }
    
    async selectHost(hostname) {
        if (!hostname) {
            this.currentHost = null;
            this.clearData();
            return;
        }
        
        this.currentHost = hostname;
        await this.loadProcessData();
        this.updateAutoRefresh();
    }
    
    async loadProcessData() {
        if (!this.currentHost) return;
        
        this.showLoading();
        
        try {
            const response = await fetch(`/api/hosts/${this.currentHost}/processes/`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.processData = data;
            this.updateHostDetails(data);
            this.updateProcessStats(data);
            this.renderProcessTree(data.process_tree);
            
            // Load system resources
            await this.loadSystemResources();
            
            this.hideLoading();
            
        } catch (error) {
            console.error('Failed to load process data:', error);
            this.showError(`Failed to load process data: ${error.message}`);
            this.hideLoading();
        }
    }
    
    async loadSystemResources() {
        if (!this.currentHost) return;
        
        try {
            const response = await fetch(`/api/hosts/${this.currentHost}/resources/`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.updateSystemResources(data.system_resources);
            
        } catch (error) {
            console.error('Failed to load system resources:', error);
            // Don't show error for system resources, just log it
        }
    }
    
    updateSystemResources(resources) {
        if (!resources) return;
        
        // Update CPU usage
        const cpuElement = document.getElementById('totalCpuUsage');
        if (cpuElement) {
            cpuElement.textContent = `${resources.total_cpu_percent}%`;
        }
        
        // Update memory usage
        const memoryElement = document.getElementById('totalMemoryUsage');
        if (memoryElement) {
            const totalMemoryMB = Math.round(resources.total_memory_rss / (1024 * 1024));
            memoryElement.textContent = `${totalMemoryMB} MB`;
        }
        
        // Update top CPU process
        const topCpuElement = document.getElementById('topCpuProcess');
        if (topCpuElement && resources.top_cpu_processes.length > 0) {
            const topProcess = resources.top_cpu_processes[0];
            topCpuElement.textContent = `${topProcess.name} (${topProcess.cpu_percent}%)`;
        }
        
        // Update top memory process
        const topMemoryElement = document.getElementById('topMemoryProcess');
        if (topMemoryElement && resources.top_memory_processes.length > 0) {
            const topProcess = resources.top_memory_processes[0];
            const memoryMB = Math.round(topProcess.memory_rss / (1024 * 1024));
            topMemoryElement.textContent = `${topProcess.name} (${memoryMB} MB)`;
        }
    }
    
    updateSystemSpecs(hostInfo) {
        if (!hostInfo) return;
        
        // Update CPU cores
        const cpuCoresElement = document.getElementById('cpuCores');
        if (cpuCoresElement) {
            cpuCoresElement.textContent = hostInfo.cpu_cores || 'Unknown';
        }
        
        // Update CPU frequency
        const cpuFreqElement = document.getElementById('cpuFrequency');
        if (cpuFreqElement) {
            cpuFreqElement.textContent = hostInfo.cpu_frequency || 'Unknown';
        }
        
        // Update total memory
        const totalMemoryElement = document.getElementById('totalMemory');
        if (totalMemoryElement) {
            totalMemoryElement.textContent = hostInfo.total_memory_gb ? `${hostInfo.total_memory_gb} GB` : 'Unknown';
        }
        
        // Update disk usage
        const diskUsageElement = document.getElementById('diskUsage');
        if (diskUsageElement) {
            if (hostInfo.disk_usage_percent && hostInfo.disk_total_gb) {
                const freeGB = hostInfo.disk_free_gb || 0;
                diskUsageElement.textContent = `${hostInfo.disk_usage_percent}% (${freeGB} GB free)`;
            } else {
                diskUsageElement.textContent = 'Unknown';
            }
        }
        
        // Update uptime
        const uptimeElement = document.getElementById('uptime');
        if (uptimeElement) {
            uptimeElement.textContent = hostInfo.uptime || 'Unknown';
        }
    }
    
    async updateHostDetails(data) {
        // Get additional host information from the hosts API
        try {
            const hostResponse = await fetch('/api/hosts/');
            const hosts = await hostResponse.json();
            const hostInfo = hosts.find(h => h.hostname === data.hostname);
            
            if (hostInfo) {
                this.hostDetails.innerHTML = `
                    <div class="host-detail-item">
                        <i class="fas fa-server"></i>
                        <div class="detail-content">
                            <span class="detail-label">Hostname:</span>
                            <span class="detail-value">${hostInfo.hostname}</span>
                        </div>
                    </div>
                    <div class="host-detail-item">
                        <i class="fas fa-network-wired"></i>
                        <div class="detail-content">
                            <span class="detail-label">IP Address:</span>
                            <span class="detail-value">${hostInfo.ip_address || 'Unknown'}</span>
                        </div>
                    </div>
                    <div class="host-detail-item">
                        <i class="fas fa-desktop"></i>
                        <div class="detail-content">
                            <span class="detail-label">Operating System:</span>
                            <span class="detail-value">${hostInfo.os_info || 'Unknown OS'}</span>
                        </div>
                    </div>
                    <div class="host-detail-item">
                        <i class="fas fa-clock"></i>
                        <div class="detail-content">
                            <span class="detail-label">First Seen:</span>
                            <span class="detail-value">${this.formatTimestamp(hostInfo.first_seen)}</span>
                        </div>
                    </div>
                    <div class="host-detail-item">
                        <i class="fas fa-sync-alt"></i>
                        <div class="detail-content">
                            <span class="detail-label">Last Seen:</span>
                            <span class="detail-value">${this.formatTimestamp(hostInfo.last_seen)}</span>
                        </div>
                    </div>
                    <div class="host-detail-item">
                        <i class="fas fa-tasks"></i>
                        <div class="detail-content">
                            <span class="detail-label">Total Processes:</span>
                            <span class="detail-value">${data.total_processes}</span>
                        </div>
                    </div>
                    <div class="host-detail-item">
                        <i class="fas fa-calendar-alt"></i>
                        <div class="detail-content">
                            <span class="detail-label">Last Update:</span>
                            <span class="detail-value">${this.formatTimestamp(data.timestamp)}</span>
                        </div>
                    </div>
                `;
                
                // Update system specifications
                this.updateSystemSpecs(hostInfo);
            } else {
                // Fallback to basic info if host details not found
                this.hostDetails.innerHTML = `
                    <div class="host-detail-item">
                        <i class="fas fa-server"></i>
                        <div class="detail-content">
                            <span class="detail-label">Hostname:</span>
                            <span class="detail-value">${data.hostname}</span>
                        </div>
                    </div>
                    <div class="host-detail-item">
                        <i class="fas fa-tasks"></i>
                        <div class="detail-content">
                            <span class="detail-label">Total Processes:</span>
                            <span class="detail-value">${data.total_processes}</span>
                        </div>
                    </div>
                    <div class="host-detail-item">
                        <i class="fas fa-calendar-alt"></i>
                        <div class="detail-content">
                            <span class="detail-label">Last Update:</span>
                            <span class="detail-value">${this.formatTimestamp(data.timestamp)}</span>
                        </div>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Failed to load host details:', error);
            // Fallback to basic info
            this.hostDetails.innerHTML = `
                <div class="host-detail-item">
                    <i class="fas fa-server"></i>
                    <div class="detail-content">
                        <span class="detail-label">Hostname:</span>
                        <span class="detail-value">${data.hostname}</span>
                    </div>
                </div>
                <div class="host-detail-item">
                    <i class="fas fa-tasks"></i>
                    <div class="detail-content">
                        <span class="detail-label">Total Processes:</span>
                        <span class="detail-value">${data.total_processes}</span>
                    </div>
                </div>
                <div class="host-detail-item">
                    <i class="fas fa-calendar-alt"></i>
                    <div class="detail-content">
                        <span class="detail-label">Last Update:</span>
                        <span class="detail-value">${this.formatTimestamp(data.timestamp)}</span>
                    </div>
                </div>
            `;
        }
    }
    
    updateProcessStats(data) {
        const processes = this.flattenProcessTree(data.process_tree);
        const statusCounts = this.countProcessesByStatus(processes);
        
        document.getElementById('totalProcesses').textContent = data.total_processes;
        document.getElementById('runningProcesses').textContent = statusCounts.running || 0;
        document.getElementById('sleepingProcesses').textContent = statusCounts.sleeping || 0;
        document.getElementById('lastUpdate').textContent = this.formatTimestamp(data.timestamp);
    }
    
    renderProcessTree(processes) {
        if (!processes || processes.length === 0) {
            this.processTree.innerHTML = `
                <div class="no-data">
                    <i class="fas fa-database"></i>
                    <p>No processes found</p>
                    <p class="no-data-subtitle">The selected host has no process data</p>
                </div>
            `;
            return;
        }
        
        const filteredProcesses = this.filterProcesses(processes);
        this.processTree.innerHTML = this.renderProcessItems(filteredProcesses);
        this.bindProcessEvents();
    }
    
    renderProcessItems(processes, level = 0) {
        return processes.map(process => {
            const hasChildren = process.children && process.children.length > 0;
            const indent = level * 20;
            
            return `
                <div class="process-item" style="margin-left: ${indent}px" data-pid="${process.pid}">
                    <div class="process-header-item" ${hasChildren ? 'data-toggle="true"' : ''}>
                        ${hasChildren ? '<i class="fas fa-caret-right process-toggle"></i>' : '<div style="width: 16px;"></div>'}
                        <div class="process-info">
                            <div class="process-details">
                                <div class="process-name">${this.escapeHtml(process.name)}</div>
                                <div class="process-pid">PID: ${process.pid}</div>
                                <div class="process-cmd" title="${this.escapeHtml(process.cmdline || '')}">
                                    ${this.escapeHtml(process.cmdline || 'No command line')}
                                </div>
                            </div>
                            <div class="process-metrics">
                                <div class="metric-item">
                                    <span class="metric-label">CPU:</span>
                                    <span class="metric-value">${process.cpu_percent?.toFixed(1) || '0.0'}%</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">Memory:</span>
                                    <span class="metric-value">${process.memory_percent?.toFixed(1) || '0.0'}%</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">Status:</span>
                                    <span class="metric-value">${process.status || 'Unknown'}</span>
                                </div>
                            </div>
                            <div class="process-user">
                                <div class="metric-item">
                                    <span class="metric-label">User:</span>
                                    <span class="metric-value">${process.username || 'Unknown'}</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">RSS:</span>
                                    <span class="metric-value">${this.formatBytes(process.memory_rss || 0)}</span>
                                </div>
                                <div class="metric-item">
                                    <span class="metric-label">VMS:</span>
                                    <span class="metric-value">${this.formatBytes(process.memory_vms || 0)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    ${hasChildren ? `
                        <div class="process-children">
                            ${this.renderProcessItems(process.children, level + 1)}
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
    }
    
    bindProcessEvents() {
        document.querySelectorAll('[data-toggle="true"]').forEach(header => {
            header.addEventListener('click', (e) => {
                e.stopPropagation();
                this.toggleProcess(header);
            });
        });
    }
    
    toggleProcess(header) {
        const processItem = header.closest('.process-item');
        const children = processItem.querySelector('.process-children');
        const toggle = header.querySelector('.process-toggle');
        
        if (children) {
            const isExpanded = children.classList.contains('expanded');
            
            if (isExpanded) {
                children.classList.remove('expanded');
                toggle.classList.remove('expanded');
            } else {
                children.classList.add('expanded');
                toggle.classList.add('expanded');
            }
        }
    }
    
    expandAllProcesses() {
        document.querySelectorAll('.process-children').forEach(children => {
            children.classList.add('expanded');
        });
        document.querySelectorAll('.process-toggle').forEach(toggle => {
            toggle.classList.add('expanded');
        });
    }
    
    collapseAllProcesses() {
        document.querySelectorAll('.process-children').forEach(children => {
            children.classList.remove('expanded');
        });
        document.querySelectorAll('.process-toggle').forEach(toggle => {
            toggle.classList.remove('expanded');
        });
    }
    
    filterProcesses(processes) {
        return processes.filter(process => {
            // Search filter
            if (this.searchTerm) {
                const searchMatch = 
                    process.name.toLowerCase().includes(this.searchTerm) ||
                    process.pid.toString().includes(this.searchTerm) ||
                    (process.cmdline && process.cmdline.toLowerCase().includes(this.searchTerm)) ||
                    (process.username && process.username.toLowerCase().includes(this.searchTerm));
                
                if (!searchMatch) {
                    // Check if any children match
                    const childrenMatch = process.children && 
                        this.filterProcesses(process.children).length > 0;
                    if (!childrenMatch) return false;
                }
            }
            
            // Type filters
            const isSystemProcess = this.isSystemProcess(process);
            if (isSystemProcess && !this.showSystemProcesses) return false;
            if (!isSystemProcess && !this.showUserProcesses) return false;
            
            // Filter children recursively
            if (process.children) {
                process.children = this.filterProcesses(process.children);
            }
            
            return true;
        });
    }
    
    filterAndRenderProcesses() {
        if (this.processData && this.processData.process_tree) {
            this.renderProcessTree(this.processData.process_tree);
        }
    }
    
    isSystemProcess(process) {
        const systemUsers = ['root', 'system', 'daemon', 'bin', 'sys', 'mail', 'www-data', 'nobody'];
        return systemUsers.includes(process.username?.toLowerCase()) || 
               process.username === null || 
               process.username === '';
    }
    
    flattenProcessTree(processes) {
        let flat = [];
        processes.forEach(process => {
            flat.push(process);
            if (process.children) {
                flat = flat.concat(this.flattenProcessTree(process.children));
            }
        });
        return flat;
    }
    
    countProcessesByStatus(processes) {
        const counts = {};
        processes.forEach(process => {
            const status = (process.status || 'unknown').toLowerCase();
            counts[status] = (counts[status] || 0) + 1;
        });
        return counts;
    }
    
    formatTimestamp(timestamp) {
        return new Date(timestamp).toLocaleString();
    }
    
    formatBytes(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, (m) => map[m]);
    }
    
    showLoading() {
        this.loadingIndicator.style.display = 'block';
        this.errorMessage.style.display = 'none';
        this.processTree.style.display = 'none';
    }
    
    hideLoading() {
        this.loadingIndicator.style.display = 'none';
        this.processTree.style.display = 'block';
    }
    
    showError(message) {
        this.errorText.textContent = message;
        this.errorMessage.style.display = 'block';
        this.loadingIndicator.style.display = 'none';
        this.processTree.style.display = 'none';
    }
    
    clearData() {
        this.processData = null;
        this.hostDetails.innerHTML = '<p>No host selected</p>';
        
        document.getElementById('totalProcesses').textContent = '-';
        document.getElementById('runningProcesses').textContent = '-';
        document.getElementById('sleepingProcesses').textContent = '-';
        document.getElementById('lastUpdate').textContent = '-';
        
        // Clear system resources
        document.getElementById('totalCpuUsage').textContent = '-';
        document.getElementById('totalMemoryUsage').textContent = '-';
        document.getElementById('topCpuProcess').textContent = '-';
        document.getElementById('topMemoryProcess').textContent = '-';
        
        // Clear system specifications
        document.getElementById('cpuCores').textContent = '-';
        document.getElementById('cpuFrequency').textContent = '-';
        document.getElementById('totalMemory').textContent = '-';
        document.getElementById('diskUsage').textContent = '-';
        document.getElementById('uptime').textContent = '-';
        
        this.processTree.innerHTML = `
            <div class="no-data">
                <i class="fas fa-database"></i>
                <p>No process data available</p>
                <p class="no-data-subtitle">Select a host to view process information</p>
            </div>
        `;
        
        this.errorMessage.style.display = 'none';
        this.loadingIndicator.style.display = 'none';
    }
    
    refreshData() {
        if (this.currentHost) {
            this.loadProcessData();
        } else {
            this.loadHosts();
        }
    }
    
    toggleAutoRefresh(enabled) {
        if (enabled) {
            this.autoRefreshInterval = setInterval(() => {
                if (this.currentHost) {
                    this.loadProcessData();
                }
            }, 30000); // 30 seconds
        } else {
            if (this.autoRefreshInterval) {
                clearInterval(this.autoRefreshInterval);
                this.autoRefreshInterval = null;
            }
        }
    }
    
    updateAutoRefresh() {
        if (this.autoRefreshCheckbox.checked) {
            this.toggleAutoRefresh(false);
            this.toggleAutoRefresh(true);
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ProcessMonitor();
}); 