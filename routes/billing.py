from flask import Blueprint, render_template, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import RolePermission, User, db
import models  # Import the models module where dynamic models are stored


def get_model(model_name):
    """
    Return the dynamic model from the models module's namespace.
    Ensure that models.reflect_fhir_tables() has been called before.
    """
    model = getattr(models, model_name, None)
    if model is None:
        flash(f"Model {model_name} not found. Please check the table reflection.", 'danger')
    return model


billing_bp = Blueprint('billing', __name__)


@billing_bp.route('/access_claims_and_patients')
@jwt_required(locations=['cookies'])  # Check cookies for JWT
def access_claims_and_patients():
    # Retrieve the logged-in user from JWT identity
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        flash("User not found!", 'danger')
        return redirect(url_for('auth.login'))

    role_id = user.role_id

    # Dynamically load the Claim and Patient models from the models module
    Claim = get_model('Claim')
    Patient = get_model('Patient')

    # Debug: Print model info and columns to confirm proper reflection
    print(f"Claim model: {Claim}")
    print("Claim columns:", Claim.__table__.columns.keys())
    print(f"Patient model: {Patient}")
    print("Patient columns:", Patient.__table__.columns.keys())

    # --- Check permission for the claims table ---
    claims_permission = RolePermission.query.filter_by(role_id=role_id, table_name='claims').first()
    if claims_permission and claims_permission.can_read:
        try:
            # Fetch the top 5 claims ordered by a specific column.
            # Note: Since the reflected column name is 'Id' (with uppercase I), use claim.Id.
            top_claims = Claim.query.order_by(Claim.HEALTHCARECLAIMTYPEID1.desc()).limit(5).all()
            claims_message = "Top 5 Claims:"
            claims_data = [{
                'id': claim.Id,  # Use the proper attribute name as reflected in your table
                'patient_id': claim.PATIENTID,
                'healthcare_claim_type': claim.HEALTHCARECLAIMTYPEID1
            } for claim in top_claims]
        except Exception as e:
            claims_message = "Error fetching claims data."
            claims_data = []
            print(f"Error fetching claims: {e}")
    else:
        claims_message = "You do not have permission to access claims."
        claims_data = []

    # --- Check permission for the patients table ---
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
        except Exception as e:
            patients_message = "Error fetching patients data."
            patients_data = []
            print(f"Error fetching patients: {e}")
    else:
        # Billing staff does not have permission to read patient data.
        patients_message = "Access denied! Billing staff does not have permission to view patient details."
        patients_data = []

    # Render the template with both claims and patients information (or error messages)
    return render_template('access_claims_and_patients.html',
                           claims_message=claims_message, claims_data=claims_data,
                           patients_message=patients_message, patients_data=patients_data)
