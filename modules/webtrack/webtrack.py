#!/usr/bin/env python3
# OSXNT - Web Tracking Module (IP, DNS, WHOIS)

import socket
import dns.resolver
import whois
from urllib.parse import urlparse
from lib.verbose import Verbose
from lib.json_save import save_to_json, prepare_output

def extract_domain(url):
    """Extract domain from URL"""
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    if ':' in domain:
        domain = domain.split(':')[0]
    return domain

def get_ip_from_domain(domain, verbose=False):
    """Dapatkan IP address dari domain"""
    v = Verbose(verbose)
    v.log(f"Resolving domain: {domain}")
    try:
        ips = []
        addrinfo = socket.getaddrinfo(domain, 80)
        for addr in addrinfo:
            ip = addr[4][0]
            if ip not in ips:
                ips.append(ip)
        return ips
    except socket.gaierror as e:
        v.error(f"Gagal resolve domain: {e}")
        return []
    except Exception as e:
        v.error(f"Error: {e}")
        return []

def get_hostname_from_ip(ip, verbose=False):
    """Reverse DNS lookup"""
    v = Verbose(verbose)
    v.log(f"Reverse DNS untuk IP: {ip}")
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except socket.herror:
        return None
    except Exception as e:
        v.error(f"Error reverse DNS: {e}")
        return None

def get_dns_records(domain, verbose=False):
    """Dapatkan semua DNS records umum"""
    v = Verbose(verbose)
    records = {}
    types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'CAA']
    for t in types:
        try:
            answers = dns.resolver.resolve(domain, t, raise_on_no_answer=False)
            records[t] = [str(r) for r in answers]
        except dns.resolver.NoAnswer:
            continue
        except Exception as e:
            v.error(f"Error {t}: {e}")
            continue
    return records

def get_whois_info(domain, verbose=False):
    """Dapatkan informasi WHOIS domain"""
    v = Verbose(verbose)
    v.log(f"Mengambil WHOIS untuk {domain}")
    try:
        w = whois.whois(domain)
        return {
            'registrar': w.registrar,
            'creation_date': str(w.creation_date) if w.creation_date else None,
            'expiration_date': str(w.expiration_date) if w.expiration_date else None,
            'updated_date': str(w.updated_date) if w.updated_date else None,
            'name_servers': w.name_servers,
            'emails': w.emails,
            'org': w.org,
            'country': w.country
        }
    except Exception as e:
        v.error(f"Gagal WHOIS: {e}")
        return None

def track_web(target, verbose=False, save=None):
    """Fungsi utama web tracking"""
    v = Verbose(verbose)
    print(f"\n[ Web Tracker ]")
    print(f"Target: {target}")
    print("-" * 50)

    domain = extract_domain(target)
    print(f"Domain: {domain}")

    result = {
        'domain': domain,
        'ips': [],
        'dns': {},
        'whois': {}
    }

    # Dapatkan IP
    ips = get_ip_from_domain(domain, verbose)
    if ips:
        result['ips'] = []
        print(f"\n[ IP Addresses ]")
        for ip in ips:
            hostname = get_hostname_from_ip(ip, verbose)
            print(f"  {ip}  {f'({hostname})' if hostname else ''}")
            result['ips'].append({'ip': ip, 'hostname': hostname})

    # Dapatkan DNS records
    dns_records = get_dns_records(domain, verbose)
    if dns_records:
        result['dns'] = dns_records
        print(f"\n[ DNS Records ]")
        for rtype, records in dns_records.items():
            print(f"  {rtype}:")
            for rec in records[:3]:
                print(f"    - {rec}")
            if len(records) > 3:
                print(f"    ... dan {len(records)-3} lainnya")

    # Dapatkan WHOIS
    whois_info = get_whois_info(domain, verbose)
    if whois_info:
        result['whois'] = whois_info
        print(f"\n[ WHOIS Info ]")
        for k, v in whois_info.items():
            if v:
                if isinstance(v, list):
                    print(f"  {k}: {', '.join(str(x) for x in v[:3])}")
                else:
                    print(f"  {k}: {v}")

    # Simpan jika diminta
    if save:
        output = prepare_output(result, target, "webtrack")
        save_to_json(output, save)
        print(f"\n[+] Hasil disimpan ke {save}")

    return result
