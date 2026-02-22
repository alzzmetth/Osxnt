#!/usr/bin/env python3
# OSXNT - SHA256 Cracker

import hashlib
from .bruteforce import HashCracker
from lib.verbose import Verbose

class SHA256Cracker(HashCracker):
    """SHA256 hash cracker"""
    
    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.algorithm = 'sha256'
    
    def crack(self, target_hash, method='auto', wordlist='rockyou'):
        """
        Crack SHA256 hash
        """
        print(f"\n🔓 SHA256 Cracker")
        print(f"Target: {target_hash}")
        print("-" * 50)
        
        if method == 'auto':
            # SHA256 is slower, try wordlist first
            result = self.crack_wordlist(target_hash, wordlist, 'sha256')
            if result:
                return result
            
            # Hybrid with limited mutations
            result = self.crack_hybrid(target_hash, wordlist, 'sha256', 
                                       mutations=True, numbers=True, symbols=False)
            return result
        
        elif method == 'wordlist':
            return self.crack_wordlist(target_hash, wordlist, 'sha256')
        
        elif method == 'hybrid':
            return self.crack_hybrid(target_hash, wordlist, 'sha256')
        
        elif method == 'bruteforce':
            # Bruteforce SHA256 is VERY slow, limit to 5 chars
            self.v.log("Warning: Bruteforce SHA256 will be very slow!")
            return self.crack_bruteforce(target_hash, 'sha256', max_len=5)
        
        else:
            self.v.error(f"Unknown method: {method}")
            return None

# Command line function
def sha256_main(args):
    """Main function for SHA256 cracker"""
    cracker = SHA256Cracker(args.verbose)
    
    result = cracker.crack(
        args.hash,
        method=args.method or 'auto',
        wordlist=args.wordlist or 'rockyou'
    )
    
    if result:
        print(f"\n✅ Password found: {result}")
    else:
        print("\n❌ Password not found")
