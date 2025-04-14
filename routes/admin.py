from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_jwt_extended import jwt_required
from extensions import db
from models import User, Role, AuditLog
from routes import has_permission  # RBAC utility
from utils import log_audit  # ✅ Import audit logging function

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/manage_users')
@login_required
@has_permission('users', 'read')  # ✅ Only roles with read access can view users
def manage_users():
    log_audit(current_user, 'VIEW_USERS', 'users')  # ✅ Log view action
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@has_permission('users', 'update')  # ✅ Only roles with update access can edit users
def edit_user(user_id):
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('admin.manage_users'))

    if request.method == 'POST':
        new_role_id = request.form.get('role_id')  # ✅ Fetch role_id instead of role_name
        role = Role.query.get(new_role_id)
        if role:
            user.role_id = role.role_id
            db.session.commit()
            flash('User role updated successfully!', 'success')

            # ✅ Log role update
            log_audit(current_user, 'UPDATE_ROLE', 'users', record_id=user.id)
        else:
            flash('Invalid role selected.', 'danger')

        return redirect(url_for('admin.manage_users'))

    roles = Role.query.all()  # ✅ Fetch all available roles
    return render_template('edit_user.html', user=user, roles=roles)

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@has_permission('users', 'delete')  # ✅ Only roles with delete access can remove users
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')

        # ✅ Log deletion
        log_audit(current_user, 'DELETE_USER', 'users', record_id=user.id)
    else:
        flash('User not found', 'danger')

    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/audit_logs')
@login_required
def view_audit_logs():
    if current_user.role.role_name != 'Admin':
        flash("Unauthorized access", "danger")
        return redirect(url_for('dashboard.index'))

    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('audit_logs.html', logs=logs)