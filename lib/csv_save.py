#!/usr/bin/env python3
# OSXNT - CSV Saver Module
# Simple CSV export untuk semua module

import csv
import os
from datetime import datetime

def save_to_csv(data, filename, fieldnames=None):
    """
    Simpan data ke file CSV
    
    Args:
        data: list of dictionaries atau list of lists
        filename: nama file CSV
        fieldnames: list kolom (optional)
    
    Returns:
        bool: True jika berhasil
    """
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            # Kalo data kosong
            if not data:
                f.write("No data")
                return True
            
            # Kalo data berupa list of dictionaries
            if isinstance(data[0], dict):
                if not fieldnames:
                    fieldnames = data[0].keys()
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            # Kalo data berupa list of lists
            elif isinstance(data[0], (list, tuple)):
                writer = csv.writer(f)
                writer.writerows(data)
            
            # Kalo data berupa single item
            else:
                writer = csv.writer(f)
                for item in data:
                    writer.writerow([item])
        
        print(f"[+] Data saved to {filename}")
        return True
        
    except Exception as e:
        print(f"[!] Error saving CSV: {e}")
        return False

def append_to_csv(data, filename):
    """Append data ke file CSV yang sudah ada"""
    try:
        with open(filename, 'a', newline='', encoding='utf-8') as f:
            if isinstance(data[0], dict):
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writerows(data)
            else:
                writer = csv.writer(f)
                writer.writerows(data)
        
        print(f"[+] Data appended to {filename}")
        return True
    except Exception as e:
        print(f"[!] Error appending CSV: {e}")
        return False

def dict_to_csv(data_dict, filename):
    """Convert dictionary ke CSV (key, value pairs)"""
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Key', 'Value'])
            for key, value in data_dict.items():
                writer.writerow([key, value])
        
        print(f"[+] Dictionary saved to {filename}")
        return True
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

# Contoh penggunaan
if __name__ == "__main__":
    # Contoh data
    data = [
        {'ip': '8.8.8.8', 'country': 'US', 'city': 'Mountain View'},
        {'ip': '1.1.1.1', 'country': 'AU', 'city': 'Sydney'}
    ]
    
    save_to_csv(data, 'test.csv')
