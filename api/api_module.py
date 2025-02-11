import os
import datetime
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from api.auth import create_api_user, verify_api_key, initialize_api_keys_from_env,verify_jwt_token  
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
    註冊新的 API 使用者，並返回 JWT Token，將 Token 儲存到 token.txt，
    並回傳 API Key 和 JWT Token 到前端
    """
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        logger.warning(f"Failed registration attempt: Missing username or password from {request.remote_addr}")
        return jsonify({"error": "Please Provide Username And Password"}), 400

    response = create_api_user(username, password)

    if "error" in response:
        logger.error(f"Registration failed for user '{username}': {response['error']}")
        return jsonify(response), 400

    # 將使用者資訊和 JWT Token 寫入 token.txt
    token_content = f"Username: {username}\nPassword: {password}\nJWT Token: {response['jwt_token']}"
    with open(f"{username}_token.txt", "w") as token_file:
        token_file.write(token_content)

    logger.info(f"User '{username}' registered successfully.")

    # 保留原有註冊成功訊息，同時回傳 API Key 和 JWT Token 給前端
    return jsonify({
        "message": "Register Successful",
        "api_key": response["api_key"],
        "jwt_token": response["jwt_token"]
    }), 201


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
    return jsonify({"error": "Can Not Find Token File"}), 404

@api_blueprint.route('/verify_key', methods=['GET'])
def verify_key():
    """
    驗證 API Key 是否有效，從請求 Header 中取得 X-API-KEY 進行驗證
    """
    api_key = request.headers.get('X-API-KEY')  # 從請求的 Header 取得 API Key

    if verify_api_key(api_key):
        logger.info(f"API Key verification successful for key: {api_key}")
        return jsonify({"message": "API Key Verification Seccessful"}), 200
    else:
        logger.warning(f"API Key verification failed for key: {api_key}")
        return jsonify({"error": "unknown API Key"}), 401



@api_blueprint.route('/verify_token', methods=['POST'])
def verify_token():
    """
    驗證 JWT Token 是否有效，從請求 Header 中取得 Authorization Bearer Token。
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        logger.warning(f"Token verification failed: No valid Authorization header from {request.remote_addr}")
        return jsonify({"error": "Please privide available Authorization Bearer Token"}), 400

    token = auth_header.split(" ")[1]  # 提取 Token
    result = verify_jwt_token(token)

    if result["valid"]:
        return jsonify({"message": "JWT Token Verification Seccessful", "username": result["username"]}), 200
    else:
        return jsonify({"error": result["error"]}), 401
    


@api_blueprint.route('/download_api_key/<username>', methods=['GET'])
def download_api_key(username):
    """
    下載指定使用者的 API Key（api_key.txt）
    """
    api_key_file = f"{username}_api_key.txt"
    if os.path.exists(api_key_file):
        logger.info(f"API Key file for user '{username}' downloaded successfully.")
        return send_file(api_key_file, as_attachment=True)
    logger.warning(f"API Key file for user '{username}' not found.")
    return jsonify({"error": "Can Not Find Api Key File"}), 404
