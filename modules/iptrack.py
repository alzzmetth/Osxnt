import requests
import socket
from core.banner import Fore
from lib.json_save import save_to_json, prepare_output
from lib.verbose import Verbose

def get_public_ip():
    try:
        r = requests.get('https://api.ipify.org?format=json', timeout=5)
        return r.json()['ip']
    except:
        return None

def track_ip(ip, verbose=False, save=None):
    v = Verbose(verbose)
    v.log(f"Tracking IP: {ip}")
    
    # Resolve hostname if domain
    try:
        resolved = socket.gethostbyname(ip)
        if resolved != ip:
            v.log(f"Resolved to IP: {resolved}")
            ip = resolved
    except:
        pass
    
    url = f"http://ip-api.com/json/{ip}?fields=66846719"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
        if data.get('status') == 'fail':
            v.error(f"Failed: {data.get('message', 'Invalid IP')}")
            return
        
        print(f"\n{Fore.GREEN}[ IP INFO ]{Fore.RESET}")
        print(f"IP: {data.get('query')}")
        print(f"Country: {data.get('country')} ({data.get('countryCode')})")
        print(f"Region: {data.get('regionName')}")
        print(f"City: {data.get('city')}")
        print(f"ISP: {data.get('isp')}")
        print(f"Organization: {data.get('org')}")
        print(f"AS: {data.get('as')}")
        print(f"Coordinates: {data.get('lat')}, {data.get('lon')}")
        
        if save:
            output = prepare_output(data, ip, "iptrack")
            save_to_json(output, save)
            
    except Exception as e:
        v.error(f"Request failed: {e}")
