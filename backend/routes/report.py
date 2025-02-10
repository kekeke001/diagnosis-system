from flask import Blueprint, request, jsonify
from models import DiagnosisRecord, Report, File, Model, db  # 导入 File 和 Model
import shutil
import os
from datetime import datetime
import logging
from fpdf import FPDF

bp = Blueprint('report', __name__)

# 设置日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 获取所有诊断记录
@bp.route('/get_diagnosis_records', methods=['GET'])
def get_diagnosis_records():
    try:
        records = DiagnosisRecord.query.all()
        records_data = []
        for record in records:
            file = File.query.get(record.file_id)
            model = Model.query.get(record.model_id)

            # 获取关联的报告
            report = Report.query.filter(Report.diagnosis_record.has(DiagnosisRecord.record_id == record.record_id)).first()

            records_data.append({
                "record_id": record.record_id,
                "file_name": file.file_name if file else 'Unknown',
                "model_name": model.model_name if model else 'Unknown',
                "created_at": record.created_at,
                "report_path": report.report_path if report else '',
                "report_name": report.report_name if report else 'No Report'  # 添加报告名
            })
        return jsonify(records=records_data), 200
    except Exception as e:
        logger.error(f"Error fetching diagnosis records: {str(e)}")
        return jsonify(message="Internal server error"), 500

# 删除诊断记录
@bp.route('/delete_diagnosis_record/<int:record_id>', methods=['DELETE'])
def delete_diagnosis_record(record_id):
    try:
        diagnosis_record = DiagnosisRecord.query.get(record_id)
        if not diagnosis_record:
            return jsonify(message="Record not found"), 404

        # 删除报告
        report = Report.query.filter_by(diagnosis_record=diagnosis_record).first()
        if report:
            os.remove(report.report_path)  # 删除报告文件
            db.session.delete(report)

        # 删除诊断记录
        db.session.delete(diagnosis_record)
        db.session.commit()

        return jsonify(message="Record deleted successfully"), 200
    except Exception as e:
        logger.error(f"Error deleting diagnosis record: {str(e)}")
        return jsonify(message="Internal server error"), 500
