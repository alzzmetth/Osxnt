#!/usr/bin/env python3
# OSXNT - File Helper Module
# Helper functions untuk file operations

import os
import shutil
import glob
from datetime import datetime

def ensure_dir(directory):
    """Buat directory kalo belum ada"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"[+] Created directory: {directory}")
        return True
    return False

def get_unique_filename(filename):
    """Generate unique filename dengan timestamp"""
    base, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{base}_{timestamp}{ext}"

def list_files(directory, pattern='*'):
    """List files dalam directory"""
    files = glob.glob(os.path.join(directory, pattern))
    return [os.path.basename(f) for f in files if os.path.isfile(f)]

def delete_file(filename):
    """Delete file dengan aman"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            print(f"[+] Deleted: {filename}")
            return True
    except Exception as e:
        print(f"[!] Error deleting: {e}")
    return False

def copy_file(src, dst):
    """Copy file"""
    try:
        shutil.copy2(src, dst)
        print(f"[+] Copied: {src} -> {dst}")
        return True
    except Exception as e:
        print(f"[!] Error copying: {e}")
        return False

def move_file(src, dst):
    """Move file"""
    try:
        shutil.move(src, dst)
        print(f"[+] Moved: {src} -> {dst}")
        return True
    except Exception as e:
        print(f"[!] Error moving: {e}")
        return False

def get_file_size(filename):
    """Get file size in human readable format"""
    try:
        size = os.path.getsize(filename)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    except:
        return "Unknown"

def read_file(filename):
    """Read file content"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[!] Error reading file: {e}")
        return None

# Contoh penggunaan
if __name__ == "__main__":
    ensure_dir("output")
    print(list_files("."))
