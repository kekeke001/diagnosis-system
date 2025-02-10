from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# 用户模型
class User(db.Model):
    __tablename__ = 'Users'  # 显式指定表名为 'Users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime)
    role = db.Column(db.Enum('admin', 'user', name='role_enum'), nullable=False)

# 文件模型
class File(db.Model):
    __tablename__ = 'Files'  # 显式指定表名为 'Files'
    
    file_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'), nullable=True)  # 关联 Users 表
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_format = db.Column(db.String(50))
    file_size = db.Column(db.String(50)) 
    upload_time = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def __repr__(self):
        return f'<File {self.file_name}>'

# 模型表
class Model(db.Model):
    __tablename__ = 'Models'  # 显式指定表名为 'Models'
    
    model_id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(255))
    model_size = db.Column(db.String(50))  # size 字段
    model_path = db.Column(db.String(255))
    upload_time = db.Column(db.DateTime, default=db.func.current_timestamp())  # 默认当前时间

    def __repr__(self):
        return f'<Model {self.model_name}>'

# 诊断记录表
class DiagnosisRecord(db.Model):
    __tablename__ = 'Diagnosis_Records'  # 显式指定表名为 'Diagnosis_Records'
    
    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 诊断记录ID
    file_id = db.Column(db.Integer, db.ForeignKey('Files.file_id'))  # 关联的文件ID
    model_id = db.Column(db.Integer, db.ForeignKey('Models.model_id'))  # 关联的模型ID
    diagnosis_result = db.Column(db.Text)  # 诊断结果
    tsne_path = db.Column(db.String(255))  # 存储 t-SNE 图的路径
    confusion_matrix_path = db.Column(db.String(255))  # 存储混淆矩阵图的路径
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    
    # 可选：定义与 Report 的关系
    report_id = db.Column(db.Integer, db.ForeignKey('Reports.report_id'))
    report = db.relationship('Report', back_populates='diagnosis_record')  # Establish relationship with Report
    
    # Relationship to File model
    file = db.relationship('File', backref='diagnosis_records', uselist=False)

    def __repr__(self):
        return f'<DiagnosisRecord {self.record_id} - {self.diagnosis_result}>'

# 报告表
class Report(db.Model):
    __tablename__ = 'Reports'  # 显式指定表名为 'Reports'
    
    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 报告ID
    report_name = db.Column(db.String(255))  # 报告名称
    report_format = db.Column(db.String(50))  # 报告格式（可以为PDF, HTML等）
    report_path = db.Column(db.String(255), nullable=False)  # 报告保存路径
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    
    # Back relationship to DiagnosisRecord
    diagnosis_record = db.relationship('DiagnosisRecord', back_populates='report', uselist=False)

    def __repr__(self):
        return f'<Report {self.report_name}>'




# 数据管理表
class DataManagement(db.Model):
    __tablename__ = 'Data_Management'  # 显式指定表名为 'Data_Management'
    
    data_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    data_type = db.Column(db.Enum('file', 'model', name='data_type_enum'), nullable=False)
    data_id_related = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.user_id'))  # 关联 Users 表
    upload_time = db.Column(db.DateTime, default=db.func.current_timestamp())  # 默认当前时间
