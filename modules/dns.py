import dns.resolver
from lib.verbose import Verbose
from lib.json_save import save_to_json, prepare_output

def dns_lookup(domain, record_type='A', verbose=False, save=None):
    v = Verbose(verbose)
    v.log(f"DNS lookup for {domain} ({record_type})")
    
    try:
        answers = dns.resolver.resolve(domain, record_type)
        results = [str(r) for r in answers]
        print(f"\n[ {record_type} Records for {domain} ]")
        for r in results:
            print(f"  - {r}")
        
        if save:
            output = prepare_output({record_type: results}, domain, "dns")
            save_to_json(output, save)
            
    except Exception as e:
        v.error(f"DNS lookup failed: {e}")
