#!/usr/bin/env python3
# OSXNT - DarkWeb Monitor Module
# Memonitor traffic, statistik, uptime, dll.

import time
import threading
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from .config import Config

class DarkWebMonitor:
    """Monitor untuk hidden service"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.stats = {
            'total_requests': 0,
            'unique_visitors': set(),
            'bytes_sent': 0,
            'bytes_received': 0,
            'requests_per_minute': [],
            'status_codes': Counter(),
            'user_agents': Counter(),
            'paths': Counter(),
            'referrers': Counter(),
            'countries': Counter(),  # butuh GeoIP
        }
        self.start_time = time.time()
        self.lock = threading.Lock()
        self._load_stats()
    
    def _load_stats(self):
        """Load statistik dari config"""
        saved = self.config.get('monitor_stats', {})
        if saved:
            self.stats['total_requests'] = saved.get('total_requests', 0)
            self.stats['unique_visitors'] = set(saved.get('unique_visitors', []))
            self.stats['bytes_sent'] = saved.get('bytes_sent', 0)
            self.stats['bytes_received'] = saved.get('bytes_received', 0)
            self.stats['status_codes'] = Counter(saved.get('status_codes', {}))
            # lainnya...
    
    def _save_stats(self):
        """Simpan statistik ke config"""
        to_save = {
            'total_requests': self.stats['total_requests'],
            'unique_visitors': list(self.stats['unique_visitors']),
            'bytes_sent': self.stats['bytes_sent'],
            'bytes_received': self.stats['bytes_received'],
            'status_codes': dict(self.stats['status_codes']),
        }
        self.config.set('monitor_stats', to_save)
    
    def log_request(self, request):
        """Catat request yang masuk"""
        with self.lock:
            self.stats['total_requests'] += 1
            ip = request.client_address[0]
            self.stats['unique_visitors'].add(ip)
            
            # Status code
            self.stats['status_codes'][request.status_code] += 1
            
            # Path
            path = request.path
            self.stats['paths'][path] += 1
            
            # User-Agent
            ua = request.headers.get('User-Agent', 'Unknown')
            self.stats['user_agents'][ua] += 1
            
            # Referrer
            ref = request.headers.get('Referer', 'Direct')
            self.stats['referrers'][ref] += 1
            
            # Bytes
            if hasattr(request, 'content_length'):
                self.stats['bytes_sent'] += request.content_length
            
            # Update per-minute
            now = time.time()
            self.stats['requests_per_minute'].append((now, 1))
            # Bersihkan data lebih dari 1 jam
            cutoff = now - 3600
            self.stats['requests_per_minute'] = [(t, c) for t, c in self.stats['requests_per_minute'] if t > cutoff]
            
            # Auto-save setiap 100 request
            if self.stats['total_requests'] % 100 == 0:
                self._save_stats()
    
    def get_uptime(self):
        """Dapatkan uptime dalam detik"""
        return time.time() - self.start_time
    
    def get_uptime_str(self):
        """Uptime dalam format string"""
        seconds = int(self.get_uptime())
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        return ' '.join(parts)
    
    def get_requests_per_minute(self):
        """Hitung rata-rata request per menit dalam 1 jam terakhir"""
        if not self.stats['requests_per_minute']:
            return 0
        # Kelompokkan per menit
        minute_counts = defaultdict(int)
        for ts, count in self.stats['requests_per_minute']:
            minute = int(ts // 60)
            minute_counts[minute] += count
        if minute_counts:
            total = sum(minute_counts.values())
            return total / len(minute_counts)
        return 0
    
    def get_top_paths(self, n=10):
        """Top N path yang paling sering diakses"""
        return self.stats['paths'].most_common(n)
    
    def get_top_user_agents(self, n=10):
        """Top N user agents"""
        return self.stats['user_agents'].most_common(n)
    
    def get_status_summary(self):
        """Ringkasan status"""
        return {
            'uptime': self.get_uptime_str(),
            'total_requests': self.stats['total_requests'],
            'unique_visitors': len(self.stats['unique_visitors']),
            'bytes_sent': self._bytes_to_human(self.stats['bytes_sent']),
            'bytes_received': self._bytes_to_human(self.stats['bytes_received']),
            'requests_per_minute_avg': self.get_requests_per_minute(),
            'status_codes': dict(self.stats['status_codes']),
        }
    
    def _bytes_to_human(self, bytes):
        """Konversi bytes ke format human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes < 1024:
                return f"{bytes:.1f} {unit}"
            bytes /= 1024
        return f"{bytes:.1f} TB"
    
    def reset_stats(self):
        """Reset semua statistik"""
        with self.lock:
            self.stats = {
                'total_requests': 0,
                'unique_visitors': set(),
                'bytes_sent': 0,
                'bytes_received': 0,
                'requests_per_minute': [],
                'status_codes': Counter(),
                'user_agents': Counter(),
                'paths': Counter(),
                'referrers': Counter(),
                'countries': Counter(),
            }
            self._save_stats()
    
    def generate_report(self):
        """Generate laporan lengkap"""
        summary = self.get_status_summary()
        lines = []
        lines.append("="*50)
        lines.append("DARKWEB MONITOR REPORT")
        lines.append("="*50)
        lines.append(f"Uptime: {summary['uptime']}")
        lines.append(f"Total Requests: {summary['total_requests']}")
        lines.append(f"Unique Visitors: {summary['unique_visitors']}")
        lines.append(f"Data Sent: {summary['bytes_sent']}")
        lines.append(f"Data Received: {summary['bytes_received']}")
        lines.append(f"Avg RPM: {summary['requests_per_minute_avg']:.2f}")
        lines.append("\nTop Paths:")
        for path, count in self.get_top_paths(5):
            lines.append(f"  {path}: {count}")
        lines.append("\nTop User Agents:")
        for ua, count in self.get_top_user_agents(5):
            lines.append(f"  {ua[:50]}: {count}")
        return "\n".join(lines)
