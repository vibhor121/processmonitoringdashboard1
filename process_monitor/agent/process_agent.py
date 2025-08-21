#!/usr/bin/env python3
"""
Process Monitoring Agent

This agent collects process information from the local system and sends it
to the Django backend API. It can be compiled to a standalone executable
using PyInstaller.

Usage:
    python process_agent.py [--config config.json] [--once] [--verbose]
"""

import psutil
import socket
import platform
import time
import json
import requests
import argparse
import sys
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional


class ProcessAgent:
    def __init__(self, config_file: str = None):
        """Initialize the process monitoring agent"""
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.session = requests.Session()
        
        # Set API key header for authentication
        self.session.headers.update({
            'X-API-Key': self.config['api_key'],
            'Content-Type': 'application/json'
        })
        
        self.logger.info("Process Agent initialized")
        self.logger.info(f"Backend URL: {self.config['backend_url']}")
        self.logger.info(f"Collection interval: {self.config['interval']} seconds")
    
    def load_config(self, config_file: str = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'backend_url': 'http://localhost:8000/api/submit/',
            'api_key': 'process-monitor-api-key-2024',
            'interval': 30,
            'timeout': 10,
            'max_retries': 3,
            'retry_delay': 5,
            'include_cmdline': True,
            'exclude_processes': ['[kthreadd]', '[ksoftirqd]', '[migration]'],
            'log_level': 'INFO'
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    file_config = json.load(f)
                    default_config.update(file_config)
                    print(f"Loaded configuration from {config_file}")
            except Exception as e:
                print(f"Warning: Failed to load config file {config_file}: {e}")
                print("Using default configuration")
        
        return default_config
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_level = getattr(logging, self.config['log_level'].upper(), logging.INFO)
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('process_agent.log')
            ]
        )
        self.logger = logging.getLogger('ProcessAgent')
    
    def get_host_info(self) -> Dict[str, str]:
        """Collect host/system information"""
        try:
            hostname = socket.gethostname()
            
            # Try to get IP address
            try:
                # Connect to a remote address to determine local IP
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ip_address = s.getsockname()[0]
                s.close()
            except Exception:
                ip_address = '127.0.0.1'
            
            # Get OS information
            os_info = f"{platform.system()} {platform.release()} {platform.machine()}"
            
            # Get additional system information
            try:
                cpu_count = psutil.cpu_count()
                cpu_freq = psutil.cpu_freq()
                cpu_freq_str = f"{cpu_freq.current:.1f} MHz" if cpu_freq else "Unknown"
                
                memory = psutil.virtual_memory()
                total_memory_gb = round(memory.total / (1024**3), 1)
                
                # Get disk information for root partition
                try:
                    disk = psutil.disk_usage('/')
                    disk_total_gb = round(disk.total / (1024**3), 1)
                    disk_free_gb = round(disk.free / (1024**3), 1)
                    disk_usage_percent = round((disk.used / disk.total) * 100, 1)
                except Exception:
                    disk_total_gb = disk_free_gb = disk_usage_percent = 0
                
                # Get system uptime
                try:
                    uptime_seconds = time.time() - psutil.boot_time()
                    uptime_hours = int(uptime_seconds // 3600)
                    uptime_days = uptime_hours // 24
                    uptime_hours = uptime_hours % 24
                    if uptime_days > 0:
                        uptime_str = f"{uptime_days}d {uptime_hours}h"
                    else:
                        uptime_str = f"{uptime_hours}h"
                except Exception:
                    uptime_str = "Unknown"
                
                # Enhanced system info
                system_info = {
                    'hostname': hostname,
                    'ip_address': ip_address,
                    'os_info': os_info,
                    'cpu_cores': cpu_count,
                    'cpu_frequency': cpu_freq_str,
                    'total_memory_gb': total_memory_gb,
                    'disk_total_gb': disk_total_gb,
                    'disk_free_gb': disk_free_gb,
                    'disk_usage_percent': disk_usage_percent,
                    'uptime': uptime_str
                }
                
            except Exception as e:
                self.logger.warning(f"Failed to get detailed system info: {e}")
                # Fallback to basic info
                system_info = {
                    'hostname': hostname,
                    'ip_address': ip_address,
                    'os_info': os_info
                }
            
            return system_info
            
        except Exception as e:
            self.logger.error(f"Failed to get host info: {e}")
            return {
                'hostname': 'unknown',
                'ip_address': '127.0.0.1',
                'os_info': 'Unknown OS'
            }
    
    def get_process_info(self, proc: psutil.Process) -> Optional[Dict[str, Any]]:
        """Extract information from a single process"""
        try:
            # Get basic process info
            pinfo = proc.as_dict(attrs=[
                'pid', 'ppid', 'name', 'username', 'status',
                'create_time', 'memory_info', 'cpu_percent'
            ])
            
            # Skip excluded processes
            if pinfo['name'] in self.config['exclude_processes']:
                return None
            
            # Get command line if enabled
            cmdline = ''
            if self.config['include_cmdline']:
                try:
                    cmdline = ' '.join(proc.cmdline())
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    cmdline = pinfo['name']
            
            # Get memory information
            memory_info = pinfo.get('memory_info')
            
            # Calculate memory percentage
            try:
                memory_percent = proc.memory_percent()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                memory_percent = 0.0
            
            return {
                'pid': pinfo['pid'],
                'parent_pid': pinfo['ppid'],
                'name': pinfo['name'],
                'cmdline': cmdline,
                'username': pinfo.get('username', 'unknown'),
                'status': pinfo.get('status', 'unknown'),
                'cpu_percent': pinfo.get('cpu_percent', 0.0),
                'memory_percent': memory_percent,
                'memory_rss': memory_info.rss if memory_info else 0,
                'memory_vms': memory_info.vms if memory_info else 0,
                'create_time': pinfo.get('create_time', 0)
            }
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            # Process may have disappeared or we don't have access
            return None
        except Exception as e:
            self.logger.warning(f"Error getting info for process {proc.pid}: {e}")
            return None
    
    def collect_processes(self) -> List[Dict[str, Any]]:
        """Collect information about all running processes"""
        processes = []
        
        try:
            # Get all processes
            all_procs = list(psutil.process_iter())
            
            # First pass: collect CPU percentages (requires some time)
            self.logger.debug("Collecting CPU usage data...")
            for proc in all_procs:
                try:
                    proc.cpu_percent()  # First call returns 0.0, this primes it
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Wait a moment for CPU calculation
            time.sleep(0.1)
            
            # Second pass: collect all process information
            self.logger.debug(f"Collecting information for {len(all_procs)} processes...")
            
            for proc in all_procs:
                proc_info = self.get_process_info(proc)
                if proc_info:
                    processes.append(proc_info)
            
            self.logger.info(f"Collected information for {len(processes)} processes")
            return processes
            
        except Exception as e:
            self.logger.error(f"Failed to collect processes: {e}")
            return []
    
    def send_data(self, data: Dict[str, Any]) -> bool:
        """Send collected data to the backend API"""
        for attempt in range(self.config['max_retries']):
            try:
                self.logger.debug(f"Sending data to {self.config['backend_url']} (attempt {attempt + 1})")
                
                response = self.session.post(
                    self.config['backend_url'],
                    json=data,
                    timeout=self.config['timeout']
                )
                
                if response.status_code == 201:
                    result = response.json()
                    self.logger.info(
                        f"Successfully sent data - Host: {result.get('host')}, "
                        f"Processes: {result.get('processes_created')}, "
                        f"Snapshot ID: {result.get('snapshot_id')}"
                    )
                    return True
                else:
                    self.logger.warning(
                        f"Server returned status {response.status_code}: {response.text}"
                    )
                    
            except requests.exceptions.ConnectionError as e:
                self.logger.warning(f"Connection error (attempt {attempt + 1}): {e}")
            except requests.exceptions.Timeout as e:
                self.logger.warning(f"Timeout error (attempt {attempt + 1}): {e}")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error (attempt {attempt + 1}): {e}")
            except Exception as e:
                self.logger.error(f"Unexpected error (attempt {attempt + 1}): {e}")
            
            if attempt < self.config['max_retries'] - 1:
                self.logger.info(f"Retrying in {self.config['retry_delay']} seconds...")
                time.sleep(self.config['retry_delay'])
        
        self.logger.error(f"Failed to send data after {self.config['max_retries']} attempts")
        return False
    
    def run_once(self) -> bool:
        """Run data collection and sending once"""
        self.logger.info("Starting data collection...")
        
        # Collect host information
        host_info = self.get_host_info()
        self.logger.info(f"Host: {host_info['hostname']} ({host_info['ip_address']})")
        
        # Collect process information
        processes = self.collect_processes()
        
        if not processes:
            self.logger.warning("No process data collected")
            return False
        
        # Prepare data for sending
        data = {
            **host_info,
            'processes': processes
        }
        
        # Send data to backend
        return self.send_data(data)
    
    def run_continuous(self):
        """Run the agent continuously with specified interval"""
        self.logger.info("Starting continuous monitoring...")
        
        try:
            while True:
                start_time = time.time()
                
                success = self.run_once()
                
                elapsed = time.time() - start_time
                self.logger.info(f"Collection cycle completed in {elapsed:.2f} seconds")
                
                if not success:
                    self.logger.warning("Data collection failed, continuing anyway...")
                
                # Wait for the specified interval
                sleep_time = max(0, self.config['interval'] - elapsed)
                if sleep_time > 0:
                    self.logger.debug(f"Sleeping for {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal, shutting down...")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
            raise


def create_default_config():
    """Create a default configuration file"""
    config = {
        "backend_url": "http://localhost:8000/api/submit/",
        "api_key": "process-monitor-api-key-2024",
        "interval": 30,
        "timeout": 10,
        "max_retries": 3,
        "retry_delay": 5,
        "include_cmdline": True,
        "exclude_processes": ["[kthreadd]", "[ksoftirqd]", "[migration]"],
        "log_level": "INFO"
    }
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    
    print("Created default configuration file: config.json")
    print("Please edit the backend_url and api_key as needed.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Process Monitoring Agent')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    parser.add_argument('--create-config', action='store_true', help='Create default config file')
    
    args = parser.parse_args()
    
    if args.create_config:
        create_default_config()
        return
    
    try:
        # Create and run the agent
        agent = ProcessAgent(args.config)
        
        if args.verbose:
            agent.logger.setLevel(logging.DEBUG)
        
        if args.once:
            success = agent.run_once()
            sys.exit(0 if success else 1)
        else:
            agent.run_continuous()
            
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 