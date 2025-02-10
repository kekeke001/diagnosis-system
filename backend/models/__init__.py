# models/__init__.py
from flask_sqlalchemy import SQLAlchemy

# 初始化数据库对象
db = SQLAlchemy()

from .models import User, File, Model, DiagnosisRecord, Report, DataManagement, db

