#!/usr/bin/env python3
import os
import json

CONFIG_DIR = os.path.expanduser("~/.config/hub")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
DB_FILE = os.path.join(CONFIG_DIR, "hub.db")

DEFAULT_CONFIG = {
    "accounts": {
        "account_1": {
            "name": "Primary Mail",
            "email": "<YOUR_EMAIL_ADDRESS_HERE>",
            "password": "<YOUR_APP_PASSWORD_HERE>",
            "imap_server": "<YOUR_IMAP_SERVER_HERE>",
            "imap_port": 993,
            "smtp_server": "<YOUR_SMTP_SERVER_HERE>",
            "smtp_port": 587,
            "use_ssl": True,
            "use_starttls": True
        },
        "account_2": {
            "name": "Secondary Mail",
            "email": "<YOUR_SECOND_EMAIL_ADDRESS_HERE>",
            "password": "<YOUR_APP_PASSWORD_HERE>",
            "imap_server": "<YOUR_IMAP_SERVER_HERE>",
            "imap_port": 993,
            "smtp_server": "<YOUR_SMTP_SERVER_HERE>",
            "smtp_port": 587,
            "use_ssl": True,
            "use_starttls": True
        }
    },
    "ai": {
        "provider": "lmstudio",
        "lmstudio_endpoint": "http://localhost:1234/v1",
        "local_model": "local-model",
        "local_models_path": "<PATH_TO_YOUR_GGUF_MODELS_DIRECTORY>",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/openai",
        "model": "gemini-2.5-flash",
        "api_key": "<YOUR_API_KEY_HERE>",
        "temperature": 0.2,
        "max_tokens": 1024
    },
    "library": {
        "calibre_metadata_path": "<PATH_TO_YOUR_CALIBRE_METADATA_DB_HERE>"
    },
    "weather": {
        "default_city": "<YOUR_DEFAULT_CITY_HERE>"
    }
}

def load_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        try:
            os.chmod(CONFIG_FILE, 0o600)
        except OSError:
            pass
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        if "weather" not in config:
            config["weather"] = DEFAULT_CONFIG["weather"]
        return config
    except Exception:
        return DEFAULT_CONFIG

def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass
