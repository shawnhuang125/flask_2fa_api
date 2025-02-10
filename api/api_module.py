import os
import datetime
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from api.auth import create_api_user, verify_api_key, initialize_api_keys_from_env
from api.logger import logger  # 導入日誌檔

# 初始化 API 金鑰
initialize_api_keys_from_env()

# 建立 API Blueprint
api_blueprint = Blueprint('api', __name__)

@api_blueprint.before_request
def log_request_info():
    logger.info(f"Received {request.method} request on {request.path} from {request.remote_addr}")

@api_blueprint.route('/create_api_user', methods=['POST'])
def register_api_user():
    """
    註冊新的 API 使用者，並返回 JWT Token，將 Token 儲存到 token.txt
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        logger.warning(f"Failed registration attempt: Missing username or password from {request.remote_addr}")
        return jsonify({"error": "請提供使用者名稱和密碼"}), 400

    response = create_api_user(username, password)

    if "error" in response:
        logger.error(f"Registration failed for user '{username}': {response['error']}")
        return jsonify(response), 400

    # 將使用者資訊和 JWT Token 寫入 token.txt
    token_content = f"Username: {username}\nPassword: {password}\nJWT Token: {response['jwt_token']}"
    with open(f"{username}_token.txt", "w") as token_file:
        token_file.write(token_content)

    logger.info(f"User '{username}' registered successfully.")
    return jsonify({"message": "註冊成功"}), 201

@api_blueprint.route('/download_token/<username>', methods=['GET'])
def download_token(username):
    """
    下載指定使用者的 JWT Token （token.txt）
    """
    token_file = f"{username}_token.txt"
    if os.path.exists(token_file):
        logger.info(f"Token file for user '{username}' downloaded successfully.")
        return send_file(token_file, as_attachment=True)
    logger.warning(f"Token file for user '{username}' not found.")
    return jsonify({"error": "找不到 Token 檔案"}), 404

@api_blueprint.route('/verify_key', methods=['GET'])
def verify_key():
    """
    驗證 API Key 是否有效，從請求 Header 中取得 X-API-KEY 進行驗證
    """
    api_key = request.headers.get('X-API-KEY')  # 從請求的 Header 取得 API Key

    if verify_api_key(api_key):
        logger.info(f"API Key verification successful for key: {api_key}")
        return jsonify({"message": "API Key 驗證成功"}), 200
    else:
        logger.warning(f"API Key verification failed for key: {api_key}")
        return jsonify({"error": "API Key 無效"}), 401

