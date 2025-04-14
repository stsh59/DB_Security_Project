from flask import Blueprint, render_template
from flask_login import login_required, current_user
from routes import has_permission

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/')
@login_required
def doctor_dashboard():
    return render_template('doctor_dashboard.html')
