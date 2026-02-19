#!/usr/bin/env python3
# OSXNT - dveloped by alzzdevmaret

import argparse
import sys
import os
from core.banner import show_banner
from core.about import about
from config.config import config
from lib.multi_target import read_targets_from_file
from modules import iptrack, dns, scanport, subdomain
from modules.webtrack import track_web, process_single_target, process_multi_targets

def main():
    # Tampilkan banner
    show_banner()

    parser = argparse.ArgumentParser(description="OSXNT - OSINT Toolkit", add_help=False)
    subparsers = parser.add_subparsers(dest='command', help='Perintah yang tersedia')

    # ----- trackip -----
    parser_trackip = subparsers.add_parser('trackip', help='Lacak informasi IP')
    parser_trackip.add_argument('target', help='IP address atau "myip"')
    parser_trackip.add_argument('-v', '--verbose', action='store_true', help='Mode verbose')
    parser_trackip.add_argument('-s', '--save', metavar='file.json', help='Simpan hasil ke JSON')

    # ----- webtrack -----
    parser_webtrack = subparsers.add_parser('webtrack', help='Web tracking (IP/DNS/WHOIS)')
    parser_webtrack.add_argument('mode', choices=['ip', 'dns'], help='Mode: ip atau dns')
    parser_webtrack.add_argument('target', help='Domain target')
    parser_webtrack.add_argument('-v', '--verbose', action='store_true')
    parser_webtrack.add_argument('-s', '--save', metavar='file.json', help='Simpan hasil ke JSON')

    # ----- scan (port scanner) -----
    parser_scan = subparsers.add_parser('scan', help='Port scanner')
    parser_scan.add_argument('target', help='Host target')
    parser_scan.add_argument('-p', '--ports', required=True, help='Ports (contoh: 80,443 atau 1-1000)')
    parser_scan.add_argument('-v', '--verbose', action='store_true')
    parser_scan.add_argument('-s', '--save', metavar='file.json', help='Simpan hasil ke JSON')

    # ----- sbdomain (subdomain) -----
    parser_sbdomain = subparsers.add_parser('sbdomain', help='Subdomain enumeration')
    parser_sbdomain.add_argument('target', help='Domain target')
    parser_sbdomain.add_argument('-u', '--use', type=int, help='Jumlah thread')
    parser_sbdomain.add_argument('-w', '--wordlist', help='File wordlist kustom')
    parser_sbdomain.add_argument('-v', '--verbose', action='store_true')
    parser_sbdomain.add_argument('-s', '--save', metavar='file.json', help='Simpan hasil ke JSON')

    # ----- trackweb (baru) -----
    parser_trackweb = subparsers.add_parser('trackweb', help='Ambil kode sumber website (HTML, CSS, JS)')
    parser_trackweb.add_argument('target', help='Target (bisa URL, domain, atau file dengan @file.txt)')
    parser_trackweb.add_argument('-c', '--code', required=True, help='Tipe kode yang diambil (pisah koma, contoh: html,css,js)')
    parser_trackweb.add_argument('-o', '--output-dir', default='package/$result$', help='Direktori output (placeholder $result$ diganti domain)')
    parser_trackweb.add_argument('-v', '--verbose', action='store_true', help='Mode verbose')

    # ----- about -----
    parser_about = subparsers.add_parser('about', help='Tampilkan informasi tools')

    # Jika tidak ada argumen, tampilkan help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # Handle about
    if args.command == 'about':
        about()
        sys.exit(0)

    # Eksekusi perintah
    if args.command == 'trackip':
        if args.target.lower() == 'myip':
            myip = iptrack.get_public_ip()
            if myip:
                iptrack.track_ip(myip, args.verbose, args.save)
            else:
                print("[!] Gagal mendapatkan IP publik sendiri")
        else:
            iptrack.track_ip(args.target, args.verbose, args.save)

    elif args.command == 'webtrack':
        if args.mode == 'ip':
            track_web(args.target, args.verbose, args.save)
        elif args.mode == 'dns':
            dns.dns_lookup(args.target, verbose=args.verbose, save=args.save)

    elif args.command == 'scan':
        scanport.port_scan(args.target, args.ports, verbose=args.verbose, save=args.save)

    elif args.command == 'sbdomain':
        wordlist = args.wordlist if args.wordlist else "requiments/subdomain.txt"
        threads = args.use if args.use else config.get('threads', 20)
        subdomain.subdomain_scan(args.target, wordlist, threads, verbose=args.verbose, save=args.save)

    elif args.command == 'trackweb':
        code_types = [t.strip() for t in args.code.split(',')]
        if args.target.startswith('@'):
            filename = args.target[1:]
            targets = read_targets_from_file(filename)
            if not targets:
                sys.exit(1)
            print(f"[+] Memproses {len(targets)} target dari {filename}")
            process_multi_targets(targets, code_types, args.output_dir, args.verbose)
        else:
            process_single_target(args.target, code_types, args.output_dir, args.verbose)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
