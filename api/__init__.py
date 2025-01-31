from flask import Flask
from api.config import Config
from api.api_module import api_blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 註冊 API 路由
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
