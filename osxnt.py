#!/usr/bin/env python3
# OSXNT - OSINT Toolkit by alzzdevmaret
# Version: 2.2.0 (with C2 Botnet Framework)

import argparse
import sys
import os
import random
from core.banner import show_banner
from core.about import about
from config.config import config
from lib.multi_target import read_targets_from_file
from modules import iptrack, dns, scanport, subdomain
from modules.webtrack import track_web, process_single_target, process_multi_targets
from modules.spam import NGLSpammer, GmailSpammer
from modules.http_analyzer import HTTPAnalyzer
from modules.ssl_analyzer import SSLAnalyzer

# Versi tools
VERSION = "2.2.0"
AUTHOR = "alzzdevmaret"
GITHUB = "https://github.com/alzzdevmaret/osxnt"

def show_version():
    """Tampilkan informasi versi"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  OSXNT Version     : {VERSION:<35} ║
║  Author            : {AUTHOR:<35} ║
║  Repository        : {GITHUB:<35} ║
║  Python            : {sys.version.split()[0]:<35} ║
║  Platform          : {sys.platform:<35} ║
║  Features          : IP Track, Web Track, Port Scan,        ║
║                      Subdomain, HTTP/SSL Analyzer,          ║
║                      Spam Modules, C2 Botnet Framework      ║
╚══════════════════════════════════════════════════════════════╝
    """.strip())

def show_full_help():
    """Tampilkan help lengkap dengan format profesional"""
    help_text = f"""
{'='*70}
{'OSXNT - OSINT TOOLKIT v' + VERSION:^70}
{'='*70}

USAGE:
    osxnt.py [-h] [-v] [-s file.json] [OPTIONS] [target]

{'='*70}
🌐 GLOBAL OPTIONS:
{'='*70}
    -h, --help              Tampilkan menu bantuan ini
    --version, -vr          Tampilkan informasi versi tools
    -v, --verbose           Mode verbose (tampilkan proses detail)
    -s file.json            Simpan hasil ke file JSON
    -about                  Tampilkan informasi tentang tools

{'='*70}
📍 IP TRACKING:
{'='*70}
    -trackip IP             Lacak informasi geolokasi IP
                            (gunakan 'myip' untuk IP sendiri)
    
    Contoh:
        osxnt.py -trackip 8.8.8.8
        osxnt.py -trackip myip -v -s hasil.json

{'='*70}
🌍 WEB TRACKING:
{'='*70}
    -webtrack {{ip,dns}}     Mode web tracking:
        ip   - Dapatkan IP address dan hostname
        dns  - Dapatkan semua DNS records (A, MX, NS, TXT, dll)
    -ip TARGET              Target untuk mode ip
    -dns TARGET             Target untuk mode dns
    
    Contoh:
        osxnt.py -webtrack ip -ip google.com
        osxnt.py -webtrack dns -dns facebook.com -s dns.json

{'='*70}
🔌 PORT SCANNER:
{'='*70}
    -scan                    Aktifkan port scanner
    -p PORTS                 Port yang di-scan (format: 80,443 atau 1-1000)
    
    Contoh:
        osxnt.py -scan -p 80,443,22 192.168.1.1
        osxnt.py -scan -p 1-1000 scanme.nmap.org -v -s scan.json

{'='*70}
🔍 SUBDOMAIN ENUMERATION:
{'='*70}
    -sbdomain                Cari subdomain dari domain target
    -use THREADS             Jumlah thread (default: 20)
    -w WORDLIST              File wordlist kustom (default: requiments/subdomain.txt)
    
    Contoh:
        osxnt.py -sbdomain google.com -use 50
        osxnt.py -sbdomain target.com -w mylist.txt -v -s subs.json

{'='*70}
📥 WEB SOURCE DOWNLOAD:
{'='*70}
    -trackweb                Download kode sumber website (HTML, CSS, JS)
    -c CODE                   Tipe kode (html,css,js - pisah koma)
    -o OUTPUT_DIR             Direktori output (gunakan $result$ untuk nama domain)
    
    Contoh:
        osxnt.py -trackweb example.com -c html,css -o package/$result$ -v
        osxnt.py -trackweb @list.txt -c js -o hasil/$result$

{'='*70}
🔬 HTTP & SSL ANALYZER:
{'='*70}
    -header URL              HTTP Header Analyzer - Analisis response headers
    
    -ssl HOST                SSL/TLS Analyzer - Analisis sertifikat SSL
    -port PORT               Port untuk SSL analyzer (default: 443)
    
    Contoh:
        osxnt.py -header https://google.com
        osxnt.py -ssl google.com -v
        osxnt.py -ssl facebook.com -port 8443 -s ssl.json

{'='*70}
📱 SPAM MODULES:
{'='*70}
    -ngl-spam USERNAME       NGL Spammer - Kirim spam ke ngl.link
    -m, --message TEXT       Pesan untuk spam
    -f, --file FILE          File berisi pesan (satu per baris)
    -n, --jumlah NUMBER      Jumlah spam (default: 10)
    -theme {{love,hate,random,scary}}  Tema pesan random
    -delay SECONDS           Delay antar pesan (default: 1)
    
    Contoh NGL Spam:
        osxnt.py -ngl-spam username123 -m "Hello" -n 50
        osxnt.py -ngl-spam target -f messages.txt -n 5

    -gmail-spam EMAIL        Gmail Spammer - SIMULASI kirim email
    -subj, --subject TEXT    Subject email
    -body TEXT               Body email
    
    Contoh Gmail Spam (Simulasi):
        osxnt.py -gmail-spam target@gmail.com -subj "Hello" -body "Test" -n 10

{'='*70}
🤖 C2 BOTNET FRAMEWORK:
{'='*70}
    -c2                      Aktifkan C2 Botnet Framework
    -startserver             Start C2 server
    
    Format:
        osxnt.py -c2 -startserver [ip] [port] [password]
        
    Contoh:
        osxnt.py -c2 -startserver                     # Interactive mode
        osxnt.py -c2 -startserver 0.0.0.0 8080 admin  # Direct mode
        osxnt.py -c2 -startserver -v                   # With verbose

{'='*70}
📌 MULTI-TARGET:
{'='*70}
    Gunakan @file.txt pada parameter target untuk memproses banyak target dari file
    
    Contoh:
        osxnt.py -trackip -ft list_ip.txt
        osxnt.py -trackweb @domains.txt -c html -o output/$result$

{'='*70}
🎯 Contoh Lengkap: osxnt.py -webtrack ip -ip google.com -v -s hasil.json
{'='*70}
"""
    print(help_text)

def create_parser():
    """Buat parser dengan format lama (tanpa subparser)"""
    parser = argparse.ArgumentParser(
        description="OSXNT - OSINT Toolkit",
        usage="osxnt.py [-h] [-v] [-s file.json] [OPTIONS] [target]",
        add_help=False
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
    
    # HTTP & SSL Analyzer
    parser.add_argument('-header', metavar='URL', help='HTTP Header Analyzer - Analisis HTTP response headers')
    parser.add_argument('-ssl', metavar='HOST', help='SSL/TLS Analyzer - Analisis sertifikat SSL')
    parser.add_argument('-port', type=int, default=443, help='Port untuk SSL analyzer (default: 443)')
    
    # NGL Spam
    parser.add_argument('-ngl-spam', metavar='USERNAME', help='NGL Spammer - Kirim spam ke ngl.link')
    parser.add_argument('-m', '--message', help='Pesan untuk spam')
    parser.add_argument('-f', '--file', help='File berisi pesan (satu per baris)')
    parser.add_argument('-n', '--jumlah', type=int, default=10, help='Jumlah spam (default: 10)')
    parser.add_argument('-theme', choices=['love', 'hate', 'random', 'scary'], help='Tema pesan random')
    parser.add_argument('-delay', type=float, default=1, help='Delay antar pesan (detik)')
    
    # Gmail Spam (Simulasi)
    parser.add_argument('-gmail-spam', metavar='EMAIL', help='Gmail Spammer - SIMULASI kirim email')
    parser.add_argument('-subj', '--subject', help='Subject email')
    parser.add_argument('-body', help='Body email')
    
    # C2 Botnet Framework
    parser.add_argument('-c2', action='store_true', help='C2 Botnet Framework')
    parser.add_argument('-startserver', action='store_true', help='Start C2 server')
    
    # Positional target (untuk scan, subdomain, dll)
    parser.add_argument('target', nargs='?', help='Target host/IP/domain')
    
    # Additional arguments untuk C2
    parser.add_argument('ip', nargs='?', help='IP address untuk C2 server')
    parser.add_argument('port', nargs='?', help='Port untuk C2 server')
    parser.add_argument('password', nargs='?', help='Password untuk C2 server')
    
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
    
    # ========== C2 BOTNET FRAMEWORK ==========
    if args.c2 and args.startserver:
        try:
            from modules.c2 import C2Server, C2Monitor, C2UI
            
            print("\n" + "="*60)
            print("🤖 OSXNT C2 BOTNET FRAMEWORK")
            print("="*60)
            
            # Parse parameters
            if args.ip and args.port and args.password:
                # Direct mode
                ip = args.ip
                port = int(args.port)
                password = args.password
            else:
                # Interactive mode
                ip = input("Enter IP address [0.0.0.0]: ") or "0.0.0.0"
                port_input = input("Enter port [8080]: ") or "8080"
                port = int(port_input)
                password = input("Enter password [osxnt]: ") or "osxnt"
            
            print(f"\n[+] Starting C2 server on {ip}:{port}")
            
            # Start server
            server = C2Server(ip=ip, port=port, password=password, verbose=verbose)
            if server.start():
                monitor = C2Monitor(server)
                ui = C2UI(server, monitor)
                ui.start()
            else:
                print("[!] Failed to start C2 server")
                
        except ImportError as e:
            print(f"[!] C2 modules not available: {e}")
            print("    Make sure modules/c2/ directory exists with required files")
        except Exception as e:
            print(f"[!] C2 server error: {e}")
        
        return
    
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
    
    # ========== HTTP HEADER ANALYZER ==========
    if args.header:
        analyzer = HTTPAnalyzer(verbose=verbose)
        analyzer.analyze(args.header, save=save_file)
        return
    
    # ========== SSL/TLS ANALYZER ==========
    if args.ssl:
        analyzer = SSLAnalyzer(verbose=verbose)
        analyzer.analyze(args.ssl, args.port, save=save_file)
        return
    
    # ========== NGL SPAM ==========
    if args.ngl_spam:
        username = args.ngl_spam
        spammer = NGLSpammer(username, verbose)
        
        # Header
        print("\n" + "="*50)
        print(f"📱 NGL SPAMMER - Target: @{username}")
        print("="*50)
        
        jumlah = args.jumlah if args.jumlah else 10
        
        # File mode
        if args.file:
            spammer.spam_from_file(args.file, jumlah, args.delay)
        
        # Random theme mode
        elif args.theme:
            spammer.random_spam(args.theme, jumlah, args.delay)
        
        # Single message mode
        elif args.message:
            spammer.spam(args.message, jumlah, args.delay)
        
        else:
            print("[!] Tentukan pesan dengan -m (single), -f (file), atau -theme (random)")
            print("    Contoh: osxnt.py -ngl-spam user -m 'Hello' -n 50")
            print("            osxnt.py -ngl-spam user -f messages.txt -n 5")
            print("            osxnt.py -ngl-spam user -theme love -n 100")
        
        return
    
    # ========== GMAIL SPAM (SIMULASI) ==========
    if args.gmail_spam:
        email = args.gmail_spam
        spammer = GmailSpammer(verbose)
        
        print("\n" + "="*50)
        print(f"📧 GMAIL SPAMMER (SIMULASI) - Target: {email}")
        print("="*50)
        
        if not args.subject or not args.body:
            print("[!] Gunakan -subj untuk subject dan -body untuk isi email")
            print("    Contoh: osxnt.py -gmail-spam target@gmail.com -subj 'Hello' -body 'Test' -n 10")
            sys.exit(1)
        
        jumlah = args.jumlah if args.jumlah else 10
        spammer.spam(email, args.subject, args.body, jumlah, args.delay)
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
