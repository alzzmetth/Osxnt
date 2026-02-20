#!/usr/bin/env python3
# DarkWeb - Main Deployer

import os
import json
import shutil
from datetime import datetime
from .tor_manager import TorManager
from .server import DarkWebServer

class DarkWebDeployer:
    """
    Main class untuk deploy ke dark web
    """
    
    def __init__(self, config_file=None):
        self.config = self._load_config(config_file)
        self.tor = TorManager(self.config)
        self.server = DarkWebServer(self.config)
        self.status = 'stopped'
    
    def _load_config(self, config_file):
        """Load configuration"""
        default_config = {
            'port': 8080,
            'tor_port': 9050,
            'control_port': 9051,
            'site_name': 'default',
            'site_dir': 'darkweb_data/sites/default',
            'tor_dir': 'darkweb_data/tor',
            'auto_start': True
        }
        
        if config_file and os.path.exists(config_file):
            with open(config_file, 'r') as f:
                loaded = json.load(f)
                default_config.update(loaded)
        
        # Buat directories
        os.makedirs(default_config['site_dir'], exist_ok=True)
        os.makedirs(default_config['tor_dir'], exist_ok=True)
        
        return default_config
    
    def save_config(self, config_file='modules/darkweb/config.json'):
        """Save current config"""
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
        print(f"[+] Config saved to {config_file}")
    
    def update_config(self, key, value):
        """Update config value"""
        if key in self.config:
            old = self.config[key]
            self.config[key] = value
            print(f"[+] Config updated: {key} = {value} (was: {old})")
            self.save_config()
        else:
            print(f"[!] Unknown config key: {key}")
    
    def setup(self, auto=False, name=None):
        """Setup Tor and environment"""
        print("\n" + "="*50)
        print("🔧 DARKWEB SETUP")
        print("="*50)
        
        if name:
            self.config['site_name'] = name
            self.config['site_dir'] = f"darkweb_data/sites/{name.replace(' ', '_')}"
            os.makedirs(self.config['site_dir'], exist_ok=True)
        
        # Setup Tor
        if self.tor.setup():
            print("[+] Tor setup complete")
        else:
            print("[!] Tor setup failed")
            return False
        
        # Save config
        self.save_config()
        
        print(f"\n✅ Setup complete!")
        print(f"   Site name: {self.config['site_name']}")
        print(f"   Site dir: {self.config['site_dir']}")
        print(f"   Port: {self.config['port']}")
        print(f"\n   Next: osxnt.py -darkweb -start")
        
        return True
    
    def start(self):
        """Start dark web server"""
        print("\n" + "="*50)
        print("🌐 STARTING DARK WEB SERVER")
        print("="*50)
        
        # Start web server
        if not self.server.start():
            print("[!] Failed to start web server")
            return False
        
        # Start Tor & create hidden service
        if not self.tor.start_tor():
            print("[!] Failed to start Tor")
            self.server.stop()
            return False
        
        self.status = 'running'
        
        # Show info
        print("\n" + "="*50)
        print("✅ DARK WEB SERVER RUNNING")
        print("="*50)
        print(f"📍 Local address: http://localhost:{self.config['port']}")
        print(f"🌐 Onion address: {self.tor.onion_address}")
        print(f"📁 Site directory: {self.config['site_dir']}")
        print(f"\n   Put your HTML/CSS/JS files in the site directory")
        print(f"   Access your site via Tor Browser")
        print("="*50)
        
        return True
    
    def stop(self):
        """Stop all services"""
        print("\n[*] Stopping dark web server...")
        self.tor.stop_tor()
        self.server.stop()
        self.status = 'stopped'
        print("[+] Dark web server stopped")
    
    def status_info(self):
        """Get status info"""
        return {
            'status': self.status,
            'site_name': self.config['site_name'],
            'site_dir': self.config['site_dir'],
            'port': self.config['port'],
            'onion': self.tor.onion_address if self.tor.onion_address else 'Not started',
            'tor_running': self.tor.tor_process is not None
        }
    
    def deploy_files(self, source_dir):
        """Deploy files from source directory"""
        if not os.path.exists(source_dir):
            print(f"[!] Source directory not found: {source_dir}")
            return False
        
        # Copy semua file
        for item in os.listdir(source_dir):
            s = os.path.join(source_dir, item)
            d = os.path.join(self.config['site_dir'], item)
            
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        
        print(f"[+] Files deployed from {source_dir}")
        return True
