import os
import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from api.auth import create_api_user, verify_api_key, initialize_api_keys_from_env
from api.csv_handler import process_csv

# 初始化 API 金鑰
initialize_api_keys_from_env()

# 建立 API Blueprint
api_blueprint = Blueprint('api', __name__)

# 設定檔案上傳資料夾
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'upload_csv')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@api_blueprint.route('/create_api_user', methods=['POST'])
def register_api_user():
    
    # 註冊新的 API 使用者，並返回 API 金鑰。
    
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "請提供使用者名稱"}), 400

    response = create_api_user(username)
    return jsonify(response), 201

@api_blueprint.route('/upload_csv', methods=['POST'])
def upload_csv():
    """
    上傳 CSV 檔案，並將其匯入資料庫。
    """
    api_key = request.headers.get("API-Key")

    # 檢查 API 金鑰
    if not api_key:
        return jsonify({"error": "API Key 缺失"}), 400

    if not verify_api_key(api_key):
        return jsonify({"error": "API Key 無效"}), 403

    # 檢查檔案是否存在
    if 'file' not in request.files:
        return jsonify({"error": "缺少檔案"}), 400

    file = request.files['file']

    # 檢查檔案格式是否為 CSV
    if not file.filename.endswith('.csv'):
        return jsonify({"error": "檔案格式錯誤，請上傳 .csv 檔案"}), 400

    # 生成唯一檔案名稱
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    username = api_key[:5]  # 使用 API 金鑰的前 5 位做識別
    filename = f"{username}_csv_upload_{timestamp}.csv"
    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))

    try:
        # 儲存檔案到 /upload_csv 資料夾
        file.save(file_path)
        print(f"檔案已成功儲存至 {file_path}")

        # 處理 CSV 檔案，並匯入資料庫
        response, status_code = process_csv(file_path)

        # 處理資料庫匯入結果
        if status_code != 200:
            return jsonify({
                "message": "CSV 上傳成功，但匯入資料庫失敗",
                "file_path": file_path,
                "database_status": response
            }), status_code

        return jsonify({
            "message": "CSV 上傳並成功匯入資料庫",
            "file_path": file_path,
            "database_status": response
        }), 200

    except Exception as e:
        print(f"檔案儲存失敗: {e}")
        return jsonify({"error": f"無法儲存檔案: {str(e)}"}), 500
