from flask import Blueprint, render_template, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import RolePermission, User, db
from utils import log_audit  # ✅ Add audit logging
import models  # Import the models module where dynamic models are stored


def get_model(model_name):
    model = getattr(models, model_name, None)
    if model is None:
        flash(f"Model {model_name} not found. Please check the table reflection.", 'danger')
    return model


billing_bp = Blueprint('billing', __name__)


@billing_bp.route('/access_claims_and_patients')
@jwt_required(locations=['cookies'])
def access_claims_and_patients():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        flash("User not found!", 'danger')
        return redirect(url_for('auth.login'))

    role_id = user.role_id

    Claim = get_model('Claim')
    Patient = get_model('Patient')

    print(f"Claim model: {Claim}")
    print("Claim columns:", Claim.__table__.columns.keys())
    print(f"Patient model: {Patient}")
    print("Patient columns:", Patient.__table__.columns.keys())

    claims_message = ""
    claims_data = []

    claims_permission = RolePermission.query.filter_by(role_id=role_id, table_name='claims').first()
    if claims_permission and claims_permission.can_read:
        try:
            top_claims = Claim.query.order_by(Claim.HEALTHCARECLAIMTYPEID1.desc()).limit(5).all()
            claims_message = "Top 5 Claims:"
            claims_data = [{
                'id': claim.Id,
                'patient_id': claim.PATIENTID,
                'healthcare_claim_type': claim.HEALTHCARECLAIMTYPEID1
            } for claim in top_claims]

            # ✅ Log access to claims
            log_audit(user, 'VIEW_CLAIMS', 'claims')
        except Exception as e:
            claims_message = "Error fetching claims data."
            print(f"Error fetching claims: {e}")
    else:
        claims_message = "You do not have permission to access claims."

    patients_message = ""
    patients_data = []

    patients_permission = RolePermission.query.filter_by(role_id=role_id, table_name='patients').first()
    if patients_permission and patients_permission.can_read:
        try:
            top_patients = Patient.query.limit(5).all()
            patients_message = "Top 5 Patients:"
            patients_data = [{
                'id': patient.Id,
                'first_name': patient.FIRST,
                'last_name': patient.LAST
            } for patient in top_patients]

            # ✅ Log access to patients
            log_audit(user, 'VIEW_PATIENTS', 'patients')
        except Exception as e:
            patients_message = "Error fetching patients data."
            print(f"Error fetching patients: {e}")
    else:
        patients_message = "Access denied! Billing staff does not have permission to view patient details."

    return render_template('access_claims_and_patients.html',
                           claims_message=claims_message, claims_data=claims_data,
                           patients_message=patients_message, patients_data=patients_data)
