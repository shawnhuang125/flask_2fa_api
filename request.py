import requests
import os

# 伺服器 API URL
BASE_URL = "http://localhost:5000/api/upload_csv"

# 讓使用者輸入 CSV 檔案名稱
csv_filename = input("請輸入要上傳的 CSV 檔案名稱（包含副檔名，例如 data.csv）: ").strip()

# 確保 CSV 檔案存在
if not os.path.exists(csv_filename):
    print(f"❌ 錯誤: 檔案 '{csv_filename}' 不存在！請確認後再試。")
    exit()

# 輸入 API Key
api_key = input("請輸入 API Key: ").strip()
headers = {"API-Key": api_key}  # ✅ 確保這裡與 Flask API 端匹配

# 上傳 CSV 檔案
files = {"file": open(csv_filename, "rb")}
response = requests.post(BASE_URL, files=files, headers=headers)

# 處理回應
if response.status_code == 200:
    print(f"✅ CSV 檔案 '{csv_filename}' 成功上傳！伺服器回應: {response.json()}")
else:
    print(f"❌ 上傳失敗: {response.json()}")
