# lib/multi_target.py
import os

def read_targets_from_file(filename):
    """Baca daftar target dari file (satu per baris, abaikan komentar #)"""
    targets = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    targets.append(line)
        return targets
    except FileNotFoundError:
        print(f"[!] File {filename} tidak ditemukan")
        return None
    except Exception as e:
        print(f"[!] Error membaca file: {e}")
        return None

def sanitize_filename(name):
    """Bersihkan string untuk digunakan sebagai nama file/folder"""
    import re
    name = re.sub(r'[^\w\-_\.]', '_', name)
    return name

def process_placeholder(path, placeholder, value):
    """Ganti placeholder dalam string path dengan nilai yang sudah disanitasi"""
    safe_value = sanitize_filename(value)
    return path.replace(placeholder, safe_value)

# Bisa ditambah fungsi lain sesuai kebutuhan
