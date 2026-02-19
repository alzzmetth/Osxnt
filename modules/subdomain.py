#!/usr/bin/env python3
# OSXNT - Subdomain Enumeration Module

import socket
import threading
from queue import Queue
from lib.verbose import Verbose
from lib.json_save import save_to_json, prepare_output

def check_subdomain(domain, sub, timeout, results, verbose):
    """Check if subdomain exists"""
    full = f"{sub}.{domain}"
    try:
        ip = socket.gethostbyname(full)
        results.append({'subdomain': full, 'ip': ip})
        if verbose:
            print(f"  [FOUND] {full} -> {ip}")
        return True
    except socket.gaierror:
        return False
    except Exception as e:
        if verbose:
            print(f"  [ERROR] {full}: {e}")
        return False

def load_wordlist(filename):
    """Load subdomain wordlist from file"""
    try:
        with open(filename, 'r') as f:
            # Skip empty lines and comments
            words = [line.strip() for line in f 
                    if line.strip() and not line.startswith('#')]
        return words
    except FileNotFoundError:
        print(f"[!] Wordlist not found: {filename}")
        return []
    except Exception as e:
        print(f"[!] Error loading wordlist: {e}")
        return []

def subdomain_scan(domain, wordlist_file, threads=20, timeout=3, verbose=False, save=None):
    """Main subdomain scanner function"""
    v = Verbose(verbose)
    print(f"\n[ Subdomain Scanner ]")
    print(f"Target: {domain}")
    print(f"Wordlist: {wordlist_file}")
    print(f"Threads: {threads}")
    print("-" * 50)
    
    # Load wordlist
    v.log("Loading wordlist...")
    subdomains = load_wordlist(wordlist_file)
    if not subdomains:
        v.error("No subdomains loaded")
        return
    
    v.log(f"Loaded {len(subdomains)} subdomains")
    
    # Setup queue and results
    queue = Queue()
    results = []
    found_count = 0
    
    # Put all subdomains in queue
    for sub in subdomains:
        queue.put(sub)
    
    # Worker function for threads
    def worker():
        nonlocal found_count
        while not queue.empty():
            try:
                sub = queue.get_nowait()
                if check_subdomain(domain, sub, timeout, results, verbose):
                    found_count += 1
            except:
                pass
            finally:
                queue.task_done()
    
    # Create and start threads
    thread_list = []
    for _ in range(min(threads, len(subdomains))):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        thread_list.append(t)
    
    # Wait for all threads to complete
    for t in thread_list:
        t.join(timeout=timeout * 2)
    
    # Sort results
    results.sort(key=lambda x: x['subdomain'])
    
    # Display results
    print(f"\n[ Results Found: {found_count} ]")
    if results:
        for r in results:
            print(f"  {r['subdomain']:<30} -> {r['ip']}")
    else:
        print("  No subdomains found")
    
    # Save to file if requested
    if save and results:
        output = prepare_output(results, domain, "subdomain")
        save_to_json(output, save)
    
    print(f"\n[ Scan Complete ]")
    print(f"Total checked: {len(subdomains)}")
    print(f"Found: {found_count}")

# For standalone testing
if __name__ == "__main__":
    # Example usage
    subdomain_scan("example.com", "requiments/subdomain.txt", verbose=True)
