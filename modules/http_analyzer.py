#!/usr/bin/env python3
# OSXNT - HTTP Header Analyzer Module
# Developed by alzzdevmaret

import requests
import json
from urllib.parse import urlparse
from lib.verbose import Verbose
from lib.json_save import save_to_json, prepare_output

class HTTPAnalyzer:
    """
    HTTP Header Analyzer untuk OSXNT
    Menganalisis HTTP response headers dari website
    """
    
    def __init__(self, verbose=False):
        self.v = Verbose(verbose)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def analyze(self, url, follow_redirects=True, save=None):
        """
        Analisis HTTP headers dari URL
        
        Args:
            url (str): Target URL
            follow_redirects (bool): Ikuti redirect
            save (str): File JSON untuk menyimpan hasil
        
        Returns:
            dict: Hasil analisis
        """
        print(f"\n[ HTTP Header Analyzer ]")
        print(f"Target: {url}")
        print("-" * 50)
        
        # Normalisasi URL
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            print(f"⚠️  Menambahkan https:// -> {url}")
        
        result = {
            'url': url,
            'headers': {},
            'security': {},
            'server_info': {},
            'cookies': [],
            'redirects': []
        }
        
        try:
            # Request dengan atau tanpa redirect
            if follow_redirects:
                response = self.session.get(url, timeout=10, allow_redirects=True)
                result['final_url'] = response.url
                
                # Catat redirect history
                for i, r in enumerate(response.history):
                    result['redirects'].append({
                        'step': i + 1,
                        'url': r.url,
                        'status': r.status_code
                    })
            else:
                response = self.session.get(url, timeout=10, allow_redirects=False)
                result['final_url'] = url
            
            # Basic info
            result['status_code'] = response.status_code
            result['reason'] = response.reason
            result['protocol'] = f"HTTP/{response.raw.version / 10}"
            
            print(f"\n📊 BASIC INFO:")
            print(f"  URL Final: {result['final_url']}")
            print(f"  Status: {response.status_code} {response.reason}")
            print(f"  Protocol: {result['protocol']}")
            
            # Headers
            print(f"\n📋 HEADERS:")
            headers = dict(response.headers)
            result['headers'] = headers
            
            for key, value in sorted(headers.items()):
                print(f"  {key}: {value}")
            
            # Security Analysis
            print(f"\n🔒 SECURITY ANALYSIS:")
            result['security'] = self._analyze_security(headers)
            
            for key, value in result['security'].items():
                status = "✅" if value['status'] == 'good' else "⚠️" if value['status'] == 'warning' else "❌"
                print(f"  {status} {key}: {value['message']}")
            
            # Server Info
            print(f"\n🖥️ SERVER INFO:")
            result['server_info'] = self._get_server_info(headers)
            
            for key, value in result['server_info'].items():
                print(f"  {key}: {value}")
            
            # Cookies
            if response.cookies:
                print(f"\n🍪 COOKIES:")
                result['cookies'] = []
                for cookie in response.cookies:
                    cookie_info = {
                        'name': cookie.name,
                        'value': cookie.value,
                        'domain': cookie.domain,
                        'path': cookie.path,
                        'secure': cookie.secure,
                        'httponly': cookie.has_nonstandard_attr('HttpOnly')
                    }
                    result['cookies'].append(cookie_info)
                    
                    secure_flag = "🔒" if cookie.secure else "⚠️"
                    http_only = "🔒" if cookie.has_nonstandard_attr('HttpOnly') else "⚠️"
                    print(f"  {cookie.name}: {cookie.value[:30]}...")
                    print(f"    Domain: {cookie.domain}, Path: {cookie.path}")
                    print(f"    Secure: {secure_flag}, HttpOnly: {http_only}")
            
            # Recommendations
            print(f"\n💡 RECOMMENDATIONS:")
            recommendations = self._get_recommendations(result['security'])
            for rec in recommendations:
                print(f"  • {rec}")
            
            # Save if requested
            if save:
                output = prepare_output(result, url, "http_analyzer")
                save_to_json(output, save)
                print(f"\n✅ Hasil disimpan ke {save}")
            
            return result
            
        except requests.exceptions.SSLError as e:
            self.v.error(f"SSL Error: {e}")
            print("\n❌ SSL Certificate Error!")
            return None
        except requests.exceptions.ConnectionError:
            self.v.error("Connection Error")
            return None
        except requests.exceptions.Timeout:
            self.v.error("Timeout")
            return None
        except Exception as e:
            self.v.error(f"Error: {e}")
            return None
    
    def _analyze_security(self, headers):
        """Analisis security headers"""
        security = {}
        
        # Security Headers Checklist
        checks = {
            'Strict-Transport-Security': {
                'good': 'HSTS enabled - good for HTTPS security',
                'warning': 'HSTS tidak ada - risiko downgrade attack',
                'status': 'good' if 'Strict-Transport-Security' in headers else 'warning'
            },
            'Content-Security-Policy': {
                'good': 'CSP ada - melindungi dari XSS',
                'warning': 'CSP tidak ada - rentan XSS',
                'status': 'good' if 'Content-Security-Policy' in headers else 'warning'
            },
            'X-Frame-Options': {
                'good': 'X-Frame-Options ada - melindungi dari clickjacking',
                'warning': 'X-Frame-Options tidak ada - rentan clickjacking',
                'status': 'good' if 'X-Frame-Options' in headers else 'warning'
            },
            'X-Content-Type-Options': {
                'good': 'X-Content-Type-Options: nosniff - good',
                'warning': 'X-Content-Type-Options tidak ada',
                'status': 'good' if headers.get('X-Content-Type-Options') == 'nosniff' else 'warning'
            },
            'Referrer-Policy': {
                'good': 'Referrer-Policy ada',
                'warning': 'Referrer-Policy tidak ada',
                'status': 'good' if 'Referrer-Policy' in headers else 'warning'
            },
            'Permissions-Policy': {
                'good': 'Permissions-Policy ada',
                'warning': 'Permissions-Policy tidak ada',
                'status': 'good' if 'Permissions-Policy' in headers else 'warning'
            }
        }
        
        for header, info in checks.items():
            security[header] = {
                'status': info['status'],
                'message': info['good'] if header in headers else info['warning'],
                'present': header in headers,
                'value': headers.get(header, None)
            }
        
        # Cache Control
        if 'Cache-Control' in headers:
            cache = headers['Cache-Control']
            if 'no-store' in cache and 'no-cache' in cache:
                security['Cache-Control'] = {
                    'status': 'good',
                    'message': 'Cache-Control baik: ' + cache,
                    'present': True,
                    'value': cache
                }
            else:
                security['Cache-Control'] = {
                    'status': 'warning',
                    'message': 'Cache-Control lemah: ' + cache,
                    'present': True,
                    'value': cache
                }
        else:
            security['Cache-Control'] = {
                'status': 'warning',
                'message': 'Cache-Control tidak ada',
                'present': False,
                'value': None
            }
        
        return security
    
    def _get_server_info(self, headers):
        """Ekstrak informasi server"""
        info = {}
        
        # Server
        if 'Server' in headers:
            info['Server'] = headers['Server']
        else:
            info['Server'] = 'Tidak diketahui'
        
        # Powered By
        if 'X-Powered-By' in headers:
            info['Powered By'] = headers['X-Powered-By']
        
        # Via (proxy)
        if 'Via' in headers:
            info['Via'] = headers['Via']
        
        # CF-Ray (Cloudflare)
        if 'CF-Ray' in headers:
            info['Cloudflare'] = 'Yes'
        
        return info
    
    def _get_recommendations(self, security):
        """Generate rekomendasi keamanan"""
        recommendations = []
        
        for header, data in security.items():
            if data['status'] == 'warning' and not data['present']:
                if header == 'Strict-Transport-Security':
                    recommendations.append(f"Tambahkan HSTS: Strict-Transport-Security: max-age=31536000")
                elif header == 'Content-Security-Policy':
                    recommendations.append(f"Tambahkan CSP untuk mencegah XSS")
                elif header == 'X-Frame-Options':
                    recommendations.append(f"Tambahkan X-Frame-Options: DENY untuk cegah clickjacking")
                elif header == 'X-Content-Type-Options':
                    recommendations.append(f"Tambahkan X-Content-Type-Options: nosniff")
                elif header == 'Referrer-Policy':
                    recommendations.append(f"Tambahkan Referrer-Policy: strict-origin-when-cross-origin")
        
        return recommendations
    
    def quick_check(self, url):
        """Quick check sederhana"""
        try:
            r = self.session.get(url, timeout=5)
            print(f"\n⚡ QUICK CHECK: {url}")
            print(f"Status: {r.status_code}")
            print(f"Server: {r.headers.get('Server', 'Unknown')}")
            print(f"Powered By: {r.headers.get('X-Powered-By', 'Unknown')}")
            print(f"Security Headers: ", end='')
            
            security_headers = ['Strict-Transport-Security', 'Content-Security-Policy', 
                              'X-Frame-Options', 'X-Content-Type-Options']
            present = [h for h in security_headers if h in r.headers]
            print(f"{len(present)}/{len(security_headers)} present")
            
        except Exception as e:
            print(f"Error: {e}")


# Untuk testing langsung
if __name__ == "__main__":
    analyzer = HTTPAnalyzer(verbose=True)
    analyzer.analyze("https://google.com")
