def read_targets_from_file(filename):
    """Read list of targets from a file (one per line)"""
    targets = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    targets.append(line)
        return targets
    except FileNotFoundError:
        print(f"[!] File {filename} not found")
        return None
    except Exception as e:
        print(f"[!] Error reading file: {e}")
        return None
