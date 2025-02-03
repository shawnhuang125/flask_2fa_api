import os
from dotenv import load_dotenv

# 載入 .env 環境變數
load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG", "True") == "True"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 5000))

    # MySQL 設定
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))  
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "yourpassword")
    DB_NAME = os.getenv("DB_NAME", "csv_database")

    # API Key 存儲設定
    API_KEY_STORAGE = os.getenv("API_KEY_STORAGE", "json")
    API_KEY_FILE = os.getenv("API_KEY_FILE", "api_keys.json")
