from flask import Blueprint, render_template
from flask_login import login_required, current_user

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard')
@login_required
def index():
    if current_user.role == 'admin':
        return render_template('admin_dashboard.html')
    elif current_user.role == 'doctor':
        return render_template('doctor_dashboard.html')
    elif current_user.role == 'patient':
        return render_template('patient_dashboard.html')
    else:
        flash('Unauthorized access', 'danger')
        return redirect('/')
