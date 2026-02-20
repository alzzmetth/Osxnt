#!/usr/bin/env python3
# DarkWeb - Tor Manager

import os
import subprocess
import time
import platform

class TorManager:
    """
    Manage Tor installation and hidden service
    """
    
    def __init__(self, config):
        self.config = config
        self.tor_process = None
        self.onion_address = None
    
    def setup(self):
        """Auto setup Tor"""
        print("[*] Setting up Tor...")
        
        # Deteksi OS
        system = platform.system().lower()
        
        if system == 'windows':
            return self._setup_windows()
        elif system == 'linux':
            return self._setup_linux()
        elif 'android' in platform.platform().lower():
            return self._setup_termux()
        elif system == 'darwin':
            return self._setup_macos()
        else:
            print("[!] OS not supported")
            return False
    
    def _setup_linux(self):
        """Setup Tor di Linux"""
        try:
            # Install Tor
            os.system("sudo apt update")
            os.system("sudo apt install tor -y")
            
            # Buat folder untuk hidden service
            os.makedirs(self.config['tor_dir'], exist_ok=True)
            os.makedirs(f"{self.config['tor_dir']}/hidden_service", exist_ok=True)
            
            return True
        except Exception as e:
            print(f"[!] Error: {e}")
            return False
    
    def _setup_termux(self):
        """Setup Tor di Termux (Android)"""
        try:
            # Install Tor
            os.system("pkg update")
            os.system("pkg install tor -y")
            
            # Buat folder
            os.makedirs(self.config['tor_dir'], exist_ok=True)
            os.makedirs(f"{self.config['tor_dir']}/hidden_service", exist_ok=True)
            
            return True
        except Exception as e:
            print(f"[!] Error: {e}")
            return False
    
    def _setup_windows(self):
        """Setup Tor di Windows (download)"""
        print("[!] Windows: Please install Tor manually from https://www.torproject.org")
        return False
    
    def _setup_macos(self):
        """Setup Tor di macOS"""
        try:
            os.system("brew install tor")
            return True
        except:
            print("[!] Install Homebrew first: https://brew.sh")
            return False
    
    def create_hidden_service(self):
        """Create hidden service configuration"""
        print("[*] Creating hidden service...")
        
        torrc_path = f"{self.config['tor_dir']}/torrc"
        
        # Buat torrc file
        with open(torrc_path, 'w') as f:
            f.write(f"""
# Tor Configuration
SOCKSPort {self.config['tor_port']}
ControlPort {self.config['control_port']}
CookieAuthentication 1

# Hidden Service
HiddenServiceDir {self.config['tor_dir']}/hidden_service
HiddenServicePort 80 127.0.0.1:{self.config['port']}

# Logs
Log notice file {self.config['tor_dir']}/tor.log
""")
        
        return torrc_path
    
    def start_tor(self):
        """Start Tor process"""
        print("[*] Starting Tor...")
        
        torrc = self.create_hidden_service()
        
        try:
            # Start Tor
            self.tor_process = subprocess.Popen(
                ['tor', '-f', torrc],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Tunggu Tor start
            time.sleep(5)
            
            # Baca onion address
            hostname_file = f"{self.config['tor_dir']}/hidden_service/hostname"
            
            for i in range(10):  # Coba 10x
                if os.path.exists(hostname_file):
                    with open(hostname_file, 'r') as f:
                        self.onion_address = f.read().strip()
                    print(f"[+] Hidden service created: {self.onion_address}")
                    return True
                time.sleep(2)
            
            print("[!] Failed to get onion address")
            return False
            
        except Exception as e:
            print(f"[!] Error starting Tor: {e}")
            return False
    
    def stop_tor(self):
        """Stop Tor process"""
        if self.tor_process:
            self.tor_process.terminate()
            print("[*] Tor stopped")
    
    def get_status(self):
        """Get Tor status"""
        return {
            'running': self.tor_process is not None,
            'onion': self.onion_address,
            'port': self.config['port']
        }
