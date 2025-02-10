from flask import Flask, render_template, request
from flask_cors import CORS
from api.api_module import api_blueprint
from api.config import Config
from api.logger import logger  # 導入日誌檔

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)

# 啟用 CORS 支援
CORS(app)

# 注冊 API Blueprint
app.register_blueprint(api_blueprint, url_prefix='/api')

# 前端首頁（註冊 API Key）
@app.route('/')
def home():
    logger.info(f"Homepage accessed from {request.remote_addr}")
    return render_template('index.html')

@app.before_request
def log_request():
    logger.info(f"Incoming request: {request.method} {request.path} from {request.remote_addr}")

@app.teardown_appcontext
def shutdown_log(exception=None):
    logger.info("Flask API server is shutting down.")

@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404 Error: {error} on path {request.path}")
    return {"error": "資源未找到"}, 404

@app.errorhandler(500)
def internal_error(error):
    logger.critical(f"500 Internal Server Error: {error}")
    return {"error": "內部服務器錯誤"}, 500

if __name__ == '__main__':
    logger.info("Flask API server is starting up.")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
