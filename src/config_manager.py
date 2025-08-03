import json
import os

class ConfigManager:
    def __init__(self, filename="config.json"):
        self.filename = filename
        self.config = {}
        self.load()

    def load(self):
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def save(self):
        with open(self.filename, "w") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()