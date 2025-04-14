from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from models import Patient, db
from utils import check_permission, log_audit
import logging
from sqlalchemy import text
from dotenv import load_dotenv
import os

load_dotenv()
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY')

# Define Blueprint
patients_bp = Blueprint('patients', __name__, url_prefix='/patients')

logger = logging.getLogger(__name__)

# 🔹 View All Patients (Admin and Doctor)
@patients_bp.route('/patients', methods=['GET'], endpoint='list_patients')
@login_required
def get_patients():
    if not check_permission(current_user, 'patients', 'read'):
        return jsonify({'error': 'Unauthorized: No read permission'}), 403

    try:
        user_role_id = current_user.role.role_id
        user_username = current_user.username

        logger.debug(f"User role_id: {user_role_id}, username: {user_username}")

        result = db.session.execute(
            text("CALL GetPatientDataByRole(:role_id, :username)"),
            {"role_id": user_role_id, "username": user_username}
        )

        columns = result.keys()
        patient_data = [dict(zip(columns, row)) for row in result.fetchall()]

        if not patient_data:
            logger.warning(f"No patient data returned from database for user: {user_username}")
            return render_template('patients.html', patients=[])

        # ✅ Log viewing of patient list
        log_audit(current_user, 'VIEW_PATIENT_LIST', 'patients')

    except Exception as e:
        logger.error(f"Database query failed: {str(e)}")
        return jsonify({'error': 'Database error'}), 500

    return render_template('patients.html', patients=patient_data)


# 🔹 Create New Patient (Admin Only)
@patients_bp.route('/patients', methods=['POST'], endpoint='create_patient')
@login_required
def create_patient():
    if current_user.role.role_name != 'Admin':
        flash("Only admins can create patients.", "danger")
        return redirect(url_for('dashboard.index'))

    if not check_permission(current_user, 'patients', 'write'):
        return jsonify({'error': 'Unauthorized: No write permission'}), 403

    data = request.form.to_dict()
    if not data or not all(k in data for k in ('Id', 'BIRTHDATE', 'FIRST', 'LAST')):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        db.session.execute(text(f"SET @encryption_key = '{ENCRYPTION_KEY}';"))

        new_patient = Patient(
            Id=data['Id'],
            BIRTHDATE=data['BIRTHDATE'],
            FIRST=data['FIRST'],
            LAST=data['LAST'],
            SSN=data.get('SSN'),
            DRIVERS=data.get('DRIVERS')
        )

        db.session.add(new_patient)
        db.session.commit()
        logger.debug(f"Created patient: {new_patient.Id}")

        # ✅ Log patient creation
        log_audit(current_user, 'CREATE_PATIENT', 'patients', record_id=data['Id'])

        flash('Patient created successfully', 'success')
        return redirect(url_for('patients.list_patients'))

    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create patient: {str(e)}")
        return jsonify({'error': 'Failed to create patient'}), 500
