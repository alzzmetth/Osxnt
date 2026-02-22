#!/usr/bin/env python3
# OSXNT - Input Validator Module
# Validasi input dari user

import re
import ipaddress
from urllib.parse import urlparse

def is_valid_ip(ip):
    """Check if string is valid IP address"""
    try:
        ipaddress.ip_address(ip)
        return True
    except:
        return False

def is_valid_domain(domain):
    """Check if string is valid domain name"""
    pattern = r'^[a-zA-Z0-9][a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, domain) is not None

def is_valid_url(url):
    """Check if string is valid URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def is_valid_email(email):
    """Check if string is valid email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_port(port):
    """Check if port number is valid"""
    try:
        port = int(port)
        return 1 <= port <= 65535
    except:
        return False

def is_valid_filename(filename):
    """Check if filename is valid"""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    return not any(c in invalid_chars for c in filename)

def validate_input(input_str, input_type='any'):
    """Validate input based on type"""
    validators = {
        'ip': is_valid_ip,
        'domain': is_valid_domain,
        'url': is_valid_url,
        'email': is_valid_email,
        'port': is_valid_port,
        'filename': is_valid_filename
    }
    
    if input_type in validators:
        return validators[input_type](input_str)
    return True  # 'any' always valid

def sanitize_filename(filename):
    """Sanitize filename (remove unsafe characters)"""
    # Replace unsafe chars with underscore
    unsafe = '<>:"/\\|?* '
    for char in unsafe:
        filename = filename.replace(char, '_')
    return filename

# Contoh penggunaan
if __name__ == "__main__":
    print(is_valid_ip("8.8.8.8"))  # True
    print(is_valid_domain("google.com"))  # True
    print(is_valid_email("test@example.com"))  # True
