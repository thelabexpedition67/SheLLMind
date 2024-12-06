import json
import os

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "config.json")

DEFAULT_CONFIG = {
    "ollama_host": "http://127.0.0.1:11434",  # Default host for Ollama
    "model_name": "",          # Default model name
    "typewriter_speed": 1      # Default typewriter speed
}

class Config:
    def __init__(self):
        self._ensure_config_file()
        self._data = self._load_config()

    def _ensure_config_file(self):
        # Check if the config file exists
        if not os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "w") as f:
                # Create the file with default values
                json.dump(DEFAULT_CONFIG, f, indent=4)

    def _load_config(self):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

    @property
    def ollama_host(self):
        return self._data.get("ollama_host")

    @property
    def model_name(self):
        return self._data.get("model_name")

    @property
    def typewriter_speed(self):
        return self._data.get("typewriter_speed", 1)
    
    def set_config(self, key, value):
        self._data[key] = value
        self._save_config()

    def _save_config(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self._data, f, indent=4)