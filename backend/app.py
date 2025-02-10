from flask import Flask, request, send_from_directory
from config import Config
from models import db
from routes import init_app
from routes.my_logging import setup_logging
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_migrate import Migrate
import os

# 初始化 Flask 应用对象
app = Flask(__name__, static_folder='/root/My_Project/backend/reports')

# 配置应用的设置
app.config.from_object(Config)

# 启用 CORS，允许来自特定来源的请求
CORS(app, resources={r"/*": {"origins": "https://47.98.188.18:8080", "methods": ["GET", "POST", "DELETE", "PUT"]}})

# 初始化 SQLAlchemy 和 Migrate
db.init_app(app)  
migrate = Migrate(app, db)

# 初始化日志
setup_logging(app)

# 初始化 Flask-SocketIO
socketio = SocketIO(app, cors_allowed_origins="https://47.98.188.18:8080")

# 注册蓝图
init_app(app)

# 根路由
@app.route('/')
def index():
    return "Welcome to the homepage!"

# 返回 /reports 目录中的文件
@app.route('/reports/<filename>')
def serve_report(filename):
    # 返回静态文件
    return send_from_directory(os.path.join(app.root_path, 'backend/reports'), filename)

# 处理预检请求
@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        return '', 200  # 预检请求成功返回 200 状态码

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, ssl_context=('server.crt', 'server.key'))