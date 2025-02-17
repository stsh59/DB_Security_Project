from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required
from flask_jwt_extended import create_access_token, set_access_cookies
from extensions import db, bcrypt
from models import User, Role  # ✅ Import Role
from flask import jsonify


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')
        role_id = request.form['role_id']  # ✅ Now receiving role_id directly from the form

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('auth.signup'))

        # ✅ No need to fetch role, since role_id is already provided
        new_user = User(username=username, password=password, role_id=role_id)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully!', 'success')
        return redirect(url_for('auth.login'))

    # ✅ Pass all roles to the template
    roles = Role.query.all()
    return render_template('signup.html', roles=roles)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            # First check if role is valid BEFORE creating token
            if not user.role:
                flash('Role not assigned. Contact admin.', 'danger')
                return redirect(url_for('auth.login'))

            role_name = user.role.role_name
            dashboard_routes = {
                "Admin": "dashboard.admin_dashboard",
                "Doctor": "dashboard.doctor_dashboard",
                "Patient": "dashboard.patient_dashboard",
                "Billing Staff": "dashboard.billing_dashboard"
            }

            if role_name not in dashboard_routes:
                flash('Invalid role detected. Contact admin.', 'danger')
                return redirect(url_for('auth.login'))

            # Now handle successful login
            login_user(user)
            access_token = create_access_token(identity=str(user.id))

            # Create response AFTER all checks
            response = redirect(url_for(dashboard_routes[role_name]))
            set_access_cookies(response, access_token)
            response.headers['Cache-Control'] = 'no-cache, no-store'  # ✅ Prevent caching issues
            return response

        else:  # This else belongs to the password check
            flash('Invalid username or password', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('login.html')  # GET request handling


@auth_bp.route('/logout', methods=['POST'])  # ✅ Change GET to POST
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))

