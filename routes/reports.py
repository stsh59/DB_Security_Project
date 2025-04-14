from flask import Blueprint, render_template, flash, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from routes import has_permission
from models import reflect_fhir_tables, User, Patient
import models  # Needed to access reflected classes dynamically
from utils import log_audit

reports_bp = Blueprint('reports', __name__)

# Ensure FHIR tables are reflected
def init_reports():
    with db.app_context():
        reflect_fhir_tables()

@reports_bp.route('/')
@jwt_required()
@has_permission('reports', 'read')  # Role-based access check
def reports():
    """Fetch and display reports for admin users."""
    try:
        # Dynamically fetch reflected models
        Encounter = getattr(models, 'Encounter', None)
        Claim = getattr(models, 'Claim', None)

        if not Encounter or not Claim:
            flash("FHIR tables are not properly loaded!", "danger")
            return redirect(url_for('dashboard.index'))

        reports_data = [
            {
                'heading': '📋 List of Patients (First 10)',
                'data': Patient.query.limit(10).all()
            },
            {
                'heading': '🏥 Outpatient Encounters (Limited to 10)',
                'data': Encounter.query.filter_by(ENCOUNTERCLASS='outpatient').limit(10).all()
            },
            {
                'heading': '💰 Top 5 Claims with Highest OUTSTANDING1',
                'data': Claim.query.order_by(Claim.OUTSTANDING1.desc()).limit(5).all()
            }
        ]

        # Audit logging
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if user:
            log_audit(user, 'VIEW_REPORTS', 'reports')

        return render_template('report.html', reports_data=reports_data)

    except Exception as e:
        print(f"Error in reports route: {e}")
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('dashboard.index'))
