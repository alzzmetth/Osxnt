#!/usr/bin/env python3
# OSXNT - SHA1 Cracker

import hashlib
from .bruteforce import HashCracker

class SHA1Cracker(HashCracker):
    """SHA1 hash cracker"""
    
    def __init__(self, verbose=False):
        super().__init__(verbose)
        self.algorithm = 'sha1'
    
    def crack(self, target_hash, method='auto', wordlist='rockyou'):
        """Crack SHA1 hash"""
        print(f"\n🔓 SHA1 Cracker")
        print(f"Target: {target_hash}")
        print("-" * 50)
        
        if method == 'auto':
            result = self.crack_wordlist(target_hash, wordlist, 'sha1')
            if result:
                return result
            
            result = self.crack_hybrid(target_hash, wordlist, 'sha1')
            return result
        
        return super().crack(target_hash, method, wordlist)

# Command line function
def sha1_main(args):
    """Main function for SHA1 cracker"""
    cracker = SHA1Cracker(args.verbose)
    
    result = cracker.crack(
        args.hash,
        method=args.method or 'auto',
        wordlist=args.wordlist or 'rockyou'
    )
    
    if result:
        print(f"\n✅ Password found: {result}")
    else:
        print("\n❌ Password not found")
