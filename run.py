from flask import Flask, render_template
from flask_cors import CORS
from api.api_module import api_blueprint
from api.config import Config

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.from_object(Config)

# 啟用 CORS 支援
CORS(app)

# 註冊 API Blueprint
app.register_blueprint(api_blueprint, url_prefix='/api')

# 前端首頁（註冊 API Key）
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
