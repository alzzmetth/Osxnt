#!/usr/bin/env python3
# OSXNT - Tor Proxy Module
# Developed by alzzdevmaret

import os
import sys
import subprocess
import time
import requests
import socket
import socks
from lib.verbose import Verbose

class TorProxy:
    """
    Tor Proxy Manager untuk OSXNT
    Mengelola koneksi melalui Tor network
    """
    
    def __init__(self, tor_port=9050, control_port=9051, verbose=False):
        """
        Inisialisasi Tor Proxy
        
        Args:
            tor_port (int): Port SOCKS Tor (default: 9050)
            control_port (int): Port kontrol Tor (default: 9051)
            verbose (bool): Mode verbose
        """
        self.tor_port = tor_port
        self.control_port = control_port
        self.v = Verbose(verbose)
        self.session = None
        self.tor_process = None
        self.is_running = False
        
        # Proxy URL format
        self.proxy_url = f"socks5://127.0.0.1:{tor_port}"
        self.proxies = {
            'http': self.proxy_url,
            'https': self.proxy_url
        }
        
        self.v.log(f"Tor Proxy initialized on port {tor_port}")
    
    def check_tor_installed(self):
        """Cek apakah Tor terinstall di sistem"""
        try:
            subprocess.run(['tor', '--version'], 
                         capture_output=True, 
                         check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def check_tor_running(self):
        """Cek apakah Tor sudah berjalan"""
        try:
            # Cek koneksi ke SOCKS port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', self.tor_port))
            sock.close()
            
            if result == 0:
                # Cek dengan request test
                test_session = requests.Session()
                test_session.proxies = self.proxies
                test_session.timeout = 5
                
                try:
                    r = test_session.get('https://check.torproject.org/', timeout=5)
                    if 'Congratulations' in r.text:
                        self.v.log("Tor is running and working")
                        return True
                except:
                    pass
            
            return False
        except Exception as e:
            self.v.error(f"Error checking Tor: {e}")
            return False
    
    def start_tor(self, wait_time=5):
        """
        Menjalankan Tor service
        
        Args:
            wait_time (int): Waktu tunggu setelah start (detik)
        
        Returns:
            bool: True jika berhasil
        """
        if not self.check_tor_installed():
            self.v.error("Tor tidak terinstall. Install dengan: pkg install tor")
            return False
        
        if self.check_tor_running():
            self.v.log("Tor already running")
            self.is_running = True
            return True
        
        self.v.log("Starting Tor service...")
        
        try:
            # Coba jalankan Tor sebagai background process
            if sys.platform == 'linux' or sys.platform == 'android':
                # Untuk Termux/Linux
                self.tor_process = subprocess.Popen(
                    ['tor'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            elif sys.platform == 'win32':
                # Untuk Windows
                self.tor_process = subprocess.Popen(
                    ['tor'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                # Untuk macOS
                self.tor_process = subprocess.Popen(
                    ['tor'],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            # Tunggu Tor start
            self.v.log(f"Waiting {wait_time} seconds for Tor to start...")
            time.sleep(wait_time)
            
            if self.check_tor_running():
                self.is_running = True
                self.v.log("✅ Tor started successfully")
                return True
            else:
                self.v.error("Failed to start Tor")
                return False
                
        except Exception as e:
            self.v.error(f"Error starting Tor: {e}")
            return False
    
    def stop_tor(self):
        """Menghentikan Tor service"""
        if self.tor_process:
            self.tor_process.terminate()
            self.tor_process.wait()
            self.is_running = False
            self.v.log("Tor stopped")
            return True
        return False
    
    def renew_identity(self):
        """
        Renew Tor identity (ganti IP)
        
        Returns:
            bool: True jika berhasil
        """
        if not self.is_running:
            self.v.error("Tor not running")
            return False
        
        try:
            # Konek ke Tor control port
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('127.0.0.1', self.control_port))
            
            # Kirim perintah NEWNYM
            s.send(b'AUTHENTICATE ""\r\n')
            time.sleep(0.5)
            s.send(b'SIGNAL NEWNYM\r\n')
            time.sleep(0.5)
            s.close()
            
            self.v.log("🔄 Tor identity renewed - New IP requested")
            time.sleep(2)  # Tunggu identity change
            return True
            
        except Exception as e:
            self.v.error(f"Failed to renew identity: {e}")
            return False
    
    def get_current_ip(self):
        """
        Dapatkan IP saat ini melalui Tor
        
        Returns:
            str: IP address atau None
        """
        if not self.is_running:
            self.v.error("Tor not running")
            return None
        
        try:
            session = self.get_session()
            r = session.get('https://api.ipify.org?format=json', timeout=10)
            ip = r.json().get('ip')
            self.v.log(f"Current Tor IP: {ip}")
            return ip
        except Exception as e:
            self.v.error(f"Failed to get IP: {e}")
            return None
    
    def get_session(self):
        """
        Dapatkan requests session dengan Tor proxy
        
        Returns:
            requests.Session: Session dengan Tor proxy
        """
        if not self.is_running:
            self.v.error("Tor not running, starting...")
            self.start_tor()
        
        session = requests.Session()
        session.proxies = self.proxies
        session.timeout = 15
        return session
    
    def test_connection(self):
        """Test koneksi Tor"""
        try:
            session = self.get_session()
            r = session.get('https://check.torproject.org/', timeout=10)
            
            if 'Congratulations' in r.text:
                self.v.log("✅ Tor connection successful")
                return True
            else:
                self.v.log("❌ Not using Tor")
                return False
        except Exception as e:
            self.v.error(f"Connection test failed: {e}")
            return False
    
    def get_status(self):
        """Dapatkan status Tor"""
        status = {
            'running': self.is_running,
            'port': self.tor_port,
            'control_port': self.control_port,
            'installed': self.check_tor_installed(),
            'ip': None
        }
        
        if self.is_running:
            status['ip'] = self.get_current_ip()
        
        return status
    
    def __enter__(self):
        """Context manager entry"""
        self.start_tor()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_tor()


# ========== CONTOH PENGGUNAAN ==========

if __name__ == "__main__":
    # Test Tor Proxy
    tor = TorProxy(verbose=True)
    
    # Start Tor
    if tor.start_tor():
        # Test koneksi
        tor.test_connection()
        
        # Dapatkan IP
        ip = tor.get_current_ip()
        print(f"Current IP: {ip}")
        
        # Renew identity
        tor.renew_identity()
        
        # Dapatkan IP baru
        new_ip = tor.get_current_ip()
        print(f"New IP: {new_ip}")
        
        # Stop Tor
        tor.stop_tor()
    
    # Atau pakai context manager
    with TorProxy(verbose=True) as tor:
        tor.test_connection()
