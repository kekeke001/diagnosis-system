from flask import Blueprint, request, jsonify, send_from_directory
from fpdf import FPDF
from models import File, Model, DiagnosisRecord, Report, db
import subprocess
import os
import json
import re
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = Blueprint('diagnosis', __name__)

# 提供静态文件访问的路由
@bp.route('/reports/<filename>')
def serve_report(filename):
    filepath = os.path.join('/root/My_Project/backend/reports', filename)
    print(f"Serving file from: {filepath}")  # 打印文件路径
    return send_from_directory('/root/My_Project/backend/reports', filename)

# 获取文件列表
@bp.route('/get_files', methods=['GET'])
def get_files():
    try:
        files = File.query.all()
        files_data = [{"file_id": file.file_id, "file_name": file.file_name} for file in files]
        return jsonify(files=files_data), 200
    except Exception as e:
        logger.error(f"Error fetching files: {str(e)}")
        return jsonify(message="Internal server error"), 500

# 获取模型列表
@bp.route('/get_models', methods=['GET'])
def get_models():
    try:
        models = Model.query.all()
        models_data = [{"model_id": model.model_id, "model_name": model.model_name} for model in models]
        return jsonify(models=models_data), 200
    except Exception as e:
        logger.error(f"Error fetching models: {str(e)}")
        return jsonify(message="Internal server error"), 500


# Generate PDF report
import json
from fpdf import FPDF
import os

def generate_report_pdf(diagnosis_record, report_path):
    # Create PDF instance
    pdf = FPDF()
    pdf.add_page()

    # Set title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(200, 10, txt="Diagnosis Report", ln=True, align='C')

    # Set content
    pdf.set_font('Arial', '', 12)
    pdf.ln(10)  # Space
    pdf.cell(200, 10, txt=f"Report Name: {diagnosis_record.report.report_name}", ln=True)  # Report name

    # Get file name by file_id
    file = File.query.get(diagnosis_record.file_id)
    file_name = file.file_name if file else "Unknown File"
    pdf.cell(200, 10, txt=f"File Name: {file_name}", ln=True)

    # Get model name by model_id
    model = Model.query.get(diagnosis_record.model_id)
    model_name = model.model_name if model else "Unknown Model"
    pdf.cell(200, 10, txt=f"Model Name: {model_name}", ln=True)

    # Diagnosis result (formatting the metrics)
    pdf.ln(10)  # Space
    pdf.cell(200, 10, txt="Diagnosis Results:", ln=True)

    # Check if diagnosis_result is a JSON string
    try:
        diagnosis_data = json.loads(diagnosis_record.diagnosis_result)  # Parse JSON string to dictionary
    except json.JSONDecodeError:
        diagnosis_data = {}

    # Extracting and formatting the metrics
    metrics = {
        "Accuracy": diagnosis_data.get("accuracy", "N/A"),
        "Precision": diagnosis_data.get("precision", "N/A"),
        "Recall": diagnosis_data.get("recall", "N/A"),
        "F1 Score": diagnosis_data.get("f1", "N/A"),
        "Specificity": diagnosis_data.get("specificity", "N/A")
    }

    # Formatting the metrics to match the desired structure
    pdf.ln(5)  # Space
    for metric, value in metrics.items():
        pdf.cell(200, 10, txt=f"{metric}: {value}", ln=True)

    # Diagnosis time
    diagnosis_time = diagnosis_record.created_at.strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(200, 10, txt=f"Diagnosis Time: {diagnosis_time}", ln=True)

    # Insert confusion matrix image
    confusion_matrix_image_path = diagnosis_record.confusion_matrix_path
    if os.path.exists(confusion_matrix_image_path):
        pdf.ln(10)  # Space
        pdf.image(confusion_matrix_image_path, x=10, w=180)  # Adjust image width
    else:
        logger.warning(f"Confusion matrix image not found: {confusion_matrix_image_path}")

    # Save PDF file
    pdf.output(report_path)


# 执行故障诊断
@bp.route('/diagnose', methods=['POST'])
def diagnose():
    try:
        # 获取请求数据
        data = request.get_json()
        file_id = data.get('file_id')
        model_id = data.get('model_id')

        if not file_id or not model_id:
            return jsonify(message="File ID and Model ID are required"), 400

        # 查询数据库获取文件和模型路径
        file = File.query.get(file_id)
        model = Model.query.get(model_id)

        if not file:
            return jsonify(message="File not found in database"), 404
        if not model:
            return jsonify(message="Model not found in database"), 404

        file_path = os.path.join("/root/My_Project/backend/uploads", file.file_name)
        model_path = os.path.join("/root/My_Project/backend/models", model.model_name)

        if not os.path.exists(file_path):
            return jsonify(message=f"File not found on server at {file_path}"), 404
        if not os.path.exists(model_path):
            return jsonify(message=f"Model not found on server at {model_path}"), 404

        # 执行诊断脚本
        result = subprocess.run(
            ["python3", "/root/My_Project/backend/routes/diagnosis_eval.py", file_path, model_path],
            check=True,
            capture_output=True,
            text=True
        )

        # 打印脚本输出和错误输出
        logger.debug(f"Diagnosis script output: {result.stdout}")
        logger.debug(f"Diagnosis script error: {result.stderr}")

        # 使用正则表达式提取JSON部分
        match = re.search(r'diagnosis_result-eval\s*(\{.*\})', result.stdout)
        if match:
            diagnosis_json = match.group(1)
            try:
                # 解析JSON内容
                diagnosis_data = json.loads(diagnosis_json)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse diagnosis script output: {result.stdout}")
                return jsonify(message="Invalid output from diagnosis script, not in JSON format"), 500
        else:
            logger.error(f"Failed to find JSON in diagnosis script output: {result.stdout}")
            return jsonify(message="Diagnosis result JSON not found in output"), 500

        # 获取诊断结果详细信息
        diagnosis_result = diagnosis_json  # 原始 JSON 字符串

        logger.debug(f"Parsed diagnosis result: {diagnosis_data}")

        # 图像路径
        tsne_image_path = "/root/My_Project/backend/reports/t-SNE_Visualization.png"
        confusion_matrix_image_path = "/root/My_Project/backend/reports/Confusion_Matrix.png"

        # 转换为相对路径
        tsne_image_url = f"/reports/{os.path.basename(tsne_image_path)}"
        confusion_matrix_image_url = f"/reports/{os.path.basename(confusion_matrix_image_path)}"

        # 创建报告名称
        report_name = f"{model.model_name}_{file.file_name}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # 保存诊断记录
        diagnosis_record = DiagnosisRecord(
            file_id=file_id,
            model_id=model_id,
            tsne_path=tsne_image_path,
            confusion_matrix_path=confusion_matrix_image_path,
            diagnosis_result=diagnosis_result
        )
        db.session.add(diagnosis_record)
        db.session.commit()
        
        report_path=f"/root/My_Project/backend/reports/{report_name}.pdf"
        # 转换为相对路径
        # report_path_url = f"/reports/{os.path.basename(report_path)}"
        # 创建并保存报告
        report = Report(
            report_name=report_name,
            report_format="PDF",  # 假设格式为 PDF
            report_path=report_path,
            created_at=diagnosis_record.created_at
        )
        db.session.add(report)
        db.session.commit()

        # 关联报告和诊断记录
        diagnosis_record.report = report
        db.session.commit()

        # 生成PDF报告
        report_path = report.report_path
        generate_report_pdf(diagnosis_record, report_path)

        return jsonify(
            diagnosis_result=diagnosis_data,
            tsne_image_path=tsne_image_url,  # 返回相对路径
            confusion_matrix_image_path=confusion_matrix_image_url,  # 返回相对路径
        ), 200


    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error: {e.stderr}")
        return jsonify(message="Diagnosis script error", error=str(e)), 500
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify(message="Internal server error", error=str(e)), 500
