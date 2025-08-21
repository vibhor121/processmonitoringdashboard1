#!/usr/bin/env python3
"""
Build script for Process Monitoring Agent

This script compiles the process_agent.py into a standalone executable
using PyInstaller.
"""

import os
import sys
import subprocess
import platform


def build_agent():
    """Build the process monitoring agent executable"""
    
    print("Building Process Monitoring Agent...")
    print(f"Platform: {platform.system()} {platform.machine()}")
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',                    # Create a single executable file
        '--console',                    # Keep console window
        '--name', 'ProcessMonitorAgent', # Executable name
        '--add-data', 'config.json;.' if platform.system() == 'Windows' else 'config.json:.',
        '--hidden-import', 'psutil',
        '--hidden-import', 'requests',
        '--hidden-import', 'socket',
        '--hidden-import', 'platform',
        '--hidden-import', 'json',
        '--distpath', 'dist',           # Output directory
        '--workpath', 'build',          # Temporary build directory
        '--specpath', '.',              # Spec file location
        'process_agent.py'              # Main script
    ]
    
    try:
        # Create default config if it doesn't exist
        if not os.path.exists('config.json'):
            print("Creating default configuration...")
            subprocess.run([sys.executable, 'process_agent.py', '--create-config'], check=True)
        
        # Run PyInstaller
        print("Running PyInstaller...")
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("Build completed successfully!")
        
        # Find the executable
        if platform.system() == 'Windows':
            exe_name = 'ProcessMonitorAgent.exe'
        else:
            exe_name = 'ProcessMonitorAgent'
        
        exe_path = os.path.join('dist', exe_name)
        
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path)
            print(f"Executable created: {exe_path}")
            print(f"Size: {size / 1024 / 1024:.1f} MB")
            
            # Make executable on Unix systems
            if platform.system() != 'Windows':
                os.chmod(exe_path, 0o755)
                print("Executable permissions set")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"Build error: {e}")
        return False


def clean_build():
    """Clean build artifacts"""
    import shutil
    
    print("Cleaning build artifacts...")
    
    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['ProcessMonitorAgent.spec']
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed directory: {dir_name}")
    
    for file_name in files_to_remove:
        if os.path.exists(file_name):
            os.remove(file_name)
            print(f"Removed file: {file_name}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Build Process Monitoring Agent')
    parser.add_argument('--clean', action='store_true', help='Clean build artifacts')
    
    args = parser.parse_args()
    
    if args.clean:
        clean_build()
        return
    
    success = build_agent()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main() 