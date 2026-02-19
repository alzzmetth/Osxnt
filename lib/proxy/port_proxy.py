#!/usr/bin/env python3
# OSXNT - Port Proxy Module
# Developed by alzzdevmaret

import random
import requests
from lib.verbose import Verbose

class PortProxy:
    """
    Port Proxy Manager untuk OSXNT
    Mengelola berbagai jenis proxy (HTTP, HTTPS, SOCKS4, SOCKS5)
    """
    
    # Proxy types
    PROXY_TYPES = {
        'http': 'http://',
        'https': 'https://',
        'socks4': 'socks4://',
        'socks5': 'socks5://'
    }
    
    def __init__(self, verbose=False):
        """
        Inisialisasi Port Proxy
        
        Args:
            verbose (bool): Mode verbose
        """
        self.v = Verbose(verbose)
        self.proxies = []
        self.current_index = 0
        self.session = None
        self.v.log("Port Proxy Manager initialized")
    
    def load_from_file(self, filename, proxy_type='http'):
        """
        Load proxy dari file
        
        Args:
            filename (str): File berisi daftar proxy
            proxy_type (str): Tipe proxy (http, https, socks4, socks5)
        
        Returns:
            int: Jumlah proxy yang diload
        """
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()
            
            self.proxies = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Format: ip:port atau user:pass@ip:port
                    proxy = self._format_proxy(line, proxy_type)
                    if proxy:
                        self.proxies.append(proxy)
            
            self.v.log(f"Loaded {len(self.proxies)} proxies from {filename}")
            return len(self.proxies)
            
        except FileNotFoundError:
            self.v.error(f"File {filename} tidak ditemukan")
            return 0
        except Exception as e:
            self.v.error(f"Error loading proxies: {e}")
            return 0
    
    def load_from_list(self, proxy_list, proxy_type='http'):
        """
        Load proxy dari list
        
        Args:
            proxy_list (list): List berisi proxy
            proxy_type (str): Tipe proxy
        
        Returns:
            int: Jumlah proxy yang diload
        """
        self.proxies = []
        for proxy in proxy_list:
            formatted = self._format_proxy(proxy, proxy_type)
            if formatted:
                self.proxies.append(formatted)
        
        self.v.log(f"Loaded {len(self.proxies)} proxies from list")
        return len(self.proxies)
    
    def _format_proxy(self, proxy_str, proxy_type='http'):
        """
        Format proxy string
        
        Args:
            proxy_str (str): String proxy (ip:port or user:pass@ip:port)
            proxy_type (str): Tipe proxy
        
        Returns:
            dict: Proxy formatted
        """
        try:
            proxy_str = proxy_str.strip()
            
            # Cek apakah ada authentication
            if '@' in proxy_str:
                auth, address = proxy_str.split('@', 1)
                if ':' in auth:
                    username, password = auth.split(':', 1)
                else:
                    username, password = auth, ''
            else:
                address = proxy_str
                username, password = None, None
            
            # Format address
            if ':' in address:
                ip, port = address.split(':', 1)
                port = int(port)
            else:
                self.v.error(f"Invalid proxy format: {proxy_str}")
                return None
            
            # Build proxy dict
            proxy_type_prefix = self.PROXY_TYPES.get(proxy_type.lower(), 'http://')
            
            if username and password:
                proxy_url = f"{proxy_type_prefix}{username}:{password}@{ip}:{port}"
                proxy_dict = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            else:
                proxy_url = f"{proxy_type_prefix}{ip}:{port}"
                proxy_dict = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            
            return {
                'ip': ip,
                'port': port,
                'type': proxy_type,
                'username': username,
                'password': password,
                'url': proxy_url,
                'dict': proxy_dict
            }
            
        except Exception as e:
            self.v.error(f"Error formatting proxy: {e}")
            return None
    
    def add_proxy(self, proxy_str, proxy_type='http'):
        """
        Tambah satu proxy
        
        Args:
            proxy_str (str): String proxy
            proxy_type (str): Tipe proxy
        
        Returns:
            bool: True jika berhasil
        """
        proxy = self._format_proxy(proxy_str, proxy_type)
        if proxy:
            self.proxies.append(proxy)
            self.v.log(f"Added proxy: {proxy_str}")
            return True
        return False
    
    def remove_proxy(self, index):
        """
        Hapus proxy berdasarkan index
        
        Args:
            index (int): Index proxy
        
        Returns:
            bool: True jika berhasil
        """
        if 0 <= index < len(self.proxies):
            removed = self.proxies.pop(index)
            self.v.log(f"Removed proxy: {removed['ip']}:{removed['port']}")
            return True
        return False
    
    def get_random_proxy(self):
        """
        Dapatkan proxy random
        
        Returns:
            dict: Proxy random atau None
        """
        if not self.proxies:
            self.v.error("No proxies available")
            return None
        
        return random.choice(self.proxies)
    
    def get_next_proxy(self):
        """
        Dapatkan proxy berikutnya (round-robin)
        
        Returns:
            dict: Proxy berikutnya
        """
        if not self.proxies:
            self.v.error("No proxies available")
            return None
        
        proxy = self.proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxies)
        return proxy
    
    def get_session(self, proxy=None, rotate=False):
        """
        Dapatkan requests session dengan proxy
        
        Args:
            proxy (dict): Proxy spesifik (None untuk random)
            rotate (bool): Rotate proxy setiap request
        
        Returns:
            requests.Session: Session dengan proxy
        """
        if rotate:
            # Untuk rotate, kita return session khusus
            return RotatingProxySession(self)
        
        session = requests.Session()
        
        if proxy:
            session.proxies = proxy['dict']
        elif self.proxies:
            proxy = self.get_random_proxy()
            session.proxies = proxy['dict']
        
        return session
    
    def test_proxy(self, proxy, test_url='https://api.ipify.org', timeout=10):
        """
        Test satu proxy
        
        Args:
            proxy (dict): Proxy to test
            test_url (str): URL untuk test
            timeout (int): Timeout
        
        Returns:
            bool: True jika proxy bekerja
        """
        try:
            session = requests.Session()
            session.proxies = proxy['dict']
            session.timeout = timeout
            
            r = session.get(test_url, timeout=timeout)
            
            if r.status_code == 200:
                self.v.log(f"✅ Proxy {proxy['ip']}:{proxy['port']} is working")
                return True
            else:
                self.v.log(f"❌ Proxy {proxy['ip']}:{proxy['port']} returned {r.status_code}")
                return False
                
        except Exception as e:
            self.v.log(f"❌ Proxy {proxy['ip']}:{proxy['port']} failed: {str(e)[:50]}")
            return False
    
    def test_all_proxies(self, test_url='https://api.ipify.org', timeout=10, remove_dead=True):
        """
        Test semua proxy
        
        Args:
            test_url (str): URL untuk test
            timeout (int): Timeout
            remove_dead (bool): Hapus proxy yang mati
        
        Returns:
            dict: Hasil test
        """
        if not self.proxies:
            self.v.error("No proxies to test")
            return {'total': 0, 'working': 0, 'dead': 0}
        
        self.v.log(f"Testing {len(self.proxies)} proxies...")
        
        working = []
        dead = []
        
        for proxy in self.proxies:
            if self.test_proxy(proxy, test_url, timeout):
                working.append(proxy)
            else:
                dead.append(proxy)
        
        if remove_dead:
            self.proxies = working
            self.v.log(f"Removed {len(dead)} dead proxies")
        
        result = {
            'total': len(working) + len(dead),
            'working': len(working),
            'dead': len(dead),
            'working_list': working,
            'dead_list': dead
        }
        
        self.v.log(f"Test complete: {len(working)} working, {len(dead)} dead")
        return result
    
    def get_status(self):
        """Dapatkan status proxy manager"""
        return {
            'total_proxies': len(self.proxies),
            'current_index': self.current_index,
            'proxies': self.proxies[:5]  # 5 proxy pertama aja
        }
    
    def clear(self):
        """Hapus semua proxy"""
        self.proxies = []
        self.current_index = 0
        self.v.log("All proxies cleared")


class RotatingProxySession:
    """
    Session dengan proxy rotating otomatis
    """
    
    def __init__(self, proxy_manager):
        """
        Inisialisasi rotating session
        
        Args:
            proxy_manager (PortProxy): Proxy manager instance
        """
        self.proxy_manager = proxy_manager
        self.session = requests.Session()
    
    def get(self, url, **kwargs):
        """GET request dengan proxy random"""
        proxy = self.proxy_manager.get_random_proxy()
        if proxy:
            self.session.proxies = proxy['dict']
        return self.session.get(url, **kwargs)
    
    def post(self, url, data=None, **kwargs):
        """POST request dengan proxy random"""
        proxy = self.proxy_manager.get_random_proxy()
        if proxy:
            self.session.proxies = proxy['dict']
        return self.session.post(url, data=data, **kwargs)
    
    def request(self, method, url, **kwargs):
        """Request dengan proxy random"""
        proxy = self.proxy_manager.get_random_proxy()
        if proxy:
            self.session.proxies = proxy['dict']
        return self.session.request(method, url, **kwargs)


# ========== CONTOH PENGGUNAAN ==========

if __name__ == "__main__":
    # Test Port Proxy
    proxy_mgr = PortProxy(verbose=True)
    
    # Tambah proxy manual
    proxy_mgr.add_proxy("127.0.0.1:8080", "http")
    proxy_mgr.add_proxy("user:pass@192.168.1.1:3128", "https")
    
    # Load dari file (buat file proxies.txt dulu)
    # proxy_mgr.load_from_file("proxies.txt", "socks5")
    
    # Test proxy
    proxy = proxy_mgr.get_random_proxy()
    if proxy:
        print(f"Using proxy: {proxy['ip']}:{proxy['port']}")
        
        # Test dengan session
        session = proxy_mgr.get_session(proxy)
        try:
            r = session.get('https://api.ipify.org?format=json', timeout=10)
            print(f"Your IP via proxy: {r.json()['ip']}")
        except:
            print("Proxy failed")
    
    # Test semua proxy
    # proxy_mgr.test_all_proxies()
    
    # Rotating session
    rot_session = proxy_mgr.get_session(rotate=True)
    for i in range(3):
        r = rot_session.get('https://api.ipify.org?format=json')
        print(f"Request {i+1} IP: {r.json()['ip']}")
