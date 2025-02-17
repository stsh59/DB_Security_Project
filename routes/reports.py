from flask import Blueprint, render_template, flash, redirect, url_for
from flask_jwt_extended import jwt_required
from extensions import db
from routes import has_permission
from models import reflect_fhir_tables

reports_bp = Blueprint('reports', __name__)

# Ensure FHIR tables are available inside an app context
def init_reports():
    """Ensures that FHIR tables are reflected properly before use."""
    with db.app.app_context():  # ✅ Fixes the error by using app context
        reflect_fhir_tables()

@reports_bp.route('/')
@jwt_required()
@has_permission('reports', 'read')
def reports():
    """Fetch and display reports for admin users."""
    try:
        # Fetch dynamically loaded models
        Encounter = globals().get('Encounter')
        Patient = globals().get('Patient')
        Claim = globals().get('Claim')

        if not Encounter or not Patient or not Claim:
            flash("FHIR tables are not properly loaded!", "danger")
            return redirect(url_for('dashboard.index'))

        # Sample report queries
        reports_data = [
            {
                'heading': 'List of Patients (Limited to 10)',
                'data': Patient.query.limit(10).all()
            },
            {
                'heading': 'Encounters that have been completed',
                'data': Encounter.query.filter_by(status='finished').limit(10).all()
            },
            {
                'heading': 'Top 5 Highest Claim Amounts',
                'data': Claim.query.order_by(Claim.total_amount.desc()).limit(5).all()
            }
        ]

        return render_template('report.html', reports_data=reports_data)

    except Exception as e:
        print(f"Error in reports route: {e}")  # Debugging log
        flash(f"An error occurred: {str(e)}", 'danger')
        return redirect(url_for('dashboard.index'))
