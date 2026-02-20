#!/usr/bin/env python3
# OSXNT - URL Extractor & Checker Module
# Developed by alzzdevmaret

import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from lib.verbose import Verbose
from lib.json_save import save_to_json, prepare_output
from collections import Counter

class URLExtractor:
    """
    URL Extractor untuk mengambil semua link dari website
    """
    
    def __init__(self, verbose=False):
        self.v = Verbose(verbose)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Kategori URL
        self.url_categories = {
            'internal': [],
            'external': [],
            'static': [],
            'mailto': [],
            'javascript': [],
            'invalid': []
        }
    
    def extract(self, url, depth=1, save=None):
        """
        Extract semua URL dari website
        
        Args:
            url (str): Target URL
            depth (int): Kedalaman crawling
            save (str): File JSON untuk menyimpan hasil
        
        Returns:
            dict: Hasil extraction
        """
        print(f"\n[ URL Extractor ]")
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
            'total_urls': 0,
            'categories': self.url_categories.copy(),
            'urls_by_type': {},
            'urls_by_domain': {},
            'broken_links': []
        }
        
        visited = set()
        to_visit = [(url, 0)]
        
        while to_visit and len(visited) < 100:  # Limit 100 pages
            current_url, current_depth = to_visit.pop(0)
            
            if current_url in visited or current_depth > depth:
                continue
            
            self.v.log(f"Crawling [{current_depth}/{depth}]: {current_url}")
            
            # Extract dari halaman ini
            page_urls = self._extract_from_page(current_url)
            
            # Kategorikan
            categorized = self._categorize_urls(page_urls, current_url)
            
            # Update result
            for cat, urls in categorized.items():
                if cat in result['categories']:
                    result['categories'][cat].extend(urls)
            
            visited.add(current_url)
            
            # Tambahkan internal links untuk crawling selanjutnya
            if current_depth < depth:
                for internal_url in categorized['internal']:
                    if internal_url not in visited and internal_url not in [v[0] for v in to_visit]:
                        to_visit.append((internal_url, current_depth + 1))
        
        # Hitung total
        for cat, urls in result['categories'].items():
            result['total_urls'] += len(urls)
            result['urls_by_type'][cat] = len(urls)
        
        # Group by domain
        domains = []
        for cat, urls in result['categories'].items():
            for u in urls:
                try:
                    domain = urlparse(u).netloc
                    if domain:
                        domains.append(domain)
                except:
                    pass
        
        result['urls_by_domain'] = dict(Counter(domains).most_common())
        
        # Tampilkan hasil
        self._display_results(result)
        
        # Check broken links (optional)
        if depth > 0:
            print("\n🔍 Checking for broken links...")
            result['broken_links'] = self._check_broken_links(
                result['categories']['internal'] + result['categories']['external']
            )
        
        # Save jika diminta
        if save:
            output = prepare_output(result, url, "url_extractor")
            save_to_json(output, save)
            print(f"\n✅ Hasil disimpan ke {save}")
        
        return result
    
    def _extract_from_page(self, url):
        """
        Extract semua URL dari satu halaman
        """
        urls = []
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Dari tag <a>
            for link in soup.find_all('a', href=True):
                href = link['href'].strip()
                if href:
                    full_url = urljoin(url, href)
                    urls.append({
                        'url': full_url,
                        'text': link.text.strip()[:100],
                        'type': 'a'
                    })
            
            # Dari tag <link> (CSS, dll)
            for link in soup.find_all('link', href=True):
                href = link['href'].strip()
                if href:
                    full_url = urljoin(url, href)
                    urls.append({
                        'url': full_url,
                        'type': 'link',
                        'rel': link.get('rel', [''])[0]
                    })
            
            # Dari tag <script> src
            for script in soup.find_all('script', src=True):
                src = script['src'].strip()
                if src:
                    full_url = urljoin(url, src)
                    urls.append({
                        'url': full_url,
                        'type': 'script'
                    })
            
            # Dari tag <img> src
            for img in soup.find_all('img', src=True):
                src = img['src'].strip()
                if src:
                    full_url = urljoin(url, src)
                    urls.append({
                        'url': full_url,
                        'type': 'image',
                        'alt': img.get('alt', '')[:50]
                    })
            
            # Dari tag <iframe> src
            for iframe in soup.find_all('iframe', src=True):
                src = iframe['src'].strip()
                if src:
                    full_url = urljoin(url, src)
                    urls.append({
                        'url': full_url,
                        'type': 'iframe'
                    })
            
            # Dari tag <form> action
            for form in soup.find_all('form', action=True):
                action = form['action'].strip()
                if action:
                    full_url = urljoin(url, action)
                    urls.append({
                        'url': full_url,
                        'type': 'form',
                        'method': form.get('method', 'get')
                    })
            
            self.v.log(f"  Found {len(urls)} URLs")
            
        except Exception as e:
            self.v.error(f"Error extracting from {url}: {e}")
        
        return urls
    
    def _categorize_urls(self, urls, base_url):
        """
        Kategorikan URL berdasarkan tipe
        """
        base_domain = urlparse(base_url).netloc
        
        categorized = {
            'internal': [],
            'external': [],
            'static': [],
            'mailto': [],
            'javascript': [],
            'invalid': []
        }
        
        for url_info in urls:
            url = url_info['url']
            
            # Skip kosong
            if not url:
                continue
            
            # Kategorikan
            if url.startswith('mailto:'):
                categorized['mailto'].append(url)
            
            elif url.startswith('javascript:'):
                categorized['javascript'].append(url)
            
            elif url.startswith(('#', 'tel:', 'sms:', 'ftp:')):
                categorized['invalid'].append(url)
            
            else:
                # Cek static files
                if url.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', 
                                '.svg', '.woff', '.ttf', '.pdf', '.doc', '.zip')):
                    categorized['static'].append(url_info)
                
                else:
                    # Cek internal/external
                    try:
                        domain = urlparse(url).netloc
                        if domain == base_domain or domain == '':
                            categorized['internal'].append(url)
                        elif domain:
                            categorized['external'].append(url)
                        else:
                            categorized['invalid'].append(url)
                    except:
                        categorized['invalid'].append(url)
        
        return categorized
    
    def _check_broken_links(self, urls, limit=50):
        """
        Check broken links (HTTP status)
        """
        broken = []
        checked = 0
        
        for url in urls[:limit]:
            try:
                response = self.session.head(url, timeout=5, allow_redirects=True)
                if response.status_code >= 400:
                    broken.append({
                        'url': url,
                        'status': response.status_code,
                        'error': response.reason
                    })
                    print(f"  ❌ {url[:60]}... -> {response.status_code}")
                else:
                    print(f"  ✅ {url[:60]}... -> OK")
                
                checked += 1
                
            except Exception as e:
                broken.append({
                    'url': url,
                    'status': 0,
                    'error': str(e)
                })
                print(f"  ❌ {url[:60]}... -> Error")
        
        return broken
    
    def _display_results(self, result):
        """
        Display hasil extraction
        """
        print("\n" + "=" * 60)
        print(f"🔗 URL EXTRACTION RESULTS")
        print("=" * 60)
        print(f"Target: {result['target']}")
        print(f"Total URLs found: {result['total_urls']}")
        print("\n📊 URL CATEGORIES:")
        
        for cat, count in result['urls_by_type'].items():
            if count > 0:
                print(f"  {cat.capitalize():12}: {count}")
        
        if result['urls_by_domain']:
            print("\n🌐 TOP DOMAINS:")
            for domain, count in list(result['urls_by_domain'].items())[:10]:
                print(f"  {domain[:40]:40} : {count}")
        
        if result['broken_links']:
            print(f"\n⚠️ Broken Links: {len(result['broken_links'])}")
            for link in result['broken_links'][:10]:
                status = link['status'] if link['status'] else 'ERR'
                print(f"  [{status}] {link['url'][:60]}...")
        
        print("=" * 60)


class URLChecker:
    """
    URL Checker untuk memeriksa resource website
    """
    
    def __init__(self, verbose=False):
        self.v = Verbose(verbose)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def check(self, url, resource_type='all', save=None):
        """
        Check resources dari website
        
        Args:
            url (str): Target URL
            resource_type: 'all', 'images', 'scripts', 'styles', 'links'
            save (str): File JSON untuk menyimpan hasil
        """
        print(f"\n[ URL Checker ]")
        print(f"Target: {url}")
        print(f"Resource type: {resource_type}")
        print("-" * 50)
        
        # Normalisasi URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            print(f"⚠️  Menambahkan https:// -> {url}")
        
        result = {
            'target': url,
            'resource_type': resource_type,
            'resources': {},
            'summary': {}
        }
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract berdasarkan tipe
            if resource_type in ['all', 'images']:
                result['resources']['images'] = self._check_images(soup, url)
            
            if resource_type in ['all', 'scripts']:
                result['resources']['scripts'] = self._check_scripts(soup, url)
            
            if resource_type in ['all', 'styles']:
                result['resources']['styles'] = self._check_styles(soup, url)
            
            if resource_type in ['all', 'links']:
                result['resources']['links'] = self._check_links(soup, url)
            
            # Summary
            for res_type, resources in result['resources'].items():
                total = len(resources)
                working = sum(1 for r in resources if r.get('status') == 'OK')
                result['summary'][res_type] = {
                    'total': total,
                    'working': working,
                    'broken': total - working
                }
            
            # Tampilkan hasil
            self._display_results(result)
            
            # Save jika diminta
            if save:
                output = prepare_output(result, url, "url_checker")
                save_to_json(output, save)
                print(f"\n✅ Hasil disimpan ke {save}")
            
        except Exception as e:
            self.v.error(f"Error: {e}")
        
        return result
    
    def _check_images(self, soup, base_url):
        """Check semua image src"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            full_url = urljoin(base_url, src)
            
            status, size = self._check_resource(full_url)
            images.append({
                'url': full_url,
                'alt': img.get('alt', ''),
                'status': status,
                'size': size
            })
        
        return images
    
    def _check_scripts(self, soup, base_url):
        """Check semua script src"""
        scripts = []
        for script in soup.find_all('script', src=True):
            src = script['src']
            full_url = urljoin(base_url, src)
            
            status, size = self._check_resource(full_url)
            scripts.append({
                'url': full_url,
                'status': status,
                'size': size
            })
        
        return scripts
    
    def _check_styles(self, soup, base_url):
        """Check semua stylesheet"""
        styles = []
        for link in soup.find_all('link', rel='stylesheet'):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            status, size = self._check_resource(full_url)
            styles.append({
                'url': full_url,
                'status': status,
                'size': size
            })
        
        return styles
    
    def _check_links(self, soup, base_url):
        """Check semua hyperlink"""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith(('http://', 'https://')):
                status, size = self._check_resource(href)
                links.append({
                    'url': href,
                    'text': a.text.strip()[:50],
                    'status': status,
                    'size': size
                })
        
        return links
    
    def _check_resource(self, url):
        """Check status dan size resource"""
        try:
            response = self.session.head(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                size = response.headers.get('content-length', 'unknown')
                return 'OK', size
            else:
                return f'HTTP {response.status_code}', None
        except:
            return 'ERROR', None
    
    def _display_results(self, result):
        """Display hasil check"""
        print("\n" + "=" * 60)
        print(f"🔍 URL CHECKER RESULTS")
        print("=" * 60)
        
        for res_type, summary in result['summary'].items():
            print(f"\n📁 {res_type.upper()}:")
            print(f"   Total: {summary['total']}")
            print(f"   ✅ Working: {summary['working']}")
            print(f"   ❌ Broken: {summary['broken']}")
            
            if summary['broken'] > 0 and res_type in result['resources']:
                print("   Broken URLs:")
                for res in result['resources'][res_type]:
                    if res['status'] != 'OK':
                        print(f"     [{res['status']}] {res['url'][:70]}...")


# Untuk testing
if __name__ == "__main__":
    # Test URL Extractor
    extractor = URLExtractor(verbose=True)
    extractor.extract("https://example.com", depth=1)
    
    # Test URL Checker
    checker = URLChecker(verbose=True)
    checker.check("https://example.com", "all")
