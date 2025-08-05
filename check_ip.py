#!/usr/bin/env python3
"""
Simple script to check local IP address for Docker access
"""

import socket
import subprocess
import sys

def get_local_ip():
    """Get the local IP address that can be accessed from Docker"""
    try:
        # Method 1: Get IP from socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"Error getting IP via socket: {e}")
        return None

def get_all_ips():
    """Get all IP addresses using ifconfig"""
    try:
        result = subprocess.run(['ifconfig'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            ips = []
            for line in lines:
                if 'inet ' in line and '127.0.0.1' not in line:
                    parts = line.strip().split()
                    for part in parts:
                        if '.' in part and part.count('.') == 3:
                            ips.append(part)
            return ips
    except Exception as e:
        print(f"Error running ifconfig: {e}")
    return []

if __name__ == "__main__":
    print("🔍 Checking local IP addresses...")
    print("=" * 50)
    
    # Get primary local IP
    local_ip = get_local_ip()
    if local_ip:
        print(f"📍 Primary Local IP: {local_ip}")
        print(f"🌐 API URL for Docker: http://{local_ip}:5001/generate-image")
        print()
    
    # Get all IPs
    all_ips = get_all_ips()
    if all_ips:
        print("📋 All available IP addresses:")
        for ip in all_ips:
            print(f"   • {ip}")
        print()
    
    print("💡 For n8n Docker integration, try these URLs in order:")
    print("   1. http://host.docker.internal:5001/generate-image")
    if local_ip:
        print(f"   2. http://{local_ip}:5001/generate-image")
    print("   3. http://10.5.0.2:5001/generate-image (from your logs)")
    print()
    
    print("🧪 Test the connection:")
    if local_ip:
        print(f"   curl -X GET http://{local_ip}:5001/health") 