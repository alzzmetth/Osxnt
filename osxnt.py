#!/usr/bin/env python3
# OSXNT - OSINT Toolkit by alzzdevmaret
# Version: 2.4.0 (with Darkweb Upgraded)

import argparse
import sys
import os
from core.banner import show_banner
from core.about import about
from config.config import config

# Import semua lib yang sudah diupgrade
from lib.multi_target import read_targets_from_file, sanitize_filename
from lib.json_save import save_to_json, prepare_output
from lib.verbose import Verbose
from lib.csv_save import save_to_csv, append_to_csv, dict_to_csv
from lib.txt_save import save_to_txt, append_to_txt, save_results
from lib.file_helper import ensure_dir, get_unique_filename, list_files, delete_file, get_file_size, read_file
from lib.validator import is_valid_ip, is_valid_domain, is_valid_url, is_valid_email, is_valid_port, validate_input
from lib.converter import json_to_csv, dict_to_txt, size_to_human, timestamp_to_date
from lib.timer import Timer, measure_time

# Import modules (tanpa http/ssl)
from modules import iptrack, dns, scanport, subdomain
from modules.webtrack import track_web, process_single_target, process_multi_targets
from modules.spam import NGLSpammer, GmailSpammer
from modules.email_harvester import EmailHarvester
from modules.url_extractor import URLExtractor, URLChecker
from modules.c2 import C2Server, C2Monitor, C2UI

# Import hash & bruteforce modules
from modules.hash import HashGenerator, HashChecker, Encoder, Decoder
from modules.bruteforce import BruteForceEngine, HashCracker, MD5Cracker, SHA256Cracker, SHA1Cracker, WordlistManager

# Import darkweb upgraded modules
from modules.darkweb import DarkWebDeployer, Config as DarkConfig, DarkWebAuth, DarkWebMonitor, DarkWebUI

# Versi tools
VERSION = "2.4.0"
AUTHOR = "alzzdevmaret"
GITHUB = "https://github.com/alzzdevmaret/osxnt"

def show_version():
    """Tampilkan informasi versi dengan lib baru"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║  OSXNT Version     : {VERSION:<35} ║
║  Author            : {AUTHOR:<35} ║
║  Repository        : {GITHUB:<35} ║
║  Python            : {sys.version.split()[0]:<35} ║
║  Platform          : {sys.platform:<35} ║
║  Lib Version       : 1.1.0 (CSV, TXT, Validator, Timer)    ║
║  Features          : IP Track, Web Track, Port Scan,       ║
║                      Subdomain, Email Harvester,           ║
║                      URL Tools, C2 Framework,              ║
║                      Dark Web (Upgraded), HASH,            ║
║                      Encode/Decode, Bruteforce             ║
╚══════════════════════════════════════════════════════════════╝
    """.strip())

def show_full_help():
    """Tampilkan help lengkap dengan semua fitur baru"""
    help_text = f"""
{'='*70}
{'OSXNT - OSINT TOOLKIT v' + VERSION:^70}
{'='*70}

USAGE:
    osxnt.py [-h] [-v] [-s file.json] [--csv file.csv] [--txt file.txt] [OPTIONS] [target]

{'='*70}
🌐 GLOBAL OPTIONS:
{'='*70}
    -h, --help              Tampilkan menu bantuan ini
    --version, -vr          Tampilkan informasi versi tools
    -v, --verbose           Mode verbose (tampilkan proses detail)
    -vv                     Double verbose (lebih detail)
    -s file.json            Simpan hasil ke file JSON
    --csv file.csv          Simpan hasil ke file CSV
    --txt file.txt          Simpan hasil ke file TXT
    --auto-save             Auto save dengan timestamp
    -about                  Tampilkan informasi tentang tools
    --timeout SECONDS       Set timeout (default: 30)

{'='*70}
📍 IP TRACKING:
{'='*70}
    -trackip IP             Lacak informasi geolokasi IP
    ip IP                   Shortcut untuk -trackip
    
    Contoh:
        osxnt.py ip 8.8.8.8
        osxnt.py -trackip myip -v --csv hasil.csv

{'='*70}
🌍 WEB TRACKING:
{'='*70}
    -webtrack {{ip,dns}}     Mode web tracking
    web TARGET              Shortcut untuk -webtrack ip
    dns TARGET              Shortcut untuk -webtrack dns
    
    Contoh:
        osxnt.py web google.com
        osxnt.py dns facebook.com --csv dns.csv

{'='*70}
🔌 PORT SCANNER:
{'='*70}
    -scan                    Aktifkan port scanner
    -p PORTS                 Port yang di-scan
    scan TARGET -p PORTS     Shortcut format
    
    Contoh:
        osxnt.py scan 192.168.1.1 -p 80,443
        osxnt.py -scan -p 1-1000 target.com --csv ports.csv

{'='*70}
🔍 SUBDOMAIN ENUMERATION:
{'='*70}
    -sbdomain                Cari subdomain
    sub TARGET              Shortcut untuk -sbdomain
    -t, --threads THREADS    Jumlah thread
    
    Contoh:
        osxnt.py sub target.com -t 50
        osxnt.py -sbdomain google.com -w wordlist.txt --csv subs.csv

{'='*70}
📧 EMAIL HARVESTER:
{'='*70}
    -email -scrap TARGET     Harvest email dari website
    -depth LEVEL             Kedalaman crawling
    
    Contoh:
        osxnt.py -email -scrap target.com -depth 3
        osxnt.py -email -scrap @list.txt --csv emails.csv

{'='*70}
🔗 URL EXTRACTOR:
{'='*70}
    -urlextract TARGET       Extract semua URL
    -urlcheck -resource TARGET Check resources
    
    Contoh:
        osxnt.py -urlextract target.com
        osxnt.py -urlcheck -resource example.com --type images

{'='*70}
🌑 DARK WEB DEPLOYER (UPGRADED):
{'='*70}
    -darkweb -create NAME    Create hidden service
    -darkweb -start NAME     Start service
    -darkweb -stop NAME      Stop service
    -darkweb -restart NAME   Restart service
    -darkweb -list           List all services
    -darkweb -status NAME    Check service status
    -darkweb -logs NAME      Show service logs
    -darkweb -dashboard      Show dashboard
    -darkweb -ui             Interactive UI
    -darkweb -auth NAME      Setup authentication
    --port PORT              Port for service
    --user USER              Username for auth
    --pass PASS              Password for auth
    
    Contoh:
        osxnt.py -darkweb -create --name mysite --port 8080
        osxnt.py -darkweb -start mysite
        osxnt.py -darkweb -dashboard
        osxnt.py -darkweb -auth mysite --user admin --pass secret

{'='*70}
🤖 C2 FRAMEWORK:
{'='*70}
    -c2 -startserver         Start C2 server
    -c2 -client              Connect sebagai client
    
    Contoh:
        osxnt.py -c2 -startserver 0.0.0.0 8080 admin

{'='*70}
🔐 HASH MODULE:
{'='*70}
    -hash --text TEXT        Generate hash dari text
    -hash --file FILE        Generate hash dari file
    --algorithm ALGO         Algorithm (md5,sha1,sha256,sha512)
    --verify HASH            Verify hash
    --find HASH --dir DIR    Find file by hash
    
    Contoh:
        osxnt.py -hash --text "password" --algorithm md5
        osxnt.py -hash --file document.pdf --algorithm sha256
        osxnt.py -hash --text "pass" --verify 5f4dcc3b5aa7

{'='*70}
🔄 ENCODE/DECODE:
{'='*70}
    -encode --type TYPE      Encode text
    -decode --type TYPE      Decode text
    --type TYPE              base64, base32, base16, rot13, url, auto
    
    Contoh:
        osxnt.py -encode --type base64 --text "secret"
        osxnt.py -decode --type auto --text "c2VjcmV0"

{'='*70}
🔓 BRUTEFORCE CRACKER:
{'='*70}
    -crack --hash HASH       Crack hash
    --method METHOD          wordlist, bruteforce, hybrid, auto
    --wordlist NAME          Wordlist to use
    --min-len LEN            Minimum length
    --max-len LEN            Maximum length
    
    Contoh:
        osxnt.py -crack --hash 5f4dcc3b5aa7 --method wordlist
        osxnt.py -crack --hash e3ceb5881a0a --method bruteforce --max-len 4

{'='*70}
📚 WORDLIST MANAGER:
{'='*70}
    -wordlist --list         List available wordlists
    -wordlist --download NAME Download wordlist
    -wordlist --create FILE  Create custom wordlist
    --words "word1,word2"    Words for custom wordlist
    
    Contoh:
        osxnt.py -wordlist --list
        osxnt.py -wordlist --download rockyou
        osxnt.py -wordlist --create mylist.txt --words "pass,admin,123"

{'='*70}
📌 MULTI-TARGET & OUTPUT:
{'='*70}
    Gunakan @file.txt untuk multi-target
    --csv file.csv           Export ke CSV
    --txt file.txt           Export ke TXT
    --auto-save              Auto save dengan timestamp
    
    Contoh:
        osxnt.py ip @list.txt --csv results.csv
        osxnt.py sub @domains.txt --txt subs.txt --auto-save

{'='*70}
🎯 Shortcuts:
    ip = -trackip
    web = -webtrack ip
    dns = -webtrack dns
    scan = -scan
    sub = -sbdomain
{'='*70}
"""
    print(help_text)

def create_parser():
    """Buat parser dengan semua fitur baru"""
    parser = argparse.ArgumentParser(
        description="OSXNT - OSINT Toolkit",
        usage="osxnt.py [-h] [-v] [-s file.json] [--csv file.csv] [--txt file.txt] [OPTIONS] [target]",
        add_help=False
    )
    
    # ===== GLOBAL OPTIONS =====
    parser.add_argument('-h', '--help', action='store_true', help='Tampilkan menu bantuan')
    parser.add_argument('--version', '-vr', action='store_true', help='Tampilkan informasi versi')
    parser.add_argument('-v', '--verbose', action='store_true', help='Mode verbose')
    parser.add_argument('-vv', action='store_true', help='Double verbose mode')
    parser.add_argument('-s', metavar='file.json', help='Simpan hasil ke file JSON')
    parser.add_argument('--csv', metavar='file.csv', help='Simpan hasil ke file CSV')
    parser.add_argument('--txt', metavar='file.txt', help='Simpan hasil ke file TXT')
    parser.add_argument('--auto-save', action='store_true', help='Auto save dengan timestamp')
    parser.add_argument('-about', action='store_true', help='Tampilkan informasi tools')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout dalam detik')
    
    # ===== SHORTCUTS =====
    parser.add_argument('ip', nargs='?', help='Shortcut untuk -trackip')
    parser.add_argument('web', nargs='?', help='Shortcut untuk -webtrack ip')
    parser.add_argument('dns', nargs='?', help='Shortcut untuk -webtrack dns')
    parser.add_argument('scan', nargs='?', help='Shortcut untuk -scan')
    parser.add_argument('sub', nargs='?', help='Shortcut untuk -sbdomain')
    
    # ===== IP TRACKING =====
    parser.add_argument('-trackip', metavar='IP', help='Lacak informasi IP')
    
    # ===== WEB TRACKING =====
    parser.add_argument('-webtrack', choices=['ip', 'dns'], help='Web tracking mode')
    parser.add_argument('-ip', metavar='TARGET', help='Target untuk -webtrack ip')
    parser.add_argument('-dns', metavar='TARGET', help='Target untuk -webtrack dns')
    
    # ===== PORT SCANNER =====
    parser.add_argument('-scan', action='store_true', help='Aktifkan port scanner')
    parser.add_argument('-p', metavar='PORTS', help='Ports untuk di-scan')
    
    # ===== SUBDOMAIN =====
    parser.add_argument('-sbdomain', action='store_true', help='Aktifkan subdomain scanner')
    parser.add_argument('-t', '--threads', metavar='THREADS', type=int, help='Jumlah thread')
    parser.add_argument('-w', metavar='WORDLIST', help='File wordlist kustom')
    
    # ===== TRACKWEB =====
    parser.add_argument('-trackweb', action='store_true', help='Download kode sumber website')
    parser.add_argument('-c', metavar='CODE', help='Tipe kode (html,css,js)')
    parser.add_argument('-o', metavar='OUTPUT_DIR', default='package/$result$', help='Direktori output')
    
    # ===== EMAIL HARVESTER =====
    parser.add_argument('-email', action='store_true', help='Email Harvester')
    parser.add_argument('-scrap', metavar='TARGET', help='Target untuk email harvester')
    parser.add_argument('-depth', type=int, default=2, help='Kedalaman crawling')
    
    # ===== URL EXTRACTOR =====
    parser.add_argument('-urlextract', metavar='TARGET', help='URL Extractor')
    parser.add_argument('-urlcheck', action='store_true', help='URL Checker')
    parser.add_argument('-resource', metavar='TARGET', help='Target untuk URL checker')
    parser.add_argument('-type', choices=['all', 'images', 'scripts', 'styles', 'links'], 
                       default='all', help='Tipe resource')
    
    # ===== SPAM MODULES =====
    parser.add_argument('-ngl-spam', metavar='USERNAME', help='NGL Spammer')
    parser.add_argument('-m', '--message', help='Pesan untuk spam')
    parser.add_argument('-f', '--file', help='File berisi pesan')
    parser.add_argument('-n', '--jumlah', type=int, default=10, help='Jumlah spam')
    parser.add_argument('-theme', choices=['love', 'hate', 'random', 'scary'], help='Tema pesan')
    parser.add_argument('-delay', type=float, default=1, help='Delay antar pesan')
    
    parser.add_argument('-gmail-spam', metavar='EMAIL', help='Gmail Spammer (simulasi)')
    parser.add_argument('-subj', '--subject', help='Subject email')
    parser.add_argument('-body', help='Body email')
    
    # ===== C2 FRAMEWORK =====
    parser.add_argument('-c2', action='store_true', help='C2 Botnet Framework')
    parser.add_argument('-startserver', action='store_true', help='Start C2 server')
    parser.add_argument('-client', action='store_true', help='Connect sebagai client')
    parser.add_argument('--server', help='Server address untuk client')
    parser.add_argument('--pass', dest='c2pass', help='Password untuk C2')
    
    # ===== DARK WEB UPGRADED =====
    parser.add_argument('-darkweb', action='store_true', help='Dark web control')
    parser.add_argument('-create', action='store_true', help='Create hidden service')
    parser.add_argument('-start', action='store_true', help='Start service')
    parser.add_argument('-stop', action='store_true', help='Stop service')
    parser.add_argument('-restart', action='store_true', help='Restart service')
    parser.add_argument('-list', action='store_true', help='List all services')
    parser.add_argument('-status', action='store_true', help='Show status')
    parser.add_argument('-logs', action='store_true', help='Show logs')
    parser.add_argument('-dashboard', action='store_true', help='Show dashboard')
    parser.add_argument('-ui', action='store_true', help='Interactive UI')
    parser.add_argument('-auth', action='store_true', help='Setup authentication')
    parser.add_argument('--name', help='Service name')
    parser.add_argument('--port', type=int, default=8080, help='Port for service')
    parser.add_argument('--user', help='Username for auth')
    parser.add_argument('--passwd', help='Password for auth')
    
    # ===== HASH MODULE =====
    parser.add_argument('-hash', action='store_true', help='Hash generator')
    parser.add_argument('--text', help='Text to hash')
    parser.add_argument('--file', help='File to hash')
    parser.add_argument('--algorithm', choices=['md5', 'sha1', 'sha256', 'sha512', 'blake2b'], 
                       default='md5', help='Hash algorithm')
    parser.add_argument('--verify', help='Verify hash')
    parser.add_argument('--find', help='Find file by hash')
    parser.add_argument('--dir', help='Directory for find operation')
    
    # ===== ENCODE/DECODE =====
    parser.add_argument('-encode', action='store_true', help='Encode text')
    parser.add_argument('-decode', action='store_true', help='Decode text')
    parser.add_argument('--type', choices=['base64', 'base32', 'base16', 'base85', 'rot13', 'url', 'auto'],
                       default='base64', help='Encoding type')
    
    # ===== BRUTEFORCE =====
    parser.add_argument('-crack', action='store_true', help='Crack hash')
    parser.add_argument('--hash', help='Target hash to crack')
    parser.add_argument('--method', choices=['wordlist', 'bruteforce', 'hybrid', 'auto'],
                       default='auto', help='Cracking method')
    parser.add_argument('--wordlist', help='Wordlist name')
    parser.add_argument('--min-len', type=int, default=1, help='Minimum length')
    parser.add_argument('--max-len', type=int, default=6, help='Maximum length')
    
    # ===== WORDLIST MANAGER =====
    parser.add_argument('-wordlist', action='store_true', help='Manage wordlists')
    parser.add_argument('--list-wl', action='store_true', help='List available wordlists')
    parser.add_argument('--download', help='Download wordlist')
    parser.add_argument('--create-wl', help='Create custom wordlist')
    parser.add_argument('--words', help='Words for custom wordlist (comma separated)')
    
    # Positional target
    parser.add_argument('target', nargs='?', help='Target host/IP/domain')
    
    return parser

def main():
    # Timer untuk seluruh eksekusi
    with Timer("Total execution"):
        # Tampilkan banner
        show_banner()
        
        parser = create_parser()
        args = parser.parse_args()
        
        # Setup verbose
        verbose = args.verbose or args.vv
        double_verbose = args.vv
        
        # Setup output files
        save_file = args.s
        csv_file = args.csv
        txt_file = args.txt
        
        # Auto-save dengan timestamp
        if args.auto_save:
            from datetime import datetime
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if not save_file:
                save_file = f"osxnt_{timestamp}.json"
            if not csv_file and args.csv is None:
                csv_file = f"osxnt_{timestamp}.csv"
            if not txt_file and args.txt is None:
                txt_file = f"osxnt_{timestamp}.txt"
        
        # ===== HANDLE HELP =====
        if args.help or len(sys.argv) == 1:
            show_full_help()
            sys.exit(0)
        
        # ===== HANDLE VERSION =====
        if getattr(args, 'version', False) or getattr(args, 'vr', False):
            show_version()
            sys.exit(0)
        
        # ===== HANDLE ABOUT =====
        if args.about:
            about()
            sys.exit(0)
        
        # ===== SHORTCUT HANDLERS =====
        if args.ip and not any([args.trackip, args.webtrack, args.scan, args.sbdomain]):
            args.trackip = args.ip
        
        if args.web and not args.webtrack:
            args.webtrack = 'ip'
            args.ip = args.web
        
        if args.dns and not args.webtrack:
            args.webtrack = 'dns'
            args.dns = args.dns
        
        if args.scan and not args.scan:
            args.scan = True
            if args.scan != True:
                args.target = args.scan
        
        if args.sub and not args.sbdomain:
            args.sbdomain = True
            args.target = args.sub
        
        # ===== WORDLIST MANAGER =====
        if args.wordlist:
            wm = WordlistManager(verbose=verbose)
            
            if args.list_wl:
                wm.list_available()
            
            elif args.download:
                wm.download(args.download)
            
            elif args.create_wl:
                if args.words:
                    words = [w.strip() for w in args.words.split(',')]
                    wm.create_custom(args.create_wl, words)
                else:
                    print("[!] Gunakan --words untuk daftar kata")
            
            return
        
        # ===== HASH MODULE =====
        if args.hash:
            generator = HashGenerator(verbose)
            checker = HashChecker(verbose)
            
            if args.text:
                if args.verify:
                    result = checker.verify_string(args.text, args.verify, args.algorithm)
                    if result:
                        print("[✓] Hash matches!")
                    else:
                        print("[✗] Hash does not match")
                else:
                    result = generator.hash_string(args.text, args.algorithm)
                    if result:
                        print(f"\n[{args.algorithm.upper()} Hash]")
                        print(result)
                        if txt_file:
                            save_to_txt(f"{args.algorithm}: {result}", txt_file)
            
            elif args.file:
                result = generator.hash_file(args.file, args.algorithm)
                if result:
                    print(f"\n[{args.algorithm.upper()} Hash of {args.file}]")
                    print(result)
                    if txt_file:
                        save_to_txt(f"{args.file}: {result}", txt_file)
            
            elif args.find and args.dir:
                result = checker.find_matching_file(args.dir, args.find, args.algorithm)
                if result:
                    print(f"\n[✓] Found: {result}")
            
            return
        
        # ===== ENCODE/DECODE MODULE =====
        if args.encode and args.text:
            encoder = Encoder(verbose)
            
            if args.type == 'base64':
                result = encoder.base64_encode(args.text)
            elif args.type == 'base32':
                result = encoder.base32_encode(args.text)
            elif args.type == 'base16':
                result = encoder.base16_encode(args.text)
            elif args.type == 'base85':
                result = encoder.base85_encode(args.text)
            elif args.type == 'rot13':
                result = encoder.rot13_encode(args.text)
            elif args.type == 'url':
                result = encoder.url_encode(args.text)
            
            if result:
                print(f"\n[{args.type.upper()} Encoded]")
                print(result)
                if txt_file:
                    save_to_txt(result, txt_file)
            
            return
        
        if args.decode and args.text:
            decoder = Decoder(verbose)
            
            if args.type == 'auto':
                results = decoder.auto_decode(args.text)
                if results:
                    print("\n[Possible Decodings]")
                    for method, decoded in results.items():
                        print(f"  {method}: {decoded}")
                        if txt_file:
                            save_to_txt(f"{method}: {decoded}", txt_file, 'a')
            else:
                if args.type == 'base64':
                    result = decoder.base64_decode(args.text)
                elif args.type == 'base32':
                    result = decoder.base32_decode(args.text)
                elif args.type == 'base16':
                    result = decoder.base16_decode(args.text)
                elif args.type == 'base85':
                    result = decoder.base85_decode(args.text)
                elif args.type == 'rot13':
                    result = decoder.rot13_decode(args.text)
                elif args.type == 'url':
                    result = decoder.url_decode(args.text)
                
                if result:
                    print(f"\n[{args.type.upper()} Decoded]")
                    print(result)
                    if txt_file:
                        save_to_txt(result, txt_file)
            
            return
        
        # ===== BRUTEFORCE CRACKER =====
        if args.crack and args.hash:
            # Auto detect algorithm based on hash length
            hash_len = len(args.hash)
            cracker = None
            
            if hash_len == 32:
                cracker = MD5Cracker(verbose)
                algo = "MD5"
            elif hash_len == 40:
                cracker = SHA1Cracker(verbose)
                algo = "SHA1"
            elif hash_len == 64:
                cracker = SHA256Cracker(verbose)
                algo = "SHA256"
            else:
                # Default ke HashCracker dengan algoritma manual
                cracker = HashCracker(verbose)
                algo = "Unknown"
                print(f"[!] Hash length {hash_len} not recognized, using generic cracker")
            
            if cracker:
                result = cracker.crack(
                    args.hash,
                    method=args.method,
                    wordlist=args.wordlist or 'rockyou'
                )
                
                if result:
                    print(f"\n[✓] {algo} Password found: {result}")
                    if txt_file:
                        save_to_txt(f"Hash: {args.hash}\nPassword: {result}", txt_file)
                else:
                    print(f"\n[✗] {algo} Password not found")
            
            return
        
        # ===== DARK WEB UPGRADED =====
        if args.darkweb:
            # Initialize darkweb components
            dark_config = DarkConfig()
            dark_monitor = DarkWebMonitor(dark_config)
            dark_ui = DarkWebUI(dark_config, dark_monitor)
            
            if args.create and args.name:
                deployer = DarkWebDeployer(dark_config)
                deployer.create_service(args.name, args.port)
            
            elif args.start and args.name:
                deployer = DarkWebDeployer(dark_config)
                deployer.start_service(args.name)
            
            elif args.stop and args.name:
                deployer = DarkWebDeployer(dark_config)
                deployer.stop_service(args.name)
            
            elif args.restart and args.name:
                deployer = DarkWebDeployer(dark_config)
                deployer.restart_service(args.name)
            
            elif args.list:
                dark_ui.quick_status()
            
            elif args.status and args.name:
                svc = dark_config.get_service(args.name)
                if svc:
                    dark_ui.show_service_summary(args.name, svc)
                else:
                    print(f"[!] Service {args.name} not found")
            
            elif args.logs and args.name:
                # Simple log display
                print(f"[*] Logs for {args.name} (not implemented in this version)")
            
            elif args.dashboard:
                dark_ui.show_dashboard()
            
            elif args.ui:
                dark_ui.interactive_menu()
            
            elif args.auth and args.name and args.user and args.passwd:
                auth = DarkWebAuth(dark_config)
                auth.add_user(args.user, args.passwd)
                print(f"[✓] Authentication setup for {args.name}")
            
            else:
                print("[!] Gunakan: -create, -start, -stop, -list, -dashboard, -ui, dll")
                print("    Contoh: osxnt.py -darkweb -create --name mysite --port 8080")
            
            return
        
        # ===== IP TRACKING =====
        if args.trackip:
            with Timer("IP Tracking"):
                if args.trackip.lower() == 'myip':
                    print("[*] Mendapatkan IP publik...")
                    myip = iptrack.get_public_ip()
                    if myip:
                        print(f"[+] IP Anda: {myip}")
                        result = iptrack.track_ip(myip, verbose)
                    else:
                        print("[!] Gagal mendapatkan IP publik")
                        return
                else:
                    # Validasi IP
                    if not is_valid_ip(args.trackip) and not is_valid_domain(args.trackip):
                        print("[!] Invalid IP or domain format")
                        return
                    
                    result = iptrack.track_ip(args.trackip, verbose)
                
                # Save results
                if result:
                    if save_file:
                        save_to_json(prepare_output(result, args.trackip, "iptrack"), save_file)
                    if csv_file:
                        if isinstance(result, dict):
                            save_to_csv([result], csv_file)
                    if txt_file:
                        save_results(result, txt_file, f"IP Track: {args.trackip}")
            
            return
        
        # ===== WEB TRACKING =====
        if args.webtrack:
            with Timer("Web Tracking"):
                if args.webtrack == 'ip':
                    if not args.ip:
                        print("[!] Gunakan -ip untuk menentukan target")
                        return
                    result = track_web(args.ip, verbose)
                elif args.webtrack == 'dns':
                    if not args.dns:
                        print("[!] Gunakan -dns untuk menentukan target")
                        return
                    result = dns.dns_lookup(args.dns, verbose=verbose)
                
                # Save results
                if result:
                    if save_file:
                        save_to_json(prepare_output(result, args.ip or args.dns, "webtrack"), save_file)
                    if csv_file and isinstance(result, dict):
                        save_to_csv([result], csv_file)
                    if txt_file:
                        save_results(result, txt_file, f"Web Track: {args.ip or args.dns}")
            
            return
        
        # ===== PORT SCANNER =====
        if args.scan:
            if not args.p or not args.target:
                print("[!] Gunakan: osxnt.py -scan -p <ports> <target>")
                return
            
            with Timer("Port Scan"):
                result = scanport.port_scan(args.target, args.p, verbose=verbose)
                
                if result and csv_file:
                    save_to_csv(result, csv_file)
                if result and txt_file:
                    save_results(result, txt_file, f"Port Scan: {args.target}")
            
            return
        
        # ===== SUBDOMAIN SCANNER =====
        if args.sbdomain:
            if not args.target:
                print("[!] Masukkan domain target")
                return
            
            wordlist = args.w if args.w else "requiments/subdomain.txt"
            threads = args.threads if args.threads else 20
            
            # Validasi domain
            if not is_valid_domain(args.target):
                print("[!] Invalid domain format")
                return
            
            with Timer("Subdomain Scan"):
                result = subdomain.subdomain_scan(args.target, wordlist, threads, verbose=verbose)
                
                if result and csv_file:
                    save_to_csv(result, csv_file)
                if result and txt_file:
                    save_results(result, txt_file, f"Subdomains: {args.target}")
            
            return
        
        # ===== EMAIL HARVESTER =====
        if args.email and args.scrap:
            harvester = EmailHarvester(verbose=verbose)
            
            # Multi-target dari file
            if args.scrap.startswith('@'):
                filename = args.scrap[1:]
                targets = read_targets_from_file(filename)
                if not targets:
                    return
                
                print(f"[+] Memproses {len(targets)} target")
                all_results = []
                
                for target in targets:
                    if is_valid_domain(target) or is_valid_url(target):
                        result = harvester.harvest(target, depth=args.depth)
                        if result:
                            all_results.append(result)
                
                if all_results and csv_file:
                    # Flatten untuk CSV
                    flat_results = []
                    for res in all_results:
                        for email in res.get('emails', []):
                            flat_results.append(email)
                    save_to_csv(flat_results, csv_file)
                
            else:
                result = harvester.harvest(args.scrap, depth=args.depth)
                
                if result and csv_file:
                    save_to_csv(result.get('emails', []), csv_file)
                if result and txt_file:
                    save_results(result, txt_file, f"Emails from {args.scrap}")
            
            return
        
        # ===== URL EXTRACTOR =====
        if args.urlextract:
            extractor = URLExtractor(verbose=verbose)
            result = extractor.extract(args.urlextract, depth=args.depth)
            
            if result and csv_file:
                # Flatten URLs
                all_urls = []
                for cat, urls in result.get('categories', {}).items():
                    for url in urls:
                        all_urls.append({'category': cat, 'url': url if isinstance(url, str) else url.get('url', '')})
                save_to_csv(all_urls, csv_file)
            
            return
        
        # ===== URL CHECKER =====
        if args.urlcheck and args.resource:
            checker = URLChecker(verbose=verbose)
            result = checker.check(args.resource, resource_type=args.type)
            
            if result and csv_file:
                # Flatten broken links
                broken = []
                for res_type, resources in result.get('resources', {}).items():
                    for res in resources:
                        if res.get('status') != 'OK':
                            broken.append({
                                'type': res_type,
                                'url': res.get('url', ''),
                                'status': res.get('status', 'Unknown')
                            })
                save_to_csv(broken, csv_file)
            
            return
        
        # ===== C2 FRAMEWORK =====
        if args.c2 and args.startserver:
            # Parse parameters
            ip = args.target if args.target else input("IP [0.0.0.0]: ") or "0.0.0.0"
            port = args.port if hasattr(args, 'port') else int(input("Port [8080]: ") or "8080")
            password = args.c2pass if args.c2pass else input("Password [osxnt]: ") or "osxnt"
            
            server = C2Server(ip=ip, port=port, password=password, verbose=verbose)
            if server.start():
                monitor = C2Monitor(server)
                ui = C2UI(server, monitor)
                ui.start()
            
            return
        
        # ===== JIKA TIDAK ADA PERINTAH =====
        print("[!] Perintah tidak dikenal. Gunakan -h untuk melihat bantuan.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Dibatalkan oleh user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Error: {e}")
        sys.exit(1)
