#!/usr/bin/env python3
# OSXNT - DarkWeb UI Module
# Antarmuka sederhana untuk menampilkan informasi site

import os
import time
from datetime import datetime
from .config import Config
from .monitor import DarkWebMonitor

class DarkWebUI:
    """UI sederhana untuk darkweb services"""
    
    def __init__(self, config=None, monitor=None):
        self.config = config or Config()
        self.monitor = monitor or DarkWebMonitor(self.config)
    
    def show_dashboard(self):
        """Tampilkan dashboard semua service"""
        services = self.config.list_services()
        
        print("\n" + "="*60)
        print("🌑 DARKWEB SERVICE DASHBOARD")
        print("="*60)
        
        if not services:
            print("No active services.")
            return
        
        for name, svc in services.items():
            self.show_service_summary(name, svc)
            print("-"*40)
    
    def show_service_summary(self, name, service_config):
        """Tampilkan ringkasan satu service"""
        # Ambil informasi dari config
        port = service_config.get('port', self.config.get('default_port'))
        onion = service_config.get('onion', 'Not yet generated')
        status = service_config.get('status', 'stopped')
        path = service_config.get('path', '')
        auto_monitor = service_config.get('auto_monitor', 'yes')
        
        # Status color
        if status == 'running':
            status_display = "🟢 ACTIVE"
        elif status == 'stopped':
            status_display = "🔴 STOPPED"
        else:
            status_display = "⚪ UNKNOWN"
        
        # Tampilkan
        print(f"\n📌 Site: {name}")
        print(f"   Version      : {service_config.get('version', '1.0')}")
        print(f"   File Path    : {path or 'Not set'}")
        print(f"   Hidden Service: {onion}")
        print(f"   Auto Monitor : {auto_monitor}")
        print(f"   Status       : {status_display}")
        print(f"   Port         : {port}")
        
        # Jika running, tampilkan statistik singkat dari monitor
        if status == 'running' and hasattr(self.monitor, 'get_status_summary'):
            stats = self.monitor.get_status_summary()
            print(f"   Uptime       : {stats.get('uptime', 'N/A')}")
            print(f"   Requests     : {stats.get('total_requests', 0)}")
            print(f"   Visitors     : {stats.get('unique_visitors', 0)}")
    
    def interactive_menu(self):
        """Menu interaktif untuk user"""
        while True:
            print("\n" + "="*60)
            print("🌑 DARKWEB CONTROL PANEL")
            print("="*60)
            print("1. List all services")
            print("2. Show service details")
            print("3. Start service")
            print("4. Stop service")
            print("5. Restart service")
            print("6. View monitor stats")
            print("7. Generate report")
            print("8. Reset stats")
            print("9. Exit")
            
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.show_dashboard()
            elif choice == '2':
                name = input("Service name: ").strip()
                svc = self.config.get_service(name)
                if svc:
                    self.show_service_summary(name, svc)
                else:
                    print("Service not found.")
            elif choice == '3':
                name = input("Service name: ").strip()
                # Panggil fungsi start dari deployer (perlu diintegrasi)
                print(f"Starting {name}... (not implemented yet)")
            elif choice == '4':
                name = input("Service name: ").strip()
                print(f"Stopping {name}...")
            elif choice == '5':
                name = input("Service name: ").strip()
                print(f"Restarting {name}...")
            elif choice == '6':
                name = input("Service name (or 'all'): ").strip()
                if name == 'all':
                    print(self.monitor.generate_report())
                else:
                    # Tampilkan stats untuk service tertentu
                    print("Stats for", name)
            elif choice == '7':
                print(self.monitor.generate_report())
            elif choice == '8':
                confirm = input("Reset all stats? (y/N): ").strip().lower()
                if confirm == 'y':
                    self.monitor.reset_stats()
                    print("Stats reset.")
            elif choice == '9':
                break
    
    def quick_status(self):
        """Tampilan status cepat (untuk command line)"""
        services = self.config.list_services()
        print("\n" + "="*60)
        print("🌑 DARKWEB STATUS")
        print("="*60)
        for name, svc in services.items():
            onion = svc.get('onion', '?')
            status = svc.get('status', '?')
            port = svc.get('port', '?')
            print(f"{name:<15} | {onion:<22} | {status:<8} | port {port}")
        print("="*60)
