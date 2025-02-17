from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from extensions import db
from models import User

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Redirects users to the appropriate dashboard based on their role."""
    if not current_user or not current_user.role:
        flash('Invalid user or missing role. Contact admin.', 'danger')
        return redirect(url_for('auth.login'))

    # Role-based redirection
    role_routes = {
        'Admin': 'dashboard.admin_dashboard',
        'Doctor': 'dashboard.doctor_dashboard',
        'Patient': 'dashboard.patient_dashboard',
        'Billing Staff': 'dashboard.billing_dashboard'
    }

    return redirect(url_for(role_routes.get(current_user.role.role_name, 'auth.login')))


@dashboard_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role and current_user.role.role_name != 'Admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard.index'))

    return render_template('admin_dashboard.html', user=current_user)


@dashboard_bp.route('/doctor_dashboard')
@login_required
def doctor_dashboard():
    if current_user.role and current_user.role.role_name != 'Doctor':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard.index'))

    return render_template('doctor_dashboard.html', user=current_user)


@dashboard_bp.route('/patient_dashboard')
@login_required
def patient_dashboard():
    if current_user.role and current_user.role.role_name != 'Patient':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard.index'))

    return render_template('patient_dashboard.html', user=current_user)


@dashboard_bp.route('/billing_dashboard')
@login_required
def billing_dashboard():
    if current_user.role and current_user.role.role_name != 'Billing Staff':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('dashboard.index'))

    return render_template('billing_dashboard.html', user=current_user)
