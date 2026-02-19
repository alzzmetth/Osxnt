#!/usr/bin/env python3
# modules/webcode.py

import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from lib.verbose import Verbose
from lib.multi_target import sanitize_filename, process_placeholder

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def download_file(url, dest_dir, verbose=False):
    """Download file dan simpan ke dest_dir, kembalikan path lengkap"""
    v = Verbose(verbose)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        
        # Tentukan nama file dari URL
        path = urlparse(url).path
        filename = os.path.basename(path) if path else 'index.html'
        if not filename or filename.endswith('/'):
            filename = 'index.html'
        # Bersihkan nama
        filename = sanitize_filename(filename)
        if not filename:
            filename = 'index.html'
        
        filepath = os.path.join(dest_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(r.content)
        v.log(f"Downloaded: {url} -> {filepath}")
        return filepath
    except Exception as e:
        v.error(f"Gagal download {url}: {e}")
        return None

def extract_resources(soup, base_url, resource_type):
    """Ekstrak URL resource berdasarkan tipe (css/js)"""
    urls = []
    if resource_type == 'css':
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                urls.append(urljoin(base_url, href))
    elif resource_type == 'js':
        for script in soup.find_all('script', src=True):
            src = script['src']
            urls.append(urljoin(base_url, src))
    return urls

def save_html_content(html_text, dest_dir, verbose=False):
    """Simpan konten HTML ke file"""
    v = Verbose(verbose)
    html_path = os.path.join(dest_dir, 'index.html')
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_text)
        v.log(f"HTML saved: {html_path}")
        return html_path
    except Exception as e:
        v.error(f"Gagal menyimpan HTML: {e}")
        return None

def process_single_target(target, code_types, output_dir_placeholder, verbose=False):
    """
    Proses satu target:
    - target: domain atau URL
    - code_types: list tipe ['html','css','js']
    - output_dir_placeholder: string dengan placeholder $result$ (misal 'package/$result$')
    - verbose: bool
    """
    v = Verbose(verbose)
    
    # Normalisasi URL
    if not target.startswith(('http://', 'https://')):
        target = 'https://' + target
    parsed = urlparse(target)
    domain = parsed.netloc or parsed.path.split('/')[0]
    
    # Tentukan direktori output dengan mengganti placeholder
    output_dir = process_placeholder(output_dir_placeholder, '$result$', domain)
    ensure_dir(output_dir)
    v.log(f"Output directory: {output_dir}")
    
    result = {
        'target': target,
        'domain': domain,
        'output_dir': output_dir,
        'downloaded': []
    }
    
    # Download halaman utama
    try:
        r = requests.get(target, timeout=10)
        r.raise_for_status()
        html_content = r.text
        v.log("Berhasil mengambil halaman utama")
    except Exception as e:
        v.error(f"Gagal mengakses {target}: {e}")
        return None
    
    # Simpan HTML jika diminta
    if 'html' in code_types:
        html_file = save_html_content(html_content, output_dir, verbose)
        if html_file:
            result['downloaded'].append(html_file)
    
    # Parse HTML untuk CSS/JS
    if 'css' in code_types or 'js' in code_types:
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            v.error(f"Gagal parsing HTML: {e}")
            return result
        
        # Download CSS
        if 'css' in code_types:
            css_urls = extract_resources(soup, target, 'css')
            if css_urls:
                css_dir = os.path.join(output_dir, 'css')
                ensure_dir(css_dir)
                for url in css_urls:
                    path = download_file(url, css_dir, verbose)
                    if path:
                        result['downloaded'].append(path)
        
        # Download JS
        if 'js' in code_types:
            js_urls = extract_resources(soup, target, 'js')
            if js_urls:
                js_dir = os.path.join(output_dir, 'js')
                ensure_dir(js_dir)
                for url in js_urls:
                    path = download_file(url, js_dir, verbose)
                    if path:
                        result['downloaded'].append(path)
    
    v.success(f"Selesai memproses {target}. File tersimpan di {output_dir}")
    return result

def process_multi_targets(targets, code_types, output_dir_placeholder, verbose=False):
    """Proses banyak target dari list"""
    results = []
    for target in targets:
        print(f"\n--- Memproses: {target} ---")
        res = process_single_target(target, code_types, output_dir_placeholder, verbose)
        if res:
            results.append(res)
    return results
