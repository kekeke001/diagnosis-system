from flask import Blueprint
from .auth import login, register
from .user_management import get_users, delete_user, update_last_login, get_current_user
from .model_management import upload_model, get_models, delete_model, check_model_exists
from .file_management import upload_file, get_files, delete_file, check_file_exists
from .data_management import get_data_records
from .diagnosis import get_files,get_models,diagnose
from .report import get_diagnosis_records,delete_diagnosis_record

bp = Blueprint('main', __name__)

# 用户相关路由
bp.add_url_rule('/login', 'login', login, methods=['POST'])
bp.add_url_rule('/register', 'register', register, methods=['POST'])
bp.add_url_rule('/users/api/users', 'get_users', get_users, methods=['GET'])
bp.add_url_rule('/users/api/users/<int:user_id>', 'delete_user', delete_user, methods=['DELETE'])
bp.add_url_rule('/users/api/users/login/<int:user_id>', 'update_last_login', update_last_login, methods=['PUT'])
bp.add_url_rule('/users/api/current_user', 'get_current_user', get_current_user, methods=['GET'])

# 模型管理相关路由
bp.add_url_rule('/upload_model', 'upload_model', upload_model, methods=['POST'])
bp.add_url_rule('/get_models', 'get_models', get_models, methods=['GET'])  
bp.add_url_rule('/delete_model/<int:model_id>', 'delete_model', delete_model, methods=['DELETE'])  
bp.add_url_rule('/check_model_exists', 'check_model_exists', check_model_exists, methods=['GET'])

# 文件管理相关路由
bp.add_url_rule('/upload_file', 'upload_file', upload_file, methods=['POST'])
bp.add_url_rule('/get_files', 'get_files', get_files, methods=['GET'])  
bp.add_url_rule('/delete_file/<int:file_id>', 'delete_file', delete_file, methods=['DELETE'])  
bp.add_url_rule('/check_file_exists', 'check_file_exists', check_file_exists, methods=['GET'])

# 数据管理相关路由
bp.add_url_rule('/get_data_records', 'get_data_records', get_data_records, methods=['GET'])

# 故障诊断相关路由
bp.add_url_rule('/get_files', 'get_files', get_files, methods=['GET'])
bp.add_url_rule('/get_models', 'get_models', get_models, methods=['GET'])
bp.add_url_rule('/diagnose', 'diagnose', diagnose, methods=['POST'])

# report相关路由
bp.add_url_rule('/get_diagnosis_records', 'get_diagnosis_records', get_diagnosis_records, methods=['GET'])
bp.add_url_rule('/delete_diagnosis_record', 'delete_diagnosis_record', delete_diagnosis_record, methods=['DELETE'])
