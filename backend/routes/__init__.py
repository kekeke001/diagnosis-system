# routes/init.py

from .auth import auth_bp
from .model_management import bp as model_management_bp
from .user_management import bp as user_management_bp
from .file_management import bp as file_management_bp
from .data_management import bp as data_management_bp
from .diagnosis import bp as diagnosis_bp
from .report import bp as report_bp

def init_app(app):
    # 不设置前缀，直接注册蓝图
    app.register_blueprint(auth_bp)  # 不设置前缀
    app.register_blueprint(model_management_bp)
    app.register_blueprint(user_management_bp)
    app.register_blueprint(file_management_bp)
    app.register_blueprint(data_management_bp)
    app.register_blueprint(diagnosis_bp)
    app.register_blueprint(report_bp)
