#!/usr/bin/env python3
# OSXNT - DarkWeb Config Module
# Menggantikan config.json dengan class Config (lebih aman untuk pyinstaller)

import os
import json
from lib.file_helper import ensure_dir

class Config:
    """Manajemen konfigurasi darkweb (simpan/load dari JSON)"""
    
    DEFAULT_CONFIG = {
        "services": {},
        "tor_port": 9050,
        "control_port": 9051,
        "data_dir": "darkweb_data",
        "default_port": 8080
    }
    
    def __init__(self, config_path=None):
        """
        Inisialisasi config
        
        Args:
            config_path: path ke file konfigurasi (jika None, pakai default)
        """
        if config_path is None:
            # Cari di direktori saat ini atau di folder data
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_path = os.path.join(base_dir, 'darkweb_config.json')
        else:
            self.config_path = config_path
        
        self.config = self.DEFAULT_CONFIG.copy()
        self.load()
    
    def load(self):
        """Load konfigurasi dari file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    # Update config dengan yang diload, tapi pertahankan default jika ada kunci baru
                    self.config.update(loaded)
                print(f"[✓] Config loaded from {self.config_path}")
            except Exception as e:
                print(f"[!] Error loading config: {e}")
        else:
            # Buat direktori jika perlu
            ensure_dir(os.path.dirname(self.config_path))
            self.save()
            print(f"[+] Created default config at {self.config_path}")
    
    def save(self):
        """Simpan konfigurasi ke file"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"[!] Error saving config: {e}")
            return False
    
    def get(self, key, default=None):
        """Dapatkan nilai konfigurasi"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """Set nilai konfigurasi dan simpan"""
        self.config[key] = value
        self.save()
    
    def add_service(self, name, service_config):
        """Tambah service baru"""
        if 'services' not in self.config:
            self.config['services'] = {}
        self.config['services'][name] = service_config
        self.save()
    
    def get_service(self, name):
        """Dapatkan konfigurasi service"""
        return self.config.get('services', {}).get(name)
    
    def remove_service(self, name):
        """Hapus service"""
        if name in self.config.get('services', {}):
            del self.config['services'][name]
            self.save()
            return True
        return False
    
    def list_services(self):
        """Daftar semua service"""
        return self.config.get('services', {})
