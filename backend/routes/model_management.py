import os
import jwt
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from config import Config
from models import db, Model
from datetime import datetime
from flask_cors import CORS

# 创建蓝图
bp = Blueprint('model_management', __name__)

# 检查文件扩展名是否合法
def allowed_model(modelname):
    allowed_extensions = {'h5', 'pt', 'zip', 'pkl'}  # 根据需求修改文件扩展名
    return '.' in modelname and modelname.rsplit('.', 1)[1].lower() in allowed_extensions

# 上传模型接口
@bp.route('/upload_model', methods=['POST'])
def upload_model():
    try:
        model = request.files.get('model')  # 获取上传的模型文件

        if not model or model.filename == '':
            return jsonify({"error": "No model uploaded or file is empty"}), 400

        if not allowed_model(model.filename):
            return jsonify({"error": "Invalid file type"}), 400

        # 检查文件是否已经存在
        model_name = model.filename
        existing_model = Model.query.filter_by(model_name=model_name).first()
        if existing_model:
            return jsonify({"error": "Model already exists"}), 400

        # 安全保存文件
        filename = secure_filename(model.filename)

        # 确保保存目录存在
        if not os.path.exists(Config.UPLOAD_MODEL):
            os.makedirs(Config.UPLOAD_MODEL)

        model_path = os.path.join(Config.UPLOAD_MODEL, filename)
        model.save(model_path)

        # 获取文件大小
        model_size = os.path.getsize(model_path)

        # 将模型信息存入数据库
        new_model = Model(
            model_name=filename,
            model_size=model_size,
            model_path=model_path,
            upload_time=datetime.utcnow()
        )

        db.session.add(new_model)
        db.session.commit()

        return jsonify({"message": "Model uploaded successfully", "model_name": filename}), 200

    except Exception as e:
        print(f"Error during model upload: {str(e)}")  # 打印详细的错误日志
        return jsonify({"error": f"Model upload failed: {str(e)}"}), 500

# 获取模型接口
@bp.route('/get_models', methods=['GET'])
def get_models():
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 5))
        
        models_query = db.session.query(Model).order_by(Model.upload_time.desc())
        
        # 分页查询
        models = models_query.offset((page - 1) * page_size).limit(page_size).all()

        # 获取总数据条数
        total_models = models_query.count()
        total_pages = (total_models + page_size - 1) // page_size

        model_data = [{
            'model_id': model.model_id,
            'model_name': model.model_name,
            'model_size': model.model_size,
            'upload_time': model.upload_time.isoformat()
        } for model in models]

        return jsonify({
            'models': model_data,
            'total': total_models,
            'total_pages': total_pages,
            'current_page': page
        })

    except Exception as e:
        print(f"Error fetching models: {str(e)}")  # 打印详细的错误日志
        return jsonify({"error": "Error fetching models"}), 500

# 删除模型接口
@bp.route('/delete_model/<int:model_id>', methods=['DELETE'])
def delete_model(model_id):
    try:
        model = Model.query.get_or_404(model_id)

        # 删除文件
        model_path = model.model_path
        if os.path.exists(model_path):
            os.remove(model_path)

        # 删除数据库中的记录
        db.session.delete(model)
        db.session.commit()

        return jsonify({"message": "模型已删除"}), 200

    except Exception as e:
        print(f"Error deleting model: {str(e)}")  # 打印详细的错误日志
        return jsonify({"error": "Error deleting model"}), 500

# 检查模型是否已存在
@bp.route('/check_model_exists', methods=['GET'])
def check_model_exists():
    model_name = request.args.get('model_name')  # 获取文件名
    if not model_name:
        return jsonify({'message': '文件名未提供'}), 400

    existing_model = db.session.query(Model).filter_by(model_name=model_name).first()
    
    if existing_model:
        return jsonify({'exists': True})  # 文件已存在
    else:
        return jsonify({'exists': False})  # 文件不存在
