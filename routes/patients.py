from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from models import Patient, db
from utils import check_permission  # 导入 check_permission
import logging
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

# 定义蓝图
patients_bp = Blueprint('patients', __name__, url_prefix='/patients')

logger = logging.getLogger(__name__)

# 显示所有患者（根据角色）
@patients_bp.route('/patients', methods=['GET'], endpoint='list_patients')
@login_required
def get_patients():
    if not check_permission(current_user, 'patients', 'read'):
        return jsonify({'error': 'Unauthorized: No read permission'}), 403

    try:
        # 确定当前用户的角色和 username
        user_role_id = current_user.role.role_id  # 从 User 模型获取 role_id
        user_username = current_user.username  # 从 User 模型获取 username

        logger.debug(f"User role_id: {user_role_id}, username: {user_username}")

        # 调用存储过程
        result = db.session.execute(
            text("CALL GetPatientDataByRole(:role_id, :username)"),
            {"role_id": user_role_id, "username": user_username}
        )
        # 获取列名
        columns = result.keys()
        logger.debug(f"Result columns: {list(columns)}")

        # 将结果转换为字典列表
        patient_data = [dict(zip(columns, row)) for row in result.fetchall()]
        logger.debug(f"Raw patient data: {patient_data}")
        print("Columns:", columns)
        print("Patient Data:", patient_data)
        if not patient_data:
            logger.warning("No patient data returned from database for user: {user_username}")
            return render_template('patients.html', patients=[])
    except Exception as e:
        logger.error(f"Database query failed: {str(e)}")
        return jsonify({'error': 'Database error'}), 500

    logger.debug(f"Queried patients: {len(patient_data)} records found")
    return render_template('patients.html', patients=patient_data)

# 添加新患者
@patients_bp.route('/patients', methods=['POST'], endpoint='create_patient')
@login_required
def create_patient():
    if not check_permission(current_user, 'patients', 'write'):
        return jsonify({'error': 'Unauthorized: No write permission'}), 403

    data = request.form.to_dict()
    if not data or not all(k in data for k in ('Id', 'BIRTHDATE', 'FIRST', 'LAST')):  # 要求提供 Id、BIRTHDATE、FIRST 和 LAST
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        # 设置加密密钥
        db.session.execute(text(f"SET @encryption_key = '{ENCRYPTION_KEY}';"))

        # 插入新患者
        new_patient = Patient(
            Id=data['Id'],  # 确保 Id 是 username 的字符串
            BIRTHDATE=data['BIRTHDATE'],
            FIRST=data['FIRST'],
            LAST=data['LAST'],
            SSN=data.get('SSN'),  # 传递原始字符串
            DRIVERS=data.get('DRIVERS')  # 传递原始字符串
        )

        db.session.add(new_patient)
        db.session.commit()  # 提交事务，确保触发器触发
        logger.debug(f"Created patient: {new_patient.Id}")
        flash('Patient created successfully', 'success')  # 添加闪存消息
        return redirect(url_for('patients.list_patients'))  # 重定向到患者列表
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create patient: {str(e)}")
        return jsonify({'error': 'Failed to create patient'}), 500