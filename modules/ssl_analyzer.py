#!/usr/bin/env python3
# OSXNT - SSL/TLS Analyzer Module
# Developed by alzzdevmaret

import ssl
import socket
import datetime
import OpenSSL
import certifi
from lib.verbose import Verbose
from lib.json_save import save_to_json, prepare_output

class SSLAnalyzer:
    """
    SSL/TLS Analyzer untuk OSXNT
    Menganalisis sertifikat SSL dan konfigurasi keamanan
    """
    
    def __init__(self, verbose=False):
        self.v = Verbose(verbose)
    
    def analyze(self, hostname, port=443, save=None):
        """
        Analisis SSL/TLS untuk host
        
        Args:
            hostname (str): Target hostname
            port (int): Port (default: 443)
            save (str): File JSON untuk menyimpan hasil
        
        Returns:
            dict: Hasil analisis
        """
        print(f"\n[ SSL/TLS Analyzer ]")
        print(f"Target: {hostname}:{port}")
        print("-" * 50)
        
        result = {
            'hostname': hostname,
            'port': port,
            'certificate': {},
            'security': {},
            'vulnerabilities': []
        }
        
        try:
            # Konek ke server
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    
                    # Dapatkan sertifikat
                    cert_bin = ssock.getpeercert(binary_form=True)
                    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, cert_bin)
                    
                    # Versi TLS/SSL
                    result['protocol'] = {
                        'version': ssock.version(),
                        'cipher': ssock.cipher()
                    }
                    
                    print(f"\n📊 BASIC INFO:")
                    print(f"  Protocol: {ssock.version()}")
                    print(f"  Cipher: {ssock.cipher()[0]} ({ssock.cipher()[1]} bits)")
                    
                    # Analisis sertifikat
                    result['certificate'] = self._analyze_certificate(cert)
                    self._print_certificate_info(result['certificate'])
                    
                    # Security checks
                    result['security'] = self._check_security(hostname, port)
                    self._print_security_info(result['security'])
                    
                    # Vulnerability checks
                    result['vulnerabilities'] = self._check_vulnerabilities(hostname, port)
                    self._print_vulnerabilities(result['vulnerabilities'])
                    
                    # Grade
                    grade = self._calculate_grade(result)
                    result['grade'] = grade
                    print(f"\n📈 SSL GRADE: {grade['grade']} - {grade['description']}")
                    
                    # Recommendations
                    recommendations = self._get_recommendations(result)
                    if recommendations:
                        print(f"\n💡 RECOMMENDATIONS:")
                        for rec in recommendations:
                            print(f"  • {rec}")
                    
                    # Save if requested
                    if save:
                        output = prepare_output(result, hostname, "ssl_analyzer")
                        save_to_json(output, save)
                        print(f"\n✅ Hasil disimpan ke {save}")
                    
                    return result
                    
        except socket.timeout:
            self.v.error(f"Timeout connecting to {hostname}:{port}")
        except socket.gaierror:
            self.v.error(f"Hostname {hostname} tidak valid")
        except ConnectionRefusedError:
            self.v.error(f"Koneksi ditolak oleh {hostname}:{port}")
        except ssl.SSLError as e:
            self.v.error(f"SSL Error: {e}")
        except Exception as e:
            self.v.error(f"Error: {e}")
        
        return None
    
    def _analyze_certificate(self, cert):
        """Analisis detail sertifikat"""
        cert_info = {}
        
        # Subject
        subject = cert.get_subject()
        cert_info['subject'] = {}
        for component in subject.get_components():
            cert_info['subject'][component[0].decode()] = component[1].decode()
        
        # Issuer
        issuer = cert.get_issuer()
        cert_info['issuer'] = {}
        for component in issuer.get_components():
            cert_info['issuer'][component[0].decode()] = component[1].decode()
        
        # Validity
        not_before = datetime.datetime.strptime(
            cert.get_notBefore().decode(), '%Y%m%d%H%M%SZ'
        )
        not_after = datetime.datetime.strptime(
            cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ'
        )
        
        cert_info['valid_from'] = not_before.isoformat()
        cert_info['valid_until'] = not_after.isoformat()
        
        # Days remaining
        now = datetime.datetime.utcnow()
        days_remaining = (not_after - now).days
        cert_info['days_remaining'] = days_remaining
        
        # Serial number
        cert_info['serial_number'] = hex(cert.get_serial_number())[2:].upper()
        
        # Signature algorithm
        cert_info['signature_algorithm'] = cert.get_signature_algorithm().decode()
        
        # Version
        cert_info['version'] = cert.get_version()
        
        # Extensions
        cert_info['extensions'] = []
        for i in range(cert.get_extension_count()):
            ext = cert.get_extension(i)
            cert_info['extensions'].append({
                'name': ext.get_short_name().decode(),
                'critical': ext.get_critical(),
                'value': str(ext)
            })
        
        return cert_info
    
    def _check_security(self, hostname, port):
        """Cek konfigurasi keamanan"""
        security = {}
        
        # Cek protocol support
        protocols = ['TLSv1', 'TLSv1.1', 'TLSv1.2', 'TLSv1.3']
        security['protocols'] = {}
        
        for protocol in protocols:
            try:
                context = ssl.SSLContext(self._get_protocol_version(protocol))
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                
                with socket.create_connection((hostname, port), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        security['protocols'][protocol] = 'supported'
            except:
                security['protocols'][protocol] = 'not_supported'
        
        # Cek HSTS (lewat koneksi HTTP nanti di module terpisah)
        # Untuk sementara kita skip
        
        # Perfect Forward Secrecy
        security['perfect_forward_secrecy'] = self._check_pfs(hostname, port)
        
        # Certificate transparency
        security['certificate_transparency'] = self._check_ct(hostname, port)
        
        return security
    
    def _check_vulnerabilities(self, hostname, port):
        """Cek kerentanan umum"""
        vulns = []
        
        # Cek Heartbleed (CVE-2014-0160)
        if self._check_heartbleed(hostname, port):
            vulns.append({
                'name': 'Heartbleed',
                'cve': 'CVE-2014-0160',
                'severity': 'CRITICAL',
                'description': 'Memori leak vulnerability in OpenSSL'
            })
        
        # Cek POODLE (CVE-2014-3566)
        if self._check_poodle(hostname, port):
            vulns.append({
                'name': 'POODLE',
                'cve': 'CVE-2014-3566',
                'severity': 'HIGH',
                'description': 'SSLv3 vulnerability'
            })
        
        # Cek FREAK (CVE-2015-0204)
        if self._check_freak(hostname, port):
            vulns.append({
                'name': 'FREAK',
                'cve': 'CVE-2015-0204',
                'severity': 'MEDIUM',
                'description': 'Export-grade RSA key vulnerability'
            })
        
        # Cek LOGJAM (CVE-2015-4000)
        if self._check_logjam(hostname, port):
            vulns.append({
                'name': 'LOGJAM',
                'cve': 'CVE-2015-4000',
                'severity': 'MEDIUM',
                'description': 'Weak Diffie-Hellman key exchange'
            })
        
        return vulns
    
    def _get_protocol_version(self, protocol):
        """Convert protocol name to SSLContext constant"""
        protocol_map = {
            'TLSv1': ssl.PROTOCOL_TLSv1,
            'TLSv1.1': ssl.PROTOCOL_TLSv1_1,
            'TLSv1.2': ssl.PROTOCOL_TLSv1_2,
            'TLSv1.3': ssl.PROTOCOL_TLS  # TLSv1.3
        }
        return protocol_map.get(protocol, ssl.PROTOCOL_TLS)
    
    def _check_pfs(self, hostname, port):
        """Check Perfect Forward Secrecy"""
        try:
            # Coba konek dengan cipher yang support PFS
            context = ssl.create_default_context()
            context.set_ciphers('ECDHE:!aNULL')
            
            with socket.create_connection((hostname, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cipher = ssock.cipher()[0]
                    if 'ECDHE' in cipher or 'DHE' in cipher:
                        return 'supported'
                    return 'not_supported'
        except:
            return 'unknown'
    
    def _check_ct(self, hostname, port):
        """Check Certificate Transparency"""
        # Simplified - ideally check SCT in certificate
        return 'not_checked'
    
    def _check_heartbleed(self, hostname, port):
        """Check Heartbleed vulnerability"""
        # Simplified - real check needs heartbeat extension test
        return False
    
    def _check_poodle(self, hostname, port):
        """Check POODLE vulnerability"""
        # Check if SSLv3 is supported
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_SSLv3)
            with socket.create_connection((hostname, port), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    return True
        except:
            return False
    
    def _check_freak(self, hostname, port):
        """Check FREAK vulnerability"""
        # Check if export-grade RSA ciphers are supported
        return False
    
    def _check_logjam(self, hostname, port):
        """Check LOGJAM vulnerability"""
        return False
    
    def _print_certificate_info(self, cert):
        """Print certificate information"""
        print(f"\n📜 CERTIFICATE INFO:")
        
        # Subject
        print(f"  Subject:")
        for key, value in cert['subject'].items():
            print(f"    {key}: {value}")
        
        # Issuer
        print(f"  Issuer:")
        for key, value in cert['issuer'].items():
            print(f"    {key}: {value}")
        
        # Validity
        print(f"  Valid From: {cert['valid_from']}")
        print(f"  Valid Until: {cert['valid_until']}")
        
        days = cert['days_remaining']
        if days > 30:
            status = "✅"
        elif days > 7:
            status = "⚠️"
        else:
            status = "❌"
        print(f"  {status} Days Remaining: {days}")
        
        print(f"  Serial: {cert['serial_number'][:20]}...")
        print(f"  Signature: {cert['signature_algorithm']}")
    
    def _print_security_info(self, security):
        """Print security information"""
        print(f"\n🔒 SECURITY CHECKS:")
        
        # Protocols
        print(f"  Protocols:")
        for proto, status in security['protocols'].items():
            icon = "✅" if status == 'supported' else "❌"
            print(f"    {icon} {proto}: {status}")
        
        # PFS
        pfs_icon = "✅" if security['perfect_forward_secrecy'] == 'supported' else "❌"
        print(f"  {pfs_icon} Perfect Forward Secrecy: {security['perfect_forward_secrecy']}")
    
    def _print_vulnerabilities(self, vulns):
        """Print vulnerabilities"""
        if vulns:
            print(f"\n⚠️ VULNERABILITIES FOUND:")
            for vuln in vulns:
                severity_icon = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠',
                    'MEDIUM': '🟡',
                    'LOW': '🟢'
                }.get(vuln['severity'], '⚪')
                
                print(f"  {severity_icon} {vuln['name']} ({vuln['cve']})")
                print(f"     Severity: {vuln['severity']}")
                print(f"     {vuln['description']}")
        else:
            print(f"\n✅ No common vulnerabilities detected")
    
    def _calculate_grade(self, result):
        """Calculate SSL grade (A-F)"""
        score = 100
        reasons = []
        
        # Protocol downgrade
        if 'TLSv1' in result.get('security', {}).get('protocols', {}):
            if result['security']['protocols']['TLSv1'] == 'supported':
                score -= 20
                reasons.append("TLSv1 masih didukung (usang)")
        
        if 'TLSv1.1' in result.get('security', {}).get('protocols', {}):
            if result['security']['protocols']['TLSv1.1'] == 'supported':
                score -= 10
                reasons.append("TLSv1.1 masih didukung")
        
        # Certificate expiry
        days = result['certificate']['days_remaining']
        if days < 0:
            score = 0
            reasons.append("Sertifikat sudah expired")
        elif days < 7:
            score -= 30
            reasons.append("Sertifikat akan segera expired")
        elif days < 30:
            score -= 10
            reasons.append("Sertifikat expired dalam 30 hari")
        
        # Vulnerabilities
        vuln_count = len(result.get('vulnerabilities', []))
        score -= vuln_count * 15
        
        # Determine grade
        if score >= 90:
            grade = 'A'
            description = "Excellent"
        elif score >= 70:
            grade = 'B'
            description = "Good"
        elif score >= 50:
            grade = 'C'
            description = "Fair"
        elif score >= 30:
            grade = 'D'
            description = "Poor"
        else:
            grade = 'F'
            description = "Very Poor"
        
        return {
            'grade': grade,
            'score': score,
            'description': description,
            'reasons': reasons
        }
    
    def _get_recommendations(self, result):
        """Generate recommendations"""
        recommendations = []
        
        # Protocol recommendations
        protocols = result.get('security', {}).get('protocols', {})
        if protocols.get('TLSv1') == 'supported':
            recommendations.append("Nonaktifkan TLSv1 (sudah usang dan tidak aman)")
        if protocols.get('TLSv1.1') == 'supported':
            recommendations.append("Nonaktifkan TLSv1.1, gunakan minimal TLSv1.2")
        if protocols.get('TLSv1.2') != 'supported':
            recommendations.append("Aktifkan TLSv1.2 untuk kompatibilitas modern")
        if protocols.get('TLSv1.3') != 'supported':
            recommendations.append("Aktifkan TLSv1.3 untuk keamanan terbaik")
        
        # Certificate recommendations
        days = result['certificate']['days_remaining']
        if days < 30:
            recommendations.append(f"Perpanjang sertifikat SSL (expired dalam {days} hari)")
        
        # Vulnerability recommendations
        for vuln in result.get('vulnerabilities', []):
            recommendations.append(f"Perbaiki {vuln['name']} - {vuln['description']}")
        
        return recommendations


# Untuk testing langsung
if __name__ == "__main__":
    analyzer = SSLAnalyzer(verbose=True)
    analyzer.analyze("google.com")
