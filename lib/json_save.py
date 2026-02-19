import json
from datetime import datetime

def save_to_json(data, filename):
    """Save data to JSON file with timestamp"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4, default=str)
        print(f"[+] Results saved to {filename}")
        return True
    except Exception as e:
        print(f"[!] Failed to save JSON: {e}")
        return False

def prepare_output(data, target, module):
    """Wrap data with metadata"""
    return {
        "timestamp": str(datetime.now()),
        "target": target,
        "module": module,
        "data": data
    }
