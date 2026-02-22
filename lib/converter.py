#!/usr/bin/env python3
# OSXNT - Data Converter Module
# Convert antar format

import json
import csv
from datetime import datetime

def json_to_csv(json_data, csv_filename):
    """Convert JSON ke CSV"""
    try:
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        if not data:
            return False
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            if isinstance(data, dict):
                writer = csv.writer(f)
                writer.writerow(['Key', 'Value'])
                for key, value in data.items():
                    writer.writerow([key, value])
            elif isinstance(data, list) and len(data) > 0:
                if isinstance(data[0], dict):
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        
        print(f"[+] Converted JSON to {csv_filename}")
        return True
    except Exception as e:
        print(f"[!] Conversion error: {e}")
        return False

def csv_to_json(csv_filename):
    """Convert CSV ke JSON"""
    try:
        data = []
        with open(csv_filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    except Exception as e:
        print(f"[!] Error: {e}")
        return None

def dict_to_txt(data, txt_filename, format_type='simple'):
    """Convert dictionary ke formatted text"""
    try:
        with open(txt_filename, 'w', encoding='utf-8') as f:
            if format_type == 'simple':
                for key, value in data.items():
                    f.write(f"{key}: {value}\n")
            elif format_type == 'table':
                # Simple table format
                max_key_len = max(len(str(k)) for k in data.keys())
                for key, value in data.items():
                    f.write(f"{str(key):<{max_key_len}} : {value}\n")
            elif format_type == 'json':
                f.write(json.dumps(data, indent=2))
        
        return True
    except Exception as e:
        print(f"[!] Error: {e}")
        return False

def list_to_columns(data, cols=3):
    """Convert list to column format for display"""
    result = []
    for i in range(0, len(data), cols):
        row = data[i:i+cols]
        result.append('\t'.join(str(x) for x in row))
    return '\n'.join(result)

def size_to_human(size):
    """Convert bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

def timestamp_to_date(timestamp):
    """Convert timestamp ke readable date"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Contoh penggunaan
if __name__ == "__main__":
    data = {'name': 'OSXNT', 'version': '2.3.2'}
    dict_to_txt(data, 'output.txt', 'table')
