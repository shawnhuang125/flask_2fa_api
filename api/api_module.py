import os
import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from api.auth import create_api_user, verify_api_key, initialize_api_keys_from_env

# 初始化 API 金鑰
initialize_api_keys_from_env()

# 建立 API Blueprint
api_blueprint = Blueprint('api', __name__)


@api_blueprint.route('/create_api_user', methods=['POST'])
def register_api_user():
    
    # 註冊新的 API 使用者，並返回 API 金鑰。
    
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "請提供使用者名稱"}), 400

    response = create_api_user(username)
    return jsonify(response), 201

@api_blueprint.route('/verify_key', methods=['GET'])
def verify_key():
    api_key = request.headers.get('X-API-KEY')  # 從請求的 Header 取得 API Key

    if verify_api_key(api_key):  # 使用 auth.py 中的函數驗證 API Key
        return jsonify({"message": "API Key verify successed"}), 200
    else:
        return jsonify({"error": "API Key 無效"}), 401
