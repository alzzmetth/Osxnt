#!/usr/bin/env python3
# OSXNT - OSINT Toolkit by alzzdevmaret
# Version: 2.0.0

import argparse
import sys
import os
from core.banner import show_banner
from core.about import about
from config.config import config
from lib.multi_target import read_targets_from_file
from modules import iptrack, dns, scanport, subdomain
from modules.webtrack import track_web, process_single_target, process_multi_targets

# Versi tools
VERSION = "2.0.0"
AUTHOR = "alzzdevmaret"
GITHUB = "https://github.com/alzzdevmaret/osxnt"

def show_version():
    """Tampilkan informasi versi"""
    print(f"""
OSXNT Version: {VERSION}
Author: {AUTHOR}
Repository: {GITHUB}
License: MIT
Python: {sys.version.split()[0]}
Platform: {sys.platform}
    """.strip())

def show_full_help():
    """Tampilkan help lengkap dengan format profesional"""
    help_text = f"""
{'='*60}
{'OSXNT - OSINT Toolkit':^60}
{'='*60}

USAGE:
    osxnt.py [-h] [-v] [-s file.json] [-trackip IP] [-webtrack {{ip,dns}}]
             [-ip TARGET] [-dns TARGET] [-scan] [-p PORTS] [-sbdomain]
             [-use THREADS] [-about] [target]

GLOBAL OPTIONS:
    -h, --help              Tampilkan menu bantuan ini
    --version, -vr          Tampilkan informasi versi tools
    -v, --verbose           Mode verbose (tampilkan proses detail)
    -s file.json            Simpan hasil ke file JSON
    -about                  Tampilkan informasi tentang tools

IP TRACKING:
    -trackip IP             Lacak informasi geolokasi IP
                            (gunakan 'myip' untuk IP sendiri)
    Contoh:
        osxnt.py -trackip 8.8.8.8
        osxnt.py -trackip myip -v -s hasil.json

WEB TRACKING:
    -webtrack {{ip,dns}}     Mode web tracking:
        ip   - Dapatkan IP address dan hostname
        dns  - Dapatkan semua DNS records (A, MX, NS, TXT, dll)
    -ip TARGET              Target untuk mode ip
    -dns TARGET             Target untuk mode dns
    Contoh:
        osxnt.py -webtrack ip -ip google.com
        osxnt.py -webtrack dns -dns facebook.com -s dns.json

PORT SCANNER:
    -scan                    Aktifkan port scanner
    -p PORTS                 Port yang di-scan (format: 80,443 atau 1-1000)
    Contoh:
        osxnt.py -scan -p 80,443,22 192.168.1.1
        osxnt.py -scan -p 1-1000 scanme.nmap.org -v -s scan.json

SUBDOMAIN ENUMERATION:
    -sbdomain                Cari subdomain dari domain target
    -use THREADS              Jumlah thread (default: 20)
    -w WORDLIST              File wordlist kustom (default: requiments/subdomain.txt)
    Contoh:
        osxnt.py -sbdomain google.com -use 50
        osxnt.py -sbdomain target.com -w mylist.txt -v -s subs.json

WEB SOURCE DOWNLOAD:
    -trackweb                Download kode sumber website (HTML, CSS, JS)
    -c CODE                   Tipe kode (html,css,js - pisah koma)
    -o OUTPUT_DIR             Direktori output (gunakan $result$ untuk nama domain)
    Contoh:
        osxnt.py -trackweb example.com -c html,css -o package/$result$ -v
        osxnt.py -trackweb @list.txt -c js -o hasil/$result$

MULTI-TARGET:
    Gunakan @file.txt pada parameter target untuk memproses banyak target dari file
    Contoh:
        osxnt.py -trackip -ft list_ip.txt
        osxnt.py -trackweb @domains.txt -c html -o output/$result$

{'='*60}
Contoh lengkap: osxnt.py -webtrack ip -ip google.com -v -s hasil.json
{'='*60}
"""
    print(help_text)

def create_parser():
    """Buat parser dengan format lama (tanpa subparser)"""
    parser = argparse.ArgumentParser(
        description="OSXNT - OSINT Toolkit",
        usage="osxnt.py [-h] [-v] [-s file.json] [-trackip IP] [-webtrack {ip,dns}] [-ip TARGET] [-dns TARGET] [-scan] [-p PORTS] [-sbdomain] [-use THREADS] [-about] [target]",
        add_help=False  # Kita handle help manual
    )
    
    # Global options
    parser.add_argument('-h', '--help', action='store_true', help='Tampilkan menu bantuan')
    parser.add_argument('--version', '-vr', action='store_true', help='Tampilkan informasi versi')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mode verbose')
    parser.add_argument('-s', metavar='file.json', help='Simpan hasil ke file JSON')
    parser.add_argument('-about', action='store_true', help='Tampilkan informasi tools')
    
    # IP tracking
    parser.add_argument('-trackip', metavar='IP', help='Lacak informasi IP (gunakan "myip" untuk IP sendiri)')
    
    # Web tracking
    parser.add_argument('-webtrack', choices=['ip', 'dns'], help='Web tracking mode: ip atau dns')
    parser.add_argument('-ip', metavar='TARGET', help='Target untuk -webtrack ip')
    parser.add_argument('-dns', metavar='TARGET', help='Target untuk -webtrack dns')
    
    # Port scanner
    parser.add_argument('-scan', action='store_true', help='Aktifkan port scanner')
    parser.add_argument('-p', metavar='PORTS', help='Ports untuk di-scan (contoh: 80,443 atau 1-1000)')
    
    # Subdomain
    parser.add_argument('-sbdomain', action='store_true', help='Aktifkan subdomain scanner')
    parser.add_argument('-use', metavar='THREADS', type=int, help='Jumlah thread untuk subdomain scan')
    parser.add_argument('-w', metavar='WORDLIST', help='File wordlist kustom')
    
    # Trackweb (download source)
    parser.add_argument('-trackweb', action='store_true', help='Download kode sumber website')
    parser.add_argument('-c', metavar='CODE', help='Tipe kode (html,css,js - pisah koma)')
    parser.add_argument('-o', metavar='OUTPUT_DIR', default='package/$result$', help='Direktori output')
    
    # Positional target (untuk scan dan subdomain)
    parser.add_argument('target', nargs='?', help='Target host/IP/domain')
    
    return parser

def main():
    # Tampilkan banner
    show_banner()
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle help
    if args.help or len(sys.argv) == 1:
        show_full_help()
        sys.exit(0)
    
    # Handle version
    if getattr(args, 'version', False) or getattr(args, 'vr', False):
        show_version()
        sys.exit(0)
    
    # Handle about
    if args.about:
        about()
        sys.exit(0)
    
    verbose = args.verbose
    save_file = args.s
    
    # ========== IP TRACK ==========
    if args.trackip:
        if args.trackip.lower() == 'myip':
            print("[*] Mendapatkan IP publik...")
            myip = iptrack.get_public_ip()
            if myip:
                print(f"[+] IP Anda: {myip}")
                iptrack.track_ip(myip, verbose, save_file)
            else:
                print("[!] Gagal mendapatkan IP publik")
        else:
            iptrack.track_ip(args.trackip, verbose, save_file)
        return
    
    # ========== WEB TRACK ==========
    if args.webtrack:
        if args.webtrack == 'ip':
            if not args.ip:
                print("[!] Gunakan -ip untuk menentukan target")
                sys.exit(1)
            track_web(args.ip, verbose, save_file)
        elif args.webtrack == 'dns':
            if not args.dns:
                print("[!] Gunakan -dns untuk menentukan target")
                sys.exit(1)
            dns.dns_lookup(args.dns, verbose=verbose, save=save_file)
        return
    
    # ========== PORT SCAN ==========
    if args.scan:
        if not args.p or not args.target:
            print("[!] Gunakan: osxnt.py -scan -p <ports> <target>")
            print("    Contoh: osxnt.py -scan -p 80,443 192.168.1.1")
            sys.exit(1)
        scanport.port_scan(args.target, args.p, verbose=verbose, save=save_file)
        return
    
    # ========== SUBDOMAIN ==========
    if args.sbdomain:
        if not args.target:
            print("[!] Masukkan domain target")
            sys.exit(1)
        wordlist = args.w if args.w else "requiments/subdomain.txt"
        threads = args.use if args.use else 20
        subdomain.subdomain_scan(args.target, wordlist, threads, verbose=verbose, save=save_file)
        return
    
    # ========== TRACKWEB (Download Source) ==========
    if args.trackweb:
        if not args.target or not args.c:
            print("[!] Gunakan: osxnt.py -trackweb <target> -c html,css,js [-o output_dir]")
            print("    Contoh: osxnt.py -trackweb example.com -c html,css -o package/$result$")
            sys.exit(1)
        
        code_types = [t.strip() for t in args.c.split(',')]
        
        # Multi-target dari file
        if args.target.startswith('@'):
            filename = args.target[1:]
            targets = read_targets_from_file(filename)
            if not targets:
                sys.exit(1)
            print(f"[+] Memproses {len(targets)} target dari {filename}")
            process_multi_targets(targets, code_types, args.o, verbose)
        else:
            process_single_target(args.target, code_types, args.o, verbose)
        return
    
    # Jika tidak ada perintah yang dikenali
    print("[!] Perintah tidak dikenal. Gunakan -h untuk melihat bantuan.")
    sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Dibatalkan oleh user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)
