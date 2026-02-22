#!/usr/bin/env python3
# OSXNT - Encode/Decode Module
# Base64, Base32, Base16, etc.

import base64
import codecs
from lib.verbose import Verbose

class Encoder:
    """Various encoding functions"""
    
    def __init__(self, verbose=False):
        self.v = Verbose(verbose)
    
    def base64_encode(self, text):
        """Encode to Base64"""
        try:
            if isinstance(text, str):
                text = text.encode('utf-8')
            result = base64.b64encode(text).decode('utf-8')
            self.v.log(f"[+] Base64: {result}")
            return result
        except Exception as e:
            self.v.error(f"Base64 encode error: {e}")
            return None
    
    def base32_encode(self, text):
        """Encode to Base32"""
        try:
            if isinstance(text, str):
                text = text.encode('utf-8')
            result = base64.b32encode(text).decode('utf-8')
            self.v.log(f"[+] Base32: {result}")
            return result
        except Exception as e:
            self.v.error(f"Base32 encode error: {e}")
            return None
    
    def base16_encode(self, text):
        """Encode to Base16 (hex)"""
        try:
            if isinstance(text, str):
                text = text.encode('utf-8')
            result = base64.b16encode(text).decode('utf-8')
            self.v.log(f"[+] Base16: {result}")
            return result
        except Exception as e:
            self.v.error(f"Base16 encode error: {e}")
            return None
    
    def base85_encode(self, text):
        """Encode to Base85"""
        try:
            if isinstance(text, str):
                text = text.encode('utf-8')
            result = base64.b85encode(text).decode('utf-8')
            self.v.log(f"[+] Base85: {result}")
            return result
        except Exception as e:
            self.v.error(f"Base85 encode error: {e}")
            return None
    
    def rot13_encode(self, text):
        """ROT13 encoding"""
        try:
            result = codecs.encode(text, 'rot_13')
            self.v.log(f"[+] ROT13: {result}")
            return result
        except Exception as e:
            self.v.error(f"ROT13 error: {e}")
            return None
    
    def url_encode(self, text):
        """URL encoding"""
        try:
            from urllib.parse import quote
            result = quote(text)
            self.v.log(f"[+] URL Encode: {result}")
            return result
        except Exception as e:
            self.v.error(f"URL encode error: {e}")
            return None

class Decoder:
    """Various decoding functions"""
    
    def __init__(self, verbose=False):
        self.v = Verbose(verbose)
    
    def base64_decode(self, encoded):
        """Decode from Base64"""
        try:
            if isinstance(encoded, str):
                encoded = encoded.encode('utf-8')
            # Add padding if needed
            while len(encoded) % 4 != 0:
                encoded += b'='
            result = base64.b64decode(encoded).decode('utf-8', errors='ignore')
            self.v.log(f"[+] Decoded: {result}")
            return result
        except Exception as e:
            self.v.error(f"Base64 decode error: {e}")
            return None
    
    def base32_decode(self, encoded):
        """Decode from Base32"""
        try:
            if isinstance(encoded, str):
                encoded = encoded.encode('utf-8')
            result = base64.b32decode(encoded).decode('utf-8', errors='ignore')
            self.v.log(f"[+] Decoded: {result}")
            return result
        except Exception as e:
            self.v.error(f"Base32 decode error: {e}")
            return None
    
    def base16_decode(self, encoded):
        """Decode from Base16 (hex)"""
        try:
            if isinstance(encoded, str):
                encoded = encoded.encode('utf-8')
            result = base64.b16decode(encoded).decode('utf-8', errors='ignore')
            self.v.log(f"[+] Decoded: {result}")
            return result
        except Exception as e:
            self.v.error(f"Base16 decode error: {e}")
            return None
    
    def base85_decode(self, encoded):
        """Decode from Base85"""
        try:
            if isinstance(encoded, str):
                encoded = encoded.encode('utf-8')
            result = base64.b85decode(encoded).decode('utf-8', errors='ignore')
            self.v.log(f"[+] Decoded: {result}")
            return result
        except Exception as e:
            self.v.error(f"Base85 decode error: {e}")
            return None
    
    def rot13_decode(self, encoded):
        """ROT13 decoding (same as encoding)"""
        try:
            result = codecs.encode(encoded, 'rot_13')
            self.v.log(f"[+] Decoded: {result}")
            return result
        except Exception as e:
            self.v.error(f"ROT13 error: {e}")
            return None
    
    def url_decode(self, encoded):
        """URL decoding"""
        try:
            from urllib.parse import unquote
            result = unquote(encoded)
            self.v.log(f"[+] Decoded: {result}")
            return result
        except Exception as e:
            self.v.error(f"URL decode error: {e}")
            return None
    
    def auto_decode(self, encoded):
        """Try to auto-detect and decode"""
        results = {}
        
        # Try Base64
        try:
            decoded = self.base64_decode(encoded)
            if decoded and not any(c in decoded for c in '\x00\x01\x02\x03'):
                results['base64'] = decoded
        except:
            pass
        
        # Try Base32
        try:
            decoded = self.base32_decode(encoded)
            if decoded and not any(c in decoded for c in '\x00\x01\x02\x03'):
                results['base32'] = decoded
        except:
            pass
        
        # Try ROT13
        try:
            decoded = self.rot13_decode(encoded)
            if decoded != encoded:
                results['rot13'] = decoded
        except:
            pass
        
        return results

# Main function untuk command line
def encode_main(args):
    """Main function for encode/decode module"""
    encoder = Encoder(args.verbose)
    decoder = Decoder(args.verbose)
    
    print("\n" + "="*60)
    print("🔐 OSXNT ENCODE/DECODE TOOL")
    print("="*60)
    
    if args.encode:
        if args.type == 'base64':
            result = encoder.base64_encode(args.text)
        elif args.type == 'base32':
            result = encoder.base32_encode(args.text)
        elif args.type == 'base16':
            result = encoder.base16_encode(args.text)
        elif args.type == 'base85':
            result = encoder.base85_encode(args.text)
        elif args.type == 'rot13':
            result = encoder.rot13_encode(args.text)
        elif args.type == 'url':
            result = encoder.url_encode(args.text)
        
        if result:
            print(f"\n✅ Encoded: {result}")
    
    elif args.decode:
        if args.type == 'base64':
            result = decoder.base64_decode(args.text)
        elif args.type == 'base32':
            result = decoder.base32_decode(args.text)
        elif args.type == 'base16':
            result = decoder.base16_decode(args.text)
        elif args.type == 'base85':
            result = decoder.base85_decode(args.text)
        elif args.type == 'rot13':
            result = decoder.rot13_decode(args.text)
        elif args.type == 'url':
            result = decoder.url_decode(args.text)
        elif args.type == 'auto':
            results = decoder.auto_decode(args.text)
            if results:
                print("\n✅ Possible decodings:")
                for method, decoded in results.items():
                    print(f"  {method}: {decoded}")
            else:
                print("❌ No decoding found")
        
        if result and args.type != 'auto':
            print(f"\n✅ Decoded: {result}")
