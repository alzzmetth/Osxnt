import socket
import threading
from queue import Queue
from lib.verbose import Verbose
from lib.json_save import save_to_json, prepare_output

COMMON_PORTS = {
    21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
    80: 'HTTP', 110: 'POP3', 111: 'RPC', 135: 'MSRPC', 139: 'NetBIOS',
    143: 'IMAP', 443: 'HTTPS', 445: 'SMB', 993: 'IMAPS', 995: 'POP3S',
    1723: 'PPTP', 3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL',
    5900: 'VNC', 6379: 'Redis', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt',
    27017: 'MongoDB'
}

def scan_port(host, port, timeout, results, verbose):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        if result == 0:
            service = COMMON_PORTS.get(port, 'unknown')
            results.append({'port': port, 'service': service})
            if verbose:
                print(f"  [OPEN] {port}/tcp - {service}")
        sock.close()
    except:
        pass

def port_scan(host, ports, threads=20, timeout=2, verbose=False, save=None):
    v = Verbose(verbose)
    v.log(f"Scanning {host} for ports...")
    
    # Resolve host
    try:
        ip = socket.gethostbyname(host)
        v.log(f"Resolved to {ip}")
    except:
        v.error("Cannot resolve host")
        return
    
    # Parse ports
    if isinstance(ports, str):
        if '-' in ports:
            start, end = map(int, ports.split('-'))
            port_list = list(range(start, end+1))
        else:
            port_list = [int(p.strip()) for p in ports.split(',')]
    else:
        port_list = ports
    
    v.log(f"Scanning {len(port_list)} ports")
    
    queue = Queue()
    results = []
    
    for port in port_list:
        queue.put(port)
    
    def worker():
        while not queue.empty():
            port = queue.get()
            scan_port(ip, port, timeout, results, verbose)
            queue.task_done()
    
    # Start threads
    thread_list = []
    for _ in range(min(threads, len(port_list))):
        t = threading.Thread(target=worker)
        t.start()
        thread_list.append(t)
    
    for t in thread_list:
        t.join()
    
    # Output
    print(f"\n[ Open Ports on {host} ]")
    if results:
        for r in sorted(results, key=lambda x: x['port']):
            print(f"  {r['port']}/tcp - {r['service']}")
    else:
        print("  No open ports found")
    
    if save:
        output = prepare_output(results, host, "portscan")
        save_to_json(output, save)
