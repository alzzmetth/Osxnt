#!/usr/bin/env python3
# OSXNT - Hash Module
# Generate and verify various hash types

import hashlib
import os
from lib.verbose import Verbose
from lib.file_helper import read_file
from lib.txt_save import save_results  # Pindah ke sini!
from lib.timer import Timer

class HashGenerator:
    """Generate various hash types from string or file"""
    
    # Supported hash algorithms
    ALGORITHMS = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha224': hashlib.sha224,
        'sha256': hashlib.sha256,
        'sha384': hashlib.sha384,
        'sha512': hashlib.sha512,
        'blake2b': hashlib.blake2b,
        'blake2s': hashlib.blake2s,
        'sha3_224': hashlib.sha3_224,
        'sha3_256': hashlib.sha3_256,
        'sha3_384': hashlib.sha3_384,
        'sha3_512': hashlib.sha3_512
    }
    
    def __init__(self, verbose=False):
        self.v = Verbose(verbose)
    
    def hash_string(self, text, algorithm='md5'):
        """Generate hash from string"""
        if algorithm not in self.ALGORITHMS:
            self.v.error(f"Unsupported algorithm: {algorithm}")
            return None
        
        try:
            hash_obj = self.ALGORITHMS[algorithm]()
            hash_obj.update(text.encode('utf-8'))
            result = hash_obj.hexdigest()
            
            self.v.log(f"[+] {algorithm.upper()} hash: {result}")
            return result
            
        except Exception as e:
            self.v.error(f"Error generating hash: {e}")
            return None
    
    def hash_file(self, filename, algorithm='md5', chunk_size=8192):
        """Generate hash from file"""
        if not os.path.exists(filename):
            self.v.error(f"File not found: {filename}")
            return None
        
        if algorithm not in self.ALGORITHMS:
            self.v.error(f"Unsupported algorithm: {algorithm}")
            return None
        
        try:
            hash_obj = self.ALGORITHMS[algorithm]()
            
            with open(filename, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    hash_obj.update(chunk)
            
            result = hash_obj.hexdigest()
            self.v.log(f"[+] {algorithm.upper()} hash of {filename}: {result}")
            return result
            
        except Exception as e:
            self.v.error(f"Error hashing file: {e}")
            return None
    
    def hash_multi(self, text, algorithms=None):
        """Generate multiple hashes at once"""
        if algorithms is None:
            algorithms = ['md5', 'sha1', 'sha256']
        
        results = {}
        for alg in algorithms:
            if alg in self.ALGORITHMS:
                results[alg] = self.hash_string(text, alg)
        
        return results
    
    def hash_directory(self, directory, algorithm='md5'):
        """Hash all files in directory"""
        if not os.path.exists(directory):
            self.v.error(f"Directory not found: {directory}")
            return {}
        
        results = {}
        for root, dirs, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, directory)
                results[rel_path] = self.hash_file(full_path, algorithm)
        
        return results

class HashChecker:
    """Compare and verify hashes"""
    
    def __init__(self, verbose=False):
        self.v = Verbose(verbose)
    
    def verify_string(self, text, expected_hash, algorithm='md5'):
        """Verify if string matches hash"""
        generator = HashGenerator(self.v.enabled)
        calculated = generator.hash_string(text, algorithm)
        
        if calculated and calculated.lower() == expected_hash.lower():
            self.v.log("[✅] Hash matches!")
            return True
        else:
            self.v.log("[❌] Hash does not match")
            return False
    
    def verify_file(self, filename, expected_hash, algorithm='md5'):
        """Verify if file matches hash"""
        generator = HashGenerator(self.v.enabled)
        calculated = generator.hash_file(filename, algorithm)
        
        if calculated and calculated.lower() == expected_hash.lower():
            self.v.log("[✅] File hash matches!")
            return True
        else:
            self.v.log("[❌] File hash does not match")
            return False
    
    def find_matching_file(self, directory, target_hash, algorithm='md5'):
        """Find file matching hash in directory"""
        generator = HashGenerator(self.v.enabled)
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                full_path = os.path.join(root, file)
                file_hash = generator.hash_file(full_path, algorithm)
                
                if file_hash and file_hash.lower() == target_hash.lower():
                    self.v.log(f"[✅] Found match: {full_path}")
                    return full_path
        
        self.v.log("[❌] No matching file found")
        return None

# Main function untuk command line
def hash_main(args):
    """Main function for hash module"""
    v = Verbose(args.verbose)
    generator = HashGenerator(args.verbose)
    checker = HashChecker(args.verbose)
    
    print("\n" + "="*60)
    print("🔐 OSXNT HASH TOOL")
    print("="*60)
    
    if args.text:
        if args.algorithm:
            result = generator.hash_string(args.text, args.algorithm)
        else:
            results = generator.hash_multi(args.text)
            for alg, hash_val in results.items():
                print(f"  {alg.upper()}: {hash_val}")
    
    elif args.file:
        result = generator.hash_file(args.file, args.algorithm or 'md5')
        if result:
            print(f"\n📁 File: {args.file}")
            print(f"🔑 {args.algorithm.upper()}: {result}")
    
    elif args.verify:
        if args.text:
            result = checker.verify_string(args.text, args.hash, args.algorithm or 'md5')
        elif args.file:
            result = checker.verify_file(args.file, args.hash, args.algorithm or 'md5')
    
    elif args.find:
        result = checker.find_matching_file(args.directory, args.hash, args.algorithm or 'md5')
        if result:
            print(f"\n✅ Found: {result}")
