import json
import secrets
import os
import jwt  # 新增 JWT 套件
from datetime import datetime, timedelta
from dotenv import load_dotenv, set_key
from api.config import Config
from api.logger import logger
# 從 .env 檔案載入環境變數
load_dotenv()

API_KEYS_FILE = os.getenv("API_KEYS_FILE", "api_keys.json")
ENV_FILE = os.getenv("ENV_FILE", ".env")
JWT_SECRET = os.getenv("JWT_SECRET", "your_secret_key")  # 從 .env 取得 JWT 簽名密鑰


def load_api_keys():
    if os.path.exists(API_KEYS_FILE):
        with open(API_KEYS_FILE, "r") as f:
            logger.info("API keys loaded successfully from file.")
            return json.load(f)
    logger.warning("API keys file not found, initializing empty keys.")
    return {}


def save_api_keys(api_keys):
    with open(API_KEYS_FILE, "w") as f:
        json.dump(api_keys, f, indent=4)
    logger.info("API keys saved to file successfully.")

def save_api_key_to_env(username, api_key):
    os.environ[f"API_KEY_{username}"] = api_key
    set_key(ENV_FILE, f"API_KEY_{username}", api_key)
    logger.info(f"API key for user '{username}' saved to environment variables.")


def create_jwt_token(username):
    payload = {
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=1)  # Token 1 小時後過期
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    logger.info(f"JWT token created for user '{username}'.")
    return token


def create_api_user(username, password):
    api_keys = load_api_keys()

    if username in api_keys:
        logger.warning(f"Registration failed: User '{username}' already exists.")
        return {"error": "該使用者已註冊", "api_key": api_keys[username]["api_key"]}

    api_key = secrets.token_hex(32)
    jwt_token = create_jwt_token(username)

    # 保存 API 金鑰和密碼（實際應加密密碼，這裡僅作示範）
    api_keys[username] = {
        "api_key": api_key,
        "password": password,  # 請改用雜氣儲存，如 bcrypt
        "jwt_token": jwt_token
    }

    save_api_key_to_env(username, api_key)
    save_api_keys(api_keys)

    # 將 JWT Token 寫入 token.txt 供前端下載
    with open(f"{username}_token.txt", "w") as token_file:
        token_file.write(jwt_token)
    logger.info(f"User '{username}' registered successfully with API key and JWT token.")
    return {"api_key": api_key, "jwt_token": jwt_token}


def verify_api_key(api_key):
    api_keys = load_api_keys()
    valid = any(user_data["api_key"] == api_key for user_data in api_keys.values())
    if valid:
        logger.info(f"API key verification successful for key: {api_key}")
    else:
        logger.warning(f"API key verification failed for key: {api_key}")
    return valid

def initialize_api_keys_from_env():
    api_keys = load_api_keys()
    for key, value in os.environ.items():
        if key.startswith("API_KEY_"):
            username = key.replace("API_KEY_", "")
            if username not in api_keys:
                api_keys[username] = {"api_key": value}
    save_api_keys(api_keys)
    logger.info("API keys initialized from environment variables.")
