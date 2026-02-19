import json
import os

class Config:
    def __init__(self, config_file='config/config.json'):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}

    def get(self, key, default=None):
        return self.config.get(key, default)

config = Config()
