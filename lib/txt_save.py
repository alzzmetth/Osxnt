#!/usr/bin/env python3
# OSXNT - TXT Saver Module
# Simple text file export

import os
from datetime import datetime

def save_to_txt(content, filename, mode='w'):
    """
    Simpan content ke file text
    
    Args:
        content: string atau list of strings
        filename: nama file
        mode: 'w' (write) atau 'a' (append)
    
    Returns:
        bool: True jika berhasil
    """
    try:
        with open(filename, mode, encoding='utf-8') as f:
            if isinstance(content, list):
                for line in content:
                    f.write(str(line) + '\n')
            else:
                f.write(str(content) + '\n')
        
        print(f"[+] Content saved to {filename}")
        return True
    except Exception as e:
        print(f"[!] Error saving TXT: {e}")
        return False

def append_to_txt(content, filename):
    """Append content ke file text"""
    return save_to_txt(content, filename, 'a')

def save_results(results, filename, title=None):
    """
    Save hasil dengan format yang rapi
    
    Args:
        results: dictionary atau list
        filename: nama file
        title: judul section (optional)
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            # Header
            f.write("="*60 + "\n")
            f.write(f"OSXNT Results - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*60 + "\n\n")
            
            if title:
                f.write(f"📌 {title}\n")
                f.write("-"*40 + "\n")
            
            # Write results
            if isinstance(results, dict):
                for key, value in results.items():
                    f.write(f"{key}: {value}\n")
            elif isinstance(results, list):
                for i, item in enumerate(results, 1):
                    if isinstance(item, dict):
                        f.write(f"\n--- Item {i} ---\n")
                        for k, v in item.items():
                            f.write(f"  {k}: {v}\n")
                    else:
                        f.write(f"{i}. {item}\n")
            else:
                f.write(str(results) + "\n")
            
            f.write("\n" + "="*60 + "\n")
        
        print(f"[+] Results saved to {filename}")
        return True
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

# Contoh penggunaan
if __name__ == "__main__":
    results = {
        'target': '8.8.8.8',
        'country': 'United States',
        'city': 'Mountain View'
    }
    save_results(results, 'report.txt', 'IP Information')
