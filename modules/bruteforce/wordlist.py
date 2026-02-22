#!/usr/bin/env python3
# OSXNT - Wordlist Manager for Bruteforce

import os
import requests
import zipfile
from lib.verbose import Verbose
from lib.file_helper import ensure_dir, get_file_size

class WordlistManager:
    """Manage wordlists for bruteforce attacks"""
    
    # Common wordlist sources
    WORDLISTS = {
        'rockyou': {
            'url': 'https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt',
            'description': 'Most popular password list (14M passwords)',
            'size': '139 MB'
        },
        'common': {
            'url': 'https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-100.txt',
            'description': 'Top 100 common passwords',
            'size': '1 KB'
        },
        'english': {
            'url': 'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt',
            'description': 'English words dictionary',
            'size': '4 MB'
        },
        'names': {
            'url': 'https://raw.githubusercontent.com/dominictarr/random-name/master/first-names.txt',
            'description': 'Common first names',
            'size': '50 KB'
        }
    }
    
    def __init__(self, wordlist_dir='wordlists', verbose=False):
        self.v = Verbose(verbose)
        self.wordlist_dir = wordlist_dir
        ensure_dir(wordlist_dir)
    
    def list_available(self):
        """List available wordlists"""
        print("\n📚 Available Wordlists:")
        print("="*60)
        
        # Built-in lists
        for name, info in self.WORDLISTS.items():
            status = "✅" if self.is_downloaded(name) else "⬇️"
            print(f"{status} {name:<15} - {info['description']} ({info['size']})")
        
        # Custom wordlists
        custom = self.get_custom_wordlists()
        if custom:
            print("\n📁 Custom Wordlists:")
            for wordlist in custom:
                size = get_file_size(os.path.join(self.wordlist_dir, wordlist))
                print(f"  📄 {wordlist} ({size})")
    
    def is_downloaded(self, name):
        """Check if wordlist is downloaded"""
        filename = os.path.join(self.wordlist_dir, f"{name}.txt")
        return os.path.exists(filename)
    
    def get_custom_wordlists(self):
        """Get list of custom wordlists"""
        files = []
        for f in os.listdir(self.wordlist_dir):
            if f.endswith('.txt') and f.replace('.txt', '') not in self.WORDLISTS:
                files.append(f)
        return files
    
    def download(self, name):
        """Download wordlist"""
        if name not in self.WORDLISTS:
            self.v.error(f"Unknown wordlist: {name}")
            return False
        
        info = self.WORDLISTS[name]
        filename = os.path.join(self.wordlist_dir, f"{name}.txt")
        
        if os.path.exists(filename):
            self.v.log(f"Wordlist already exists: {filename}")
            return True
        
        self.v.log(f"Downloading {name} wordlist...")
        self.v.log(f"URL: {info['url']}")
        
        try:
            response = requests.get(info['url'], stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size:
                            percent = (downloaded / total_size) * 100
                            print(f"\rProgress: {percent:.1f}%", end='')
            
            print("\n✅ Download complete!")
            return True
            
        except Exception as e:
            self.v.error(f"Download failed: {e}")
            if os.path.exists(filename):
                os.remove(filename)
            return False
    
    def load_wordlist(self, name):
        """Load wordlist into memory"""
        filename = os.path.join(self.wordlist_dir, f"{name}.txt")
        
        if not os.path.exists(filename):
            self.v.error(f"Wordlist not found: {filename}")
            return []
        
        try:
            with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
                words = [line.strip() for line in f if line.strip()]
            
            self.v.log(f"Loaded {len(words)} words from {name}")
            return words
            
        except Exception as e:
            self.v.error(f"Error loading wordlist: {e}")
            return []
    
    def create_custom(self, filename, words):
        """Create custom wordlist"""
        filepath = os.path.join(self.wordlist_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                for word in words:
                    f.write(word + '\n')
            
            self.v.log(f"Created custom wordlist: {filename}")
            return True
        except Exception as e:
            self.v.error(f"Error creating wordlist: {e}")
            return False
    
    def merge_wordlists(self, output_name, *wordlists):
        """Merge multiple wordlists"""
        all_words = set()
        
        for wl in wordlists:
            words = self.load_wordlist(wl)
            all_words.update(words)
        
        return self.create_custom(output_name, list(all_words))
