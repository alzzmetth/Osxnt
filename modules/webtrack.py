import socket
import dns.resolver
import whois
from urllib.parse import urlparse
from lib.verbose import Verbose
from lib.json_save import save_to_json, prepare_output

def extract_domain(url):
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path
    if ':' in domain:
        domain = domain.split(':')[0]
    return domain

def get_ip_from_domain(domain, verbose=False):
    v = Verbose(verbose)
    try:
        ips = []
        addrinfo = socket.getaddrinfo(domain, 80)
        for addr in addrinfo:
            ip = addr[4][0]
            if ip not in ips:
                ips.append(ip)
        return ips
    except Exception as e:
        v.error(f"DNS resolution failed: {e}")
        return []

def get_dns_records(domain, verbose=False):
    v = Verbose(verbose)
    records = {}
    types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA']
    for t in types:
        try:
            answers = dns.resolver.resolve(domain, t, raise_on_no_answer=False)
            records[t] = [str(r) for r in answers]
        except:
            continue
    return records

def get_whois(domain, verbose=False):
    v = Verbose(verbose)
    try:
        w = whois.whois(domain)
        return {
            'registrar': w.registrar,
            'creation': str(w.creation_date),
            'expiration': str(w.expiration_date),
            'name_servers': w.name_servers
        }
    except:
        return None

def track_web(target, verbose=False, save=None):
    v = Verbose(verbose)
    domain = extract_domain(target)
    v.log(f"Target domain: {domain}")
    
    result = {}
    
    # IPs
    ips = get_ip_from_domain(domain, verbose)
    result['ips'] = ips
    print(f"\n[ IP ADDRESSES ]")
    for ip in ips:
        print(f"  - {ip}")
    
    # DNS
    dns = get_dns_records(domain, verbose)
    result['dns'] = dns
    print(f"\n[ DNS RECORDS ]")
    for rec, values in dns.items():
        print(f"  {rec}:")
        for v in values[:3]:
            print(f"    - {v}")
    
    # WHOIS
    who = get_whois(domain, verbose)
    result['whois'] = who
    if who:
        print(f"\n[ WHOIS ]")
        print(f"  Registrar: {who.get('registrar')}")
        print(f"  Creation: {who.get('creation')}")
    
    if save:
        output = prepare_output(result, target, "webtrack")
        save_to_json(output, save)
