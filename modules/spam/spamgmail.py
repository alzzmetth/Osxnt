#!/usr/bin/env python3
# OSXNT - Gmail Spam Module
# Developed by alzzdevmaret
# CATATAN: Ini hanya simulasi, tidak mengirim email sungguhan

import time
import random
from lib.verbose import Verbose

class GmailSpammer:
    def __init__(self, verbose=False):
        """
        Inisialisasi Gmail Spammer Simulasi
        
        Args:
            verbose (bool): Mode verbose
        """
        self.v = Verbose(verbose)
        self.v.log("Gmail Spammer initialized (SIMULATION MODE)")
    
    def send_email(self, to_email, subject, body):
        """
        SIMULASI: Kirim satu email
        
        Args:
            to_email (str): Email target
            subject (str): Subjek email
            body (str): Isi email
            
        Returns:
            bool: Selalu True (simulasi)
        """
        self.v.log(f"📧 SIMULASI: Mengirim email ke {to_email}")
        self.v.log(f"   Subject: {subject[:30]}...")
        self.v.log(f"   Body: {body[:50]}...")
        
        # Simulasi proses
        time.sleep(1)
        
        print(f"✅ [SIMULASI] Email terkirim ke {to_email}")
        return True
    
    def spam(self, to_email, subject, body, count=10, delay=1):
        """
        SIMULASI: Kirim banyak email
        
        Args:
            to_email (str): Email target
            subject (str): Subjek email
            body (str): Isi email
            count (int): Jumlah email
            delay (float): Delay antar email
        """
        print(f"\n[ GMAIL SPAMMER - SIMULASI ]")
        print(f"Target: {to_email}")
        print(f"Subject: {subject}")
        print(f"Jumlah: {count}")
        print(f"Delay: {delay} detik")
        print("=" * 40)
        print("⚠️  INI HANYA SIMULASI - TIDAK MENGIRIM EMAIL SUNGGAHAN")
        print("=" * 40)
        
        for i in range(count):
            print(f"[{i+1}/{count}] Mengirim email ke {to_email}...")
            self.send_email(to_email, subject, body)
            
            if i < count - 1:
                print(f"   Menunggu {delay} detik...")
                time.sleep(delay)
        
        print("\n" + "=" * 40)
        print(f"✅ SIMULASI SPAM SELESAI")
        print(f"   Target: {to_email}")
        print(f"   Total: {count}")
        print("=" * 40)
    
    def spam_from_file(self, to_email, subject_file, body_file=None, count=10, delay=1):
        """
        SIMULASI: Kirim email dengan subject/body dari file
        
        Args:
            to_email (str): Email target
            subject_file (str): File berisi subject
            body_file (str): File berisi body
            count (int): Jumlah email
            delay (float): Delay antar email
        """
        # Baca subject
        try:
            with open(subject_file, 'r') as f:
                subjects = [line.strip() for line in f if line.strip()]
        except:
            subjects = ["Test Subject"]
        
        # Baca body
        if body_file:
            try:
                with open(body_file, 'r') as f:
                    bodies = [line.strip() for line in f if line.strip()]
            except:
                bodies = ["Test Body"]
        else:
            bodies = ["This is a test email from OSXNT"]
        
        print(f"\n[ GMAIL SPAMMER - FILE MODE - SIMULASI ]")
        print(f"Target: {to_email}")
        print(f"Subject file: {subject_file}")
        print(f"Body file: {body_file or 'Default'}")
        print(f"Jumlah: {count}")
        print("=" * 40)
        print("⚠️  INI HANYA SIMULASI - TIDAK MENGIRIM EMAIL SUNGGAHAN")
        print("=" * 40)
        
        for i in range(count):
            subject = random.choice(subjects)
            body = random.choice(bodies)
            
            print(f"[{i+1}/{count}] Simulasi kirim: {subject[:30]}...")
            time.sleep(0.5)  # Simulasi proses
            print(f"   ✅ [SIMULASI] Terkirim")
            
            if i < count - 1:
                time.sleep(delay)
        
        print("\n" + "=" * 40)
        print(f"✅ SIMULASI SPAM FILE SELESAI")
        print(f"   Total: {count}")
        print("=" * 40)
    
    def generate_spam(self, to_email, theme='random', count=10, delay=1):
        """
        SIMULASI: Generate dan kirim spam random
        
        Args:
            to_email (str): Email target
            theme (str): Tema spam
            count (int): Jumlah email
            delay (float): Delay antar email
        """
        subjects = {
            'random': ["Hello", "Hi", "Check this out", "Important", "Urgent"],
            'promo': ["DISKON 50%", "SALE TODAY", "Limited Offer", "Flash Sale"],
            'scam': ["You Won!", "Congratulations", "Claim Prize", "Inheritance"],
            'love': ["I Love You", "Miss You", "Be Mine", "Romantic"]
        }
        
        bodies = {
            'random': ["Just saying hi", "How are you?", "Long time no see"],
            'promo': ["Buy now!", "Limited stock", "Don't miss out"],
            'scam': ["Click here to claim", "Transfer fee required", "Urgent response"],
            'love': ["Thinking of you", "You're special", "Can we meet?"]
        }
        
        subj_list = subjects.get(theme, subjects['random'])
        body_list = bodies.get(theme, bodies['random'])
        
        print(f"\n[ GMAIL SPAMMER - GENERATE {theme.upper()} - SIMULASI ]")
        print(f"Target: {to_email}")
        print(f"Tema: {theme}")
        print(f"Jumlah: {count}")
        print("=" * 40)
        print("⚠️  INI HANYA SIMULASI - TIDAK MENGIRIM EMAIL SUNGGAHAN")
        print("=" * 40)
        
        for i in range(count):
            subject = random.choice(subj_list)
            body = random.choice(body_list)
            
            print(f"[{i+1}/{count}] Generate: {subject}")
            print(f"   Body: {body}")
            print(f"   ✅ [SIMULASI] Terkirim ke {to_email}")
            
            if i < count - 1:
                time.sleep(delay)
        
        print("\n" + "=" * 40)
        print(f"✅ GENERATE SPAM SELESAI")
        print(f"   Total: {count}")
        print("=" * 40)

# Untuk testing langsung
if __name__ == "__main__":
    # Test simulasi
    spammer = GmailSpammer(verbose=True)
    spammer.spam("target@gmail.com", "Hello", "Test Body", count=3)
