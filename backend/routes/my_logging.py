import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    # 创建日志目录
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    # 设置日志文件和格式
    log_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    log_handler.setLevel(logging.INFO)
    log_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))

    # 将日志处理器添加到 Flask 应用
    app.logger.addHandler(log_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Logging is set up")
