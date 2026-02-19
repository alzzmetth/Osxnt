#!/usr/bin/env python3
# OSXNT - OSINT Toolkit by alzzdevmaret

import argparse
import sys
from core.banner import show_banner
from core.about import about
from config.config import config
from lib.multi_target import read_targets_from_file
from modules import iptrack, webtrack, dns, scanport, subdomain

def main():
    show_banner()
    
    parser = argparse.ArgumentParser(description="OSXNT - OSINT Toolkit", add_help=False)
    
    # Global options
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('-s', metavar='file.json', help='Save output to JSON file')
    
    # Subcommands
    parser.add_argument('-trackip', metavar='IP', help='Track IP address (use "myip" for your own IP)')
    parser.add_argument('-webtrack', choices=['ip', 'dns'], help='Web tracking: ip (get IPs), dns (get DNS records)')
    parser.add_argument('-ip', metavar='TARGET', help='Target for -webtrack ip')
    parser.add_argument('-dns', metavar='TARGET', help='Target for -webtrack dns')
    parser.add_argument('-scan', action='store_true', help='Port scanner')
    parser.add_argument('-p', metavar='PORTS', help='Ports to scan (e.g., 80,443 or 1-1000)')
    parser.add_argument('-sbdomain', action='store_true', help='Subdomain scanner')
    parser.add_argument('-use', metavar='THREADS', type=int, help='Number of threads for subdomain scan')
    parser.add_argument('-about', action='store_true', help='Show about info')
    
    # Positional target for scan and subdomain
    parser.add_argument('target', nargs='?', help='Target host/IP/domain')
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    args = parser.parse_args()
    
    # Handle about
    if args.about:
        about()
        sys.exit(0)
    
    verbose = args.verbose
    save_file = args.s
    
    # IP Track
    if args.trackip:
        if args.trackip.lower() == 'myip':
            myip = iptrack.get_public_ip()
            if myip:
                iptrack.track_ip(myip, verbose, save_file)
            else:
                print("[!] Could not get your public IP")
        else:
            iptrack.track_ip(args.trackip, verbose, save_file)
    
    # Webtrack
    elif args.webtrack:
        if args.webtrack == 'ip':
            if not args.ip:
                print("[!] Need -ip <target>")
                sys.exit(1)
            webtrack.track_web(args.ip, verbose, save_file)
        elif args.webtrack == 'dns':
            if not args.dns:
                print("[!] Need -dns <target>")
                sys.exit(1)
            dns.dns_lookup(args.dns, verbose=verbose, save=save_file)
    
    # Port scan
    elif args.scan:
        if not args.p or not args.target:
            print("[!] Usage: osxnt.py -scan -p <ports> <target>")
            sys.exit(1)
        threads = config.get('threads', 20)
        timeout = config.get('timeout', 2)
        scanport.port_scan(args.target, args.p, threads, timeout, verbose, save_file)
    
    # Subdomain scan
    elif args.sbdomain:
        if not args.target:
            print("[!] Need target domain")
            sys.exit(1)
        # Use wordlist from requiments/subdomain.txt or subdomain2.txt? Kita bisa pilih berdasarkan argumen -use?
        # Karena -use dimaksudkan untuk jumlah thread, kita asumsikan wordlist default subdomain.txt
        # Bisa juga nanti dikembangkan: -w untuk pilih wordlist
        wordlist = "requiments/subdomain.txt"
        threads = args.use if args.use else config.get('threads', 20)
        timeout = config.get('timeout', 3)
        subdomain.subdomain_scan(args.target, wordlist, threads, timeout, verbose, save_file)
    
    else:
        print("[!] No valid command specified. Use -h for help.")

if __name__ == "__main__":
    main()
