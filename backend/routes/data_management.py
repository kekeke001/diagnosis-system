# data_management.py
from flask import Blueprint, jsonify
from models import DataManagement, db

bp = Blueprint('data_management', __name__)

# 获取所有数据上传记录
@bp.route('/data_management', methods=['GET'])
def get_data_records():
    try:
        data_records = DataManagement.query.all()
        records_list = [{
            "id": record.data_id,  # 这里确保 data_id 是模型的字段
            "name": record.data_type,  # 确保 data_type 是正确的字段
            "uploadedAt": record.upload_time.isoformat()  # 统一格式化时间
        } for record in data_records]
        return jsonify({"dataRecords": records_list}), 200
    except Exception as e:
        return jsonify({"error": f"Error fetching data records: {str(e)}"}), 500

