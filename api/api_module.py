import os
import datetime
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from api.auth import create_api_user, verify_api_key, initialize_api_keys_from_env
from api.csv_handler import process_csv

initialize_api_keys_from_env()

api_blueprint = Blueprint('api', __name__)

UPLOAD_FOLDER = "/upload_csv"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@api_blueprint.route('/create_api_user', methods=['POST'])
def register_api_user():
    data = request.json
    username = data.get("username")

    if not username:
        return jsonify({"error": "請提供使用者名稱"}), 400

    response = create_api_user(username)
    return jsonify(response), 201

@api_blueprint.route('/upload_csv', methods=['POST'])
def upload_csv():
    api_key = request.headers.get("API-Key")

    if not api_key:
        return jsonify({"error": "API Key 缺失"}), 400

    if not verify_api_key(api_key):
        return jsonify({"error": "API Key 無效"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "缺少檔案"}), 400

    file = request.files['file']

    if not file.filename.endswith('.csv'):
        return jsonify({"error": "檔案格式錯誤"}), 400

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"csv_upload_{timestamp}.csv"
    file_path = os.path.join(UPLOAD_FOLDER, secure_filename(filename))

    try:
        file.save(file_path)
        response, status_code = process_csv(file_path)
        return jsonify({"message": "CSV 上傳成功", "file_path": file_path, "database_status": response}), status_code

    except Exception as e:
        return jsonify({"error": f"無法儲存檔案: {str(e)}"}), 500
