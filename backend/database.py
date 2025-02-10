from models import db, File, Model, DiagnosisRecord, Report, DataManagement

# 添加文件记录
def add_file(user_id, file_name, file_path, file_format):
    try:
        file = File(user_id=user_id, file_name=file_name, file_path=file_path, file_format=file_format)
        db.session.add(file)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

# 添加模型记录
def add_model(model_name, description, model_path):
    try:
        model = Model(model_name=model_name, description=description, model_path=model_path)
        db.session.add(model)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

# 创建诊断记录
def create_diagnosis_record(file_id, model_id, diagnosis_result, fault_type, probability):
    try:
        record = DiagnosisRecord(file_id=file_id, model_id=model_id, diagnosis_result=diagnosis_result,
                                 fault_type=fault_type, probability=probability)
        db.session.add(record)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

# 生成报告
def generate_report(record_id, report_format, report_path):
    try:
        report = Report(record_id=record_id, report_format=report_format, report_path=report_path)
        db.session.add(report)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
