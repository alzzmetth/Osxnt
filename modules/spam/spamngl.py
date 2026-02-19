#!/usr/bin/env python3
# OSXNT - NGL Spam Module
# Developed by alzzdevmaret

import requests
import random
import time
import hashlib
import uuid
from lib.verbose import Verbose

class NGLSpammer:
    def __init__(self, username, verbose=False):
        """
        Inisialisasi NGL Spammer
        
        Args:
            username (str): Username target (tanpa @)
            verbose (bool): Mode verbose
        """
        self.username = username
        self.v = Verbose(verbose)
        self.base_url = "https://ngl.link"
        self.api_url = "https://ngl.link/api/submit"
        
        # Setup session
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://ngl.link',
            'Referer': f'https://ngl.link/{username}',
            'Connection': 'keep-alive'
        })
        
        self.v.log(f"NGL Spammer initialized for @{username}")
    
    def _generate_device_id(self):
        """Generate random device ID"""
        return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()
    
    def send_message(self, message):
        """
        Kirim satu pesan ke NGL
        
        Args:
            message (str): Pesan yang akan dikirim
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        data = {
            'username': self.username,
            'question': message,
            'deviceId': self._generate_device_id()
        }
        
        try:
            self.v.log(f"Mengirim: {message[:30]}...")
            
            response = self.session.post(self.api_url, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success':
                    self.v.log(f"✅ Pesan terkirim!")
                    return True
                else:
                    error_msg = result.get('message', 'Unknown error')
                    self.v.error(f"Gagal: {error_msg}")
                    
                    if 'rate' in error_msg.lower():
                        self.v.log("Rate limit detected. Waiting 30 seconds...")
                        time.sleep(30)
                    
                    return False
            else:
                self.v.error(f"HTTP Error: {response.status_code}")
                
                if response.status_code == 429:
                    self.v.log("Too many requests. Waiting 60 seconds...")
                    time.sleep(60)
                
                return False
                
        except requests.exceptions.Timeout:
            self.v.error("Timeout - Server lambat")
            return False
        except requests.exceptions.ConnectionError:
            self.v.error("Connection Error - Internet bermasalah")
            return False
        except Exception as e:
            self.v.error(f"Error: {str(e)}")
            return False
    
    def spam(self, message, count=10, delay=1):
        """
        Kirim banyak pesan
        
        Args:
            message (str): Pesan yang akan dikirim
            count (int): Jumlah pesan
            delay (float): Delay antar pesan (detik)
            
        Returns:
            dict: Statistik hasil spam
        """
        print(f"\n[ NGL SPAMMER ]")
        print(f"Target: @{self.username}")
        print(f"Pesan: {message}")
        print(f"Jumlah: {count}")
        print(f"Delay: {delay} detik")
        print("-" * 40)
        
        success = 0
        failed = 0
        
        for i in range(count):
            print(f"[{i+1}/{count}] ", end="")
            
            if self.send_message(message):
                success += 1
            else:
                failed += 1
            
            # Progress bar sederhana
            progress = int((i+1) / count * 20)
            bar = "█" * progress + "░" * (20 - progress)
            print(f" {bar} {i+1}/{count}")
            
            # Delay kecuali pesan terakhir
            if i < count - 1:
                time.sleep(delay)
        
        # Hasil akhir
        print("\n" + "=" * 40)
        print(f"✅ SPAM COMPLETE")
        print(f"   Target: @{self.username}")
        print(f"   Total: {count}")
        print(f"   Berhasil: {success}")
        print(f"   Gagal: {failed}")
        print(f"   Success Rate: {(success/count)*100:.1f}%")
        print("=" * 40)
        
        return {
            'target': self.username,
            'total': count,
            'success': success,
            'failed': failed,
            'message': message
        }
    
    def spam_from_file(self, filename, repeat=1, delay=1):
        """
        Kirim pesan dari file (satu pesan per baris)
        
        Args:
            filename (str): File berisi pesan
            repeat (int): Berapa kali setiap pesan dikirim
            delay (float): Delay antar pesan
        """
        try:
            with open(filename, 'r') as f:
                messages = [line.strip() for line in f if line.strip()]
            
            print(f"\n[ NGL SPAMMER - FILE MODE ]")
            print(f"Target: @{self.username}")
            print(f"File: {filename}")
            print(f"Jumlah pesan unik: {len(messages)}")
            print(f"Repeat per pesan: {repeat}")
            print(f"Total kiriman: {len(messages) * repeat}")
            print("-" * 40)
            
            total_success = 0
            total_failed = 0
            
            for msg_idx, message in enumerate(messages, 1):
                print(f"\n📝 Pesan {msg_idx}/{len(messages)}: {message[:50]}")
                
                for r in range(repeat):
                    print(f"  [{r+1}/{repeat}] ", end="")
                    
                    if self.send_message(message):
                        total_success += 1
                    else:
                        total_failed += 1
                    
                    print()
                    time.sleep(delay)
            
            # Hasil akhir
            total = len(messages) * repeat
            print("\n" + "=" * 40)
            print(f"✅ SPAM FROM FILE COMPLETE")
            print(f"   Target: @{self.username}")
            print(f"   Total: {total}")
            print(f"   Berhasil: {total_success}")
            print(f"   Gagal: {total_failed}")
            print(f"   Success Rate: {(total_success/total)*100:.1f}%")
            print("=" * 40)
            
        except FileNotFoundError:
            self.v.error(f"File {filename} tidak ditemukan")
        except Exception as e:
            self.v.error(f"Error: {e}")
    
    def random_spam(self, theme='random', count=10, delay=1):
        """
        Kirim pesan random berdasarkan tema
        
        Args:
            theme (str): Tema pesan (love, hate, random, scary)
            count (int): Jumlah pesan
            delay (float): Delay antar pesan
        """
        # Template pesan per tema
        templates = {
            'love': [
                "I love you ❤️",
                "You're beautiful 😍",
                "Will you be mine? 💕",
                "I miss you 🥺",
                "You're perfect 💯",
                "I think about you all the time 💭",
                "Can we meet? 👉👈",
                "You're my crush 😳",
                "I like you a lot 💖",
                "You make me happy 😊"
            ],
            'hate': [
                "You're ugly 🤮",
                "Nobody likes you 👎",
                "Go away 🖕",
                "You're annoying 😒",
                "I hate you 💔",
                "You're stupid 🤡",
                "Delete your account 🗑️",
                "You're cringe 😬",
                "Worst person ever 💀",
                "Get a life 💅"
            ],
            'random': [
                "Hello 👋",
                "What's up? 🤙",
                "How are you? 🤔",
                "Nice profile 😎",
                "Follow back 🔙",
                "Check my story 📱",
                "DM me 📨",
                "You're famous 🌟",
                "I'm your fan 🙌",
                "Spam spam spam 🥫"
            ],
            'scary': [
                "I know where you live 🏠",
                "I'm watching you 👀",
                "You're not alone 👻",
                "I'm your biggest fan 🔪",
                "Check behind you... 😱",
                "I see you 👁️",
                "Run... 🏃",
                "You're next ☠️",
                "Boo! 👻",
                "I'm coming for you 💀"
            ]
        }
        
        # Ambil template sesuai tema
        message_templates = templates.get(theme, templates['random'])
        
        print(f"\n[ NGL SPAMMER - RANDOM {theme.upper()} ]")
        print(f"Target: @{self.username}")
        print(f"Tema: {theme}")
        print(f"Jumlah: {count}")
        print("-" * 40)
        
        success = 0
        failed = 0
        
        for i in range(count):
            # Pilih pesan random
            message = random.choice(message_templates)
            
            # Tambah variasi random
            if random.random() > 0.3:
                message += random.choice(['!', '!!', '...', '???', '✨', '🔥'])
            
            print(f"[{i+1}/{count}] {message[:30]}... ", end="")
            
            if self.send_message(message):
                success += 1
            else:
                failed += 1
            
            print()
            time.sleep(delay)
        
        # Hasil akhir
        print("\n" + "=" * 40)
        print(f"✅ RANDOM SPAM COMPLETE")
        print(f"   Target: @{self.username}")
        print(f"   Tema: {theme}")
        print(f"   Total: {count}")
        print(f"   Berhasil: {success}")
        print(f"   Gagal: {failed}")
        print("=" * 40)

# Untuk testing langsung
if __name__ == "__main__":
    # Test sederhana
    spammer = NGLSpammer("testuser", verbose=True)
    spammer.send_message("Hello from OSXNT!")
