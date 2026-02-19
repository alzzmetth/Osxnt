class Verbose:
    def __init__(self, enabled=False):
        self.enabled = enabled

    def log(self, msg):
        if self.enabled:
            print(f"[*] {msg}")

    def error(self, msg):
        print(f"[!] {msg}")

    def success(self, msg):
        print(f"[+] {msg}")
