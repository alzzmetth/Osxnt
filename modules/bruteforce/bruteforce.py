#!/usr/bin/env python3
# OSXNT - Bruteforce Engine Core

import itertools
import string
import hashlib
import threading
import time
from queue import Queue
from lib.verbose import Verbose
from lib.timer import Timer
from .wordlist import WordlistManager

class BruteForceEngine:
    """Core bruteforce engine"""
    
    def __init__(self, verbose=False):
        self.v = Verbose(verbose)
        self.found = False
        self.result = None
    
    def brute_force(self, target, callback, charset=None, min_len=1, max_len=8, threads=4):
        """Generic bruteforce function"""
        if charset is None:
            charset = string.ascii_letters + string.digits
        
        self.found = False
        self.result = None
        
        print(f"\n[ Bruteforce Started ]")
        print(f"Target: {target}")
        print(f"Charset: {charset[:20]}... ({len(charset)} chars)")
        print(f"Length: {min_len}-{max_len}")
        print(f"Threads: {threads}")
        print("-" * 50)
        
        total_combinations = sum(len(charset) ** i for i in range(min_len, max_len + 1))
        print(f"Total combinations: {total_combinations:,}")
        
        queue = Queue()
        
        # Fill queue with length ranges
        for length in range(min_len, max_len + 1):
            queue.put(length)
        
        with Timer("Bruteforce"):
            threads_list = []
            for _ in range(threads):
                t = threading.Thread(
                    target=self._worker,
                    args=(queue, charset, callback, target)
                )
                t.daemon = True
                t.start()
                threads_list.append(t)
            
            # Wait for completion
            for t in threads_list:
                t.join(timeout=1)
        
        if self.found:
            print(f"\n✅ Found: {self.result}")
            return self.result
        else:
            print(f"\n❌ Not found in given range")
            return None
    
    def _worker(self, queue, charset, callback, target):
        """Worker thread for bruteforce"""
        while not queue.empty() and not self.found:
            try:
                length = queue.get_nowait()
                self.v.log(f"Trying length {length}...")
                
                for candidate in self._generate_candidates(charset, length):
                    if self.found:
                        break
                    
                    if callback(candidate, target):
                        self.found = True
                        self.result = candidate
                        break
                        
            except:
                break
    
    def _generate_candidates(self, charset, length):
        """Generate all possible combinations"""
        for combo in itertools.product(charset, repeat=length):
            yield ''.join(combo)


class HashCracker:
    """Crack various hash types using wordlist or bruteforce"""
    
    def __init__(self, verbose=False):
        self.v = Verbose(verbose)
        self.engine = BruteForceEngine(verbose)
        self.wordlist_manager = WordlistManager(verbose=verbose)
    
    def hash_function(self, algorithm):
        """Get hash function for algorithm"""
        hash_funcs = {
            'md5': hashlib.md5,
            'sha1': hashlib.sha1,
            'sha256': hashlib.sha256,
            'sha512': hashlib.sha512
        }
        return hash_funcs.get(algorithm)
    
    def crack_wordlist(self, target_hash, wordlist_name, algorithm='md5'):
        """Crack hash using wordlist"""
        hash_func = self.hash_function(algorithm)
        if not hash_func:
            self.v.error(f"Unsupported algorithm: {algorithm}")
            return None
        
        words = self.wordlist_manager.load_wordlist(wordlist_name)
        if not words:
            return None
        
        print(f"\n[ Wordlist Attack ]")
        print(f"Hash: {target_hash}")
        print(f"Algorithm: {algorithm}")
        print(f"Wordlist: {wordlist_name} ({len(words)} words)")
        print("-" * 50)
        
        with Timer("Wordlist attack"):
            for i, word in enumerate(words):
                if i % 10000 == 0 and i > 0:
                    print(f"  Progress: {i}/{len(words)} words")
                
                calculated = hash_func(word.encode()).hexdigest()
                if calculated.lower() == target_hash.lower():
                    print(f"\n✅ Found! Password: {word}")
                    return word
        
        print("\n❌ Not found in wordlist")
        return None
    
    def crack_bruteforce(self, target_hash, algorithm='md5', 
                        charset=None, min_len=1, max_len=6):
        """Crack hash using bruteforce"""
        hash_func = self.hash_function(algorithm)
        if not hash_func:
            self.v.error(f"Unsupported algorithm: {algorithm}")
            return None
        
        def check_password(password, target):
            calculated = hash_func(password.encode()).hexdigest()
            return calculated.lower() == target.lower()
        
        result = self.engine.brute_force(
            target_hash, 
            check_password,
            charset, 
            min_len, 
            max_len
        )
        
        return result
    
    def crack_hybrid(self, target_hash, wordlist_name, algorithm='md5',
                    mutations=True, numbers=True, symbols=True):
        """Hybrid attack: wordlist + mutations"""
        hash_func = self.hash_function(algorithm)
        if not hash_func:
            self.v.error(f"Unsupported algorithm: {algorithm}")
            return None
        
        words = self.wordlist_manager.load_wordlist(wordlist_name)
        if not words:
            return None
        
        print(f"\n[ Hybrid Attack ]")
        print(f"Hash: {target_hash}")
        print(f"Algorithm: {algorithm}")
        print(f"Wordlist: {wordlist_name} ({len(words)} words)")
        print(f"Mutations: numbers={numbers}, symbols={symbols}")
        print("-" * 50)
        
        with Timer("Hybrid attack"):
            for word in words:
                # Original word
                if self._check_hash(word, target_hash, hash_func):
                    return word
                
                if mutations:
                    # Capitalize first letter
                    if self._check_hash(word.capitalize(), target_hash, hash_func):
                        return word.capitalize()
                    
                    # All uppercase
                    if self._check_hash(word.upper(), target_hash, hash_func):
                        return word.upper()
                
                if numbers:
                    # Add numbers
                    for i in range(10):
                        if self._check_hash(f"{word}{i}", target_hash, hash_func):
                            return f"{word}{i}"
                        
                        if self._check_hash(f"{word}{i}{i}", target_hash, hash_func):
                            return f"{word}{i}{i}"
                
                if symbols:
                    # Add common symbols
                    for sym in ['!', '@', '#', '$', '%', '&', '*']:
                        if self._check_hash(f"{word}{sym}", target_hash, hash_func):
                            return f"{word}{sym}"
        
        return None
    
    def _check_hash(self, password, target_hash, hash_func):
        """Check if password matches hash"""
        calculated = hash_func(password.encode()).hexdigest()
        return calculated.lower() == target_hash.lower()
