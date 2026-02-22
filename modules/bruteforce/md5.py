#!/usr/bin/env python3
# OSXNT - MD5 Cracker
# Specialized MD5 hash cracker

import hashlib
from .bruteforce import HashCracker
from lib.verbose import Verbose

class MD5Cracker(HashCracker):
    """MD5 hash cracker with optimizations"""
    
    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.algorithm = 'md5'
    
    def crack(self, target_hash, method='auto', wordlist='rockyou'):
        """
        Crack MD5 hash
        
        Args:
            target_hash: MD5 hash to crack
            method: 'wordlist', 'bruteforce', 'hybrid', or 'auto'
            wordlist: wordlist name
        """
        print(f"\n🔓 MD5 Cracker")
        print(f"Target: {target_hash}")
        print("-" * 50)
        
        if method == 'auto':
            # Try wordlist first, then hybrid, then bruteforce
            result = self.crack_wordlist(target_hash, wordlist, 'md5')
            if result:
                return result
            
            result = self.crack_hybrid(target_hash, wordlist, 'md5')
            if result:
                return result
            
            result = self.crack_bruteforce(target_hash, 'md5', max_len=5)
            return result
        
        elif method == 'wordlist':
            return self.crack_wordlist(target_hash, wordlist, 'md5')
        
        elif method == 'hybrid':
            return self.crack_hybrid(target_hash, wordlist, 'md5')
        
        elif method == 'bruteforce':
            return self.crack_bruteforce(target_hash, 'md5', max_len=6)
        
        else:
            self.v.error(f"Unknown method: {method}")
            return None

# Command line function
def md5_main(args):
    """Main function for MD5 cracker"""
    cracker = MD5Cracker(args.verbose)
    
    result = cracker.crack(
        args.hash,
        method=args.method or 'auto',
        wordlist=args.wordlist or 'rockyou'
    )
    
    if result:
        print(f"\n✅ Password found: {result}")
    else:
        print("\n❌ Password not found")
