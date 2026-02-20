#!/usr/bin/env python3
# OSXNT - Email Harvester Module
# Developed by alzzdevmaret

import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from lib.verbose import Verbose
from lib.json_save import save_to_json, prepare_output

class EmailHarvester:
    """
    Email Harvester untuk mengumpulkan alamat email dari website
    """
    
    def __init__(self, verbose=False):
        self.v = Verbose(verbose)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.emails_found = set()
        self.pages_scanned = 0
        
        # Regex pattern untuk email
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        
        # Regex untuk skip email palsu
        self.skip_patterns = [
            r'\.png$', r'\.jpg$', r'\.jpeg$', r'\.gif$', r'\.css$', r'\.js$',
            r'@example\.com', r'@domain\.com', r'@yourdomain\.com',
            r'noreply@', r'no-reply@', r'donotreply@'
        ]
        self.skip_regex = re.compile('|'.join(self.skip_patterns), re.IGNORECASE)
    
    def harvest(self, url, depth=2, save=None):
        """
        Main function untuk harvest email dari website
        
        Args:
            url (str): Target URL
            depth (int): Kedalaman crawling (default: 2)
            save (str): File JSON untuk menyimpan hasil
        
        Returns:
            dict: Hasil harvesting
        """
        print(f"\n[ Email Harvester ]")
        print(f"Target: {url}")
        print(f"Depth: {depth}")
        print("-" * 50)
        
        # Normalisasi URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            print(f"⚠️  Menambahkan https:// -> {url}")
        
        result = {
            'target': url,
            'depth': depth,
            'emails': [],
            'pages_scanned': 0,
            'unique_domains': set()
        }
        
        visited = set()
        to_visit = [(url, 0)]
        
        while to_visit and self.pages_scanned < 50:  # Limit 50 pages
            current_url, current_depth = to_visit.pop(0)
            
            if current_url in visited or current_depth > depth:
                continue
            
            self.v.log(f"Scanning [{current_depth}/{depth}]: {current_url}")
            
            # Scan page
            page_emails = self._scan_page(current_url)
            
            if page_emails:
                print(f"  ✓ Found {len(page_emails)} emails on {current_url}")
                for email in page_emails:
                    if email not in self.emails_found:
                        self.emails_found.add(email)
                        result['emails'].append({
                            'email': email,
                            'source': current_url,
                            'domain': email.split('@')[1] if '@' in email else 'unknown'
                        })
            
            visited.add(current_url)
            self.pages_scanned += 1
            result['pages_scanned'] = self.pages_scanned
            
            # Extract more links if depth allows
            if current_depth < depth:
                links = self._extract_links(current_url)
                for link in links:
                    if link not in visited:
                        to_visit.append((link, current_depth + 1))
        
        # Group by domain
        domains = {}
        for email in result['emails']:
            domain = email['domain']
            if domain not in domains:
                domains[domain] = 0
            domains[domain] += 1
        
        result['unique_domains'] = domains
        
        # Tampilkan hasil
        self._display_results(result)
        
        # Save jika diminta
        if save:
            output = prepare_output(result, url, "email_harvester")
            save_to_json(output, save)
            print(f"\n✅ Hasil disimpan ke {save}")
        
        return result
    
    def _scan_page(self, url):
        """
        Scan satu halaman untuk mencari email
        """
        emails = set()
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Scan HTML content
            html_emails = self.email_pattern.findall(response.text)
            for email in html_emails:
                if self._is_valid_email(email):
                    emails.add(email.lower())
            
            # Scan mailto links
            soup = BeautifulSoup(response.text, 'html.parser')
            for mailto in soup.find_all('a', href=True):
                href = mailto['href']
                if href.startswith('mailto:'):
                    email = href[7:].split('?')[0]  # Remove ?subject etc
                    if self._is_valid_email(email):
                        emails.add(email.lower())
            
            self.v.log(f"  Found {len(emails)} valid emails")
            
        except requests.exceptions.RequestException as e:
            self.v.error(f"Error scanning {url}: {e}")
        except Exception as e:
            self.v.error(f"Unexpected error: {e}")
        
        return list(emails)
    
    def _is_valid_email(self, email):
        """
        Validasi email (bukan dummy/gambar/file)
        """
        # Cek panjang
        if len(email) > 100 or len(email) < 5:
            return False
        
        # Cek pattern skip
        if self.skip_regex.search(email):
            return False
        
        # Cek ekstensi file
        if email.endswith(('.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.svg')):
            return False
        
        # Cek karakter valid
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False
        
        return True
    
    def _extract_links(self, url):
        """
        Extract semua link dari halaman
        """
        links = []
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                
                # Filter hanya HTTP/HTTPS
                if full_url.startswith(('http://', 'https://')):
                    # Filter domain yang sama
                    if urlparse(full_url).netloc == urlparse(url).netloc:
                        links.append(full_url)
            
        except:
            pass
        
        return list(set(links))[:20]  # Max 20 links per page
    
    def _display_results(self, result):
        """
        Display hasil harvest
        """
        print("\n" + "=" * 60)
        print(f"📧 EMAIL HARVEST RESULTS")
        print("=" * 60)
        print(f"Target: {result['target']}")
        print(f"Pages scanned: {result['pages_scanned']}")
        print(f"Total emails found: {len(result['emails'])}")
        
        if result['emails']:
            print("\n📋 EMAILS FOUND:")
            for i, email in enumerate(result['emails'][:20], 1):
                print(f"  {i:2d}. {email['email']} (from: {email['source'][:50]}...)")
            
            if len(result['emails']) > 20:
                print(f"  ... and {len(result['emails']) - 20} more")
            
            print("\n📊 DOMAIN STATISTICS:")
            for domain, count in sorted(result['unique_domains'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  {domain}: {count} emails")
        else:
            print("\n❌ No emails found")
        
        print("=" * 60)
    
    def quick_scan(self, url):
        """
        Quick scan tanpa crawling (halaman utama saja)
        """
        print(f"\n⚡ Quick Email Scan: {url}")
        emails = self._scan_page(url)
        
        if emails:
            print(f"Found {len(emails)} emails:")
            for email in emails:
                print(f"  📧 {email}")
        else:
            print("No emails found")
        
        return emails
    
    def scan_from_file(self, filename, save=None):
        """
        Scan multiple targets dari file
        """
        from lib.multi_target import read_targets_from_file
        
        targets = read_targets_from_file(filename)
        if not targets:
            return
        
        all_results = []
        for target in targets:
            print(f"\n{'='*60}")
            print(f"Scanning: {target}")
            result = self.harvest(target, depth=1)
            all_results.append(result)
        
        if save:
            output = prepare_output(all_results, "multi_target", "email_harvester")
            save_to_json(output, save)
            print(f"\n✅ All results saved to {save}")


# Untuk testing langsung
if __name__ == "__main__":
    harvester = EmailHarvester(verbose=True)
    harvester.harvest("https://example.com", depth=2)
