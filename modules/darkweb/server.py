#!/usr/bin/env python3
# DarkWeb - Simple Web Server

import http.server
import socketserver
import os
import threading
import socket

class DarkWebServer:
    """
    Simple HTTP server untuk serve file
    """
    
    def __init__(self, config):
        self.config = config
        self.port = config['port']
        self.directory = config['site_dir']
        self.server = None
        self.thread = None
    
    def prepare_site(self):
        """Prepare site directory"""
        os.makedirs(self.directory, exist_ok=True)
        
        # Buat index.html default jika kosong
        index_path = f"{self.directory}/index.html"
        if not os.path.exists(index_path):
            with open(index_path, 'w') as f:
                f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>{self.config['site_name']}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f0f0f0;
        }}
        h1 {{ color: #333; }}
        .info {{ background: #fff; padding: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>🌐 {self.config['site_name']}</h1>
    <div class="info">
        <p>Welcome to your Dark Web site!</p>
        <p>Put your HTML, CSS, JS files in: <code>{self.directory}</code></p>
    </div>
</body>
</html>""")
        
        print(f"[+] Site directory: {self.directory}")
    
    def start(self):
        """Start web server"""
        self.prepare_site()
        
        # Pindah ke directory
        os.chdir(self.directory)
        
        # Create handler
        handler = http.server.SimpleHTTPRequestHandler
        
        # Cek port available
        if not self._is_port_available(self.port):
            print(f"[!] Port {self.port} already in use")
            return False
        
        # Start server di thread terpisah
        try:
            self.server = socketserver.TCPServer(("", self.port), handler)
            self.thread = threading.Thread(target=self.server.serve_forever)
            self.thread.daemon = True
            self.thread.start()
            
            print(f"[+] Web server started on port {self.port}")
            return True
            
        except Exception as e:
            print(f"[!] Error starting server: {e}")
            return False
    
    def _is_port_available(self, port):
        """Check if port is available"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
    
    def stop(self):
        """Stop web server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            print("[*] Web server stopped")
