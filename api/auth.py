import json
import secrets
import os
from dotenv import load_dotenv, set_key
from api.config import Config

API_KEYS_FILE = "api_keys.json"
ENV_FILE = ".env"

# 載入 .env
load_dotenv()

def load_api_keys():
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_api_keys(api_keys):
    with open(API_KEYS_FILE, "w") as f:
        json.dump(api_keys, f, indent=4)

def save_api_key_to_env(username, api_key):
    os.environ[f"API_KEY_{username}"] = api_key
    set_key(ENV_FILE, f"API_KEY_{username}", api_key)

def create_api_user(username):
    api_keys = load_api_keys()

    if username in api_keys:
        return {"error": "該使用者已註冊", "api_key": api_keys[username]}

    api_key = secrets.token_hex(32)
    api_keys[username] = api_key

    save_api_key_to_env(username, api_key)
    save_api_keys(api_keys)

    return {"api_key": api_key}

def verify_api_key(api_key):
    api_keys = load_api_keys()
    return api_key in api_keys.values()

def initialize_api_keys_from_env():
    api_keys = load_api_keys()
    for key, value in os.environ.items():
        if key.startswith("API_KEY_"):
            username = key.replace("API_KEY_", "")
            if username not in api_keys:
                api_keys[username] = value
    save_api_keys(api_keys)
