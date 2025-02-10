import logging
import os
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from config import Config
from models import db, File
from datetime import datetime

# 创建蓝图
bp = Blueprint('file_management', __name__)

# 设置日志
logging.basicConfig(level=logging.DEBUG)

# 检查文件扩展名是否合法
def allowed_file(filename):
    allowed_extensions = {'dat', 'pt', 'zip', 'xlsx'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# 上传文件接口
@bp.route('/upload_file', methods=['POST'])
def upload_file():
    try:
        # 获取上传的文件
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({"error": "No file uploaded or file is empty"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        # 检查文件是否已经存在
        file_name = file.filename
        existing_file = File.query.filter_by(file_name=file_name).first()
        if existing_file:
            return jsonify({"error": "File already exists"}), 400

        # 安全保存文件
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FILE, filename)

        # 确保保存目录存在
        if not os.path.exists(Config.UPLOAD_FILE):
            os.makedirs(Config.UPLOAD_FILE)

        file.save(file_path)

        # 获取文件大小
        file_size = os.path.getsize(file_path)

        # 将文件信息存入数据库
        new_file = File(
            file_name=filename,
            file_size=file_size,
            file_path=file_path,
            upload_time=datetime.utcnow()
        )

        db.session.add(new_file)
        db.session.commit()

        return jsonify({"message": "File uploaded successfully", "file_name": filename}), 200

    except Exception as e:
        logging.error(f"File upload failed: {str(e)}")
        return jsonify({"error": "File upload failed"}), 500

# 获取文件列表接口
@bp.route('/get_files', methods=['GET'])
def get_files():
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 5))

        files_query = db.session.query(File).order_by(File.upload_time.desc())

        # 分页查询
        files = files_query.offset((page - 1) * page_size).limit(page_size).all()

        # 获取总数据条数
        total_files = files_query.count()
        total_pages = (total_files + page_size - 1) // page_size

        file_data = [{
            'file_id': file.file_id,
            'file_name': file.file_name,
            'file_size': file.file_size,
            'upload_time': file.upload_time.isoformat()
        } for file in files]

        return jsonify({
            'files': file_data,
            'total': total_files,
            'total_pages': total_pages,
            'current_page': page
        })

    except Exception as e:
        logging.error(f"Error fetching files: {str(e)}")
        return jsonify({"error": "Error fetching files"}), 500

# 删除文件接口
@bp.route('/delete_file/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    try:
        file = File.query.get_or_404(file_id)

        # 删除文件
        file_path = file.file_path
        if os.path.exists(file_path):
            os.remove(file_path)

        # 删除数据库中的记录
        db.session.delete(file)
        db.session.commit()

        return jsonify({"message": "File deleted successfully"}), 200

    except Exception as e:
        logging.error(f"Error deleting file: {str(e)}")
        return jsonify({"error": "Error deleting file"}), 500

# 检查文件是否已存在
@bp.route('/check_file_exists', methods=['GET'])
def check_file_exists():
    file_name = request.args.get('file_name')
    if not file_name:
        return jsonify({'message': 'File name not provided'}), 400

    existing_file = db.session.query(File).filter_by(file_name=file_name).first()

    if existing_file:
        return jsonify({'exists': True})  # 文件已存在
    else:
        return jsonify({'exists': False})  # 文件不存在
