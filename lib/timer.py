#!/usr/bin/env python3
# OSXNT - Execution Timer Module
# Track waktu eksekusi

import time
from datetime import timedelta

class Timer:
    """Simple timer untuk tracking execution time"""
    
    def __init__(self, name="Process"):
        self.name = name
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """Start timer"""
        self.start_time = time.time()
        print(f"[*] {self.name} started...")
        return self
    
    def stop(self):
        """Stop timer"""
        if self.start_time:
            self.end_time = time.time()
            elapsed = self.end_time - self.start_time
            print(f"[+] {self.name} completed in {self.format_time(elapsed)}")
            return elapsed
        return 0
    
    def elapsed(self):
        """Get elapsed time without stopping"""
        if self.start_time:
            return time.time() - self.start_time
        return 0
    
    def format_time(self, seconds):
        """Format waktu ke readable string"""
        return str(timedelta(seconds=seconds)).split('.')[0]
    
    def __enter__(self):
        """Context manager entry"""
        return self.start()
    
    def __exit__(self, *args):
        """Context manager exit"""
        self.stop()

def measure_time(func):
    """Decorator untuk measure function execution time"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"[i] {func.__name__} took {end-start:.2f} seconds")
        return result
    return wrapper

# Contoh penggunaan
if __name__ == "__main__":
    # Cara 1: Manual
    timer = Timer("Scanning")
    timer.start()
    time.sleep(2)
    timer.stop()
    
    # Cara 2: Context manager
    with Timer("Processing") as t:
        time.sleep(1.5)
    
    # Cara 3: Decorator
    @measure_time
    def test_function():
        time.sleep(1)
    
    test_function()
