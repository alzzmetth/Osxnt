#!/usr/bin/env python3
# OSXNT - DarkWeb Authentication Module
# Menyediakan autentikasi untuk hidden service

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from .config import Config

class DarkWebAuth:
    """Manajemen autentikasi untuk darkweb service"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.users = self.config.get('auth_users', {})
        self.sessions = {}  # token: {username, expires}
        self.failed_attempts = {}  # ip: count, timestamp
    
    def add_user(self, username, password, role='user', max_attempts=5):
        """Tambah user baru"""
        salt = secrets.token_hex(16)
        password_hash = self._hash_password(password, salt)
        
        self.users[username] = {
            'salt': salt,
            'hash': password_hash,
            'role': role,
            'created': datetime.now().isoformat(),
            'last_login': None,
            'max_attempts': max_attempts
        }
        self._save_users()
        return True
    
    def remove_user(self, username):
        """Hapus user"""
        if username in self.users:
            del self.users[username]
            self._save_users()
            return True
        return False
    
    def authenticate(self, username, password, client_ip=None):
        """Autentikasi user"""
        # Cek failed attempts
        if client_ip and self._is_ip_blocked(client_ip):
            return None, "Too many failed attempts. Try later."
        
        if username not in self.users:
            self._record_failed_attempt(client_ip)
            return None, "Invalid username or password"
        
        user = self.users[username]
        password_hash = self._hash_password(password, user['salt'])
        
        if hmac.compare_digest(password_hash, user['hash']):
            # Sukses
            token = self._generate_token()
            self.sessions[token] = {
                'username': username,
                'expires': time.time() + 86400,  # 24 jam
                'created': time.time()
            }
            # Update last login
            user['last_login'] = datetime.now().isoformat()
            self._save_users()
            # Reset failed attempts untuk IP ini
            if client_ip and client_ip in self.failed_attempts:
                del self.failed_attempts[client_ip]
            return token, "Authentication successful"
        else:
            self._record_failed_attempt(client_ip)
            return None, "Invalid username or password"
    
    def verify_token(self, token):
        """Verifikasi token session"""
        if token in self.sessions:
            if self.sessions[token]['expires'] > time.time():
                return self.sessions[token]['username']
            else:
                del self.sessions[token]
        return None
    
    def revoke_token(self, token):
        """Hapus token (logout)"""
        if token in self.sessions:
            del self.sessions[token]
            return True
        return False
    
    def change_password(self, username, old_password, new_password):
        """Ganti password"""
        if username not in self.users:
            return False, "User not found"
        
        user = self.users[username]
        old_hash = self._hash_password(old_password, user['salt'])
        
        if not hmac.compare_digest(old_hash, user['hash']):
            return False, "Old password incorrect"
        
        # Generate salt baru
        new_salt = secrets.token_hex(16)
        new_hash = self._hash_password(new_password, new_salt)
        user['salt'] = new_salt
        user['hash'] = new_hash
        self._save_users()
        return True, "Password changed"
    
    def basic_auth_middleware(self, handler_func):
        """Decorator untuk HTTP basic auth"""
        def wrapper(request, *args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Basic '):
                return self._unauthorized_response()
            
            import base64
            try:
                creds = base64.b64decode(auth_header[6:]).decode().split(':')
                username, password = creds[0], creds[1]
                token, msg = self.authenticate(username, password, request.client_address[0])
                if token:
                    request.auth_user = username
                    return handler_func(request, *args, **kwargs)
            except:
                pass
            
            return self._unauthorized_response()
        return wrapper
    
    def token_auth_middleware(self, handler_func):
        """Decorator untuk token-based auth (Bearer)"""
        def wrapper(request, *args, **kwargs):
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return self._unauthorized_response()
            
            token = auth_header[7:]
            username = self.verify_token(token)
            if username:
                request.auth_user = username
                return handler_func(request, *args, **kwargs)
            
            return self._unauthorized_response()
        return wrapper
    
    def _hash_password(self, password, salt):
        """Hash password dengan PBKDF2"""
        return hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
    
    def _generate_token(self):
        """Generate random token"""
        return secrets.token_urlsafe(32)
    
    def _save_users(self):
        """Simpan users ke config"""
        self.config.set('auth_users', self.users)
    
    def _record_failed_attempt(self, ip):
        """Catat failed attempt untuk rate limiting"""
        if not ip:
            return
        now = time.time()
        if ip in self.failed_attempts:
            count, first = self.failed_attempts[ip]
            if now - first > 300:  # 5 menit reset
                self.failed_attempts[ip] = (1, now)
            else:
                self.failed_attempts[ip] = (count + 1, first)
        else:
            self.failed_attempts[ip] = (1, now)
    
    def _is_ip_blocked(self, ip, max_attempts=5, window=300):
        """Cek apakah IP diblokir karena gagal login"""
        if ip not in self.failed_attempts:
            return False
        count, first = self.failed_attempts[ip]
        if time.time() - first > window:
            del self.failed_attempts[ip]
            return False
        return count >= max_attempts
    
    def _unauthorized_response(self):
        """Return HTTP 401 response"""
        from http.server import BaseHTTPRequestHandler
        class Response:
            def __init__(self):
                self.status = 401
                self.headers = {'WWW-Authenticate': 'Basic realm="DarkWeb Login"'}
                self.body = b"Unauthorized"
        return Response()
