import os
from urllib.parse import quote_plus

class Config:
    # Flask 密钥
    SECRET_KEY = os.urandom(24)

    # 对数据库密码中的特殊字符进行 URL 编码
    password = quote_plus('Xj20170324#')
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:{password}@localhost/diagnosis'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FILE = './uploads'  # 文件上传路径
    UPLOAD_MODEL = './models'  # 文件上传路径
    REPORT_FOLDER = './reports'  # 报告文件夹
    SECRET_KEY = 'your-secret-key'
    SSL_CERTIFICATE = 'server.crt'  # 证书文件路
    SESSION_TYPE = 'filesystem'  # 设置 Flask Session 存储类型
    SESSION_TYPE = 'filesystem'  # 设置 Flask Session 存储类型
    SESSION_COOKIE_HTTPONLY = True  # 限制 JavaScript 访问 session cookie
    PERMANENT_SESSION_LIFETIME = 3600  # 设置 session 过期时间，单位为秒
    ALLOWED_EXTENSIONS = {'h5', 'pt', 'pkl', 'onnx'}  # 允许的模型文件扩展名


