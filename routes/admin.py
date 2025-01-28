from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models import User

bp = Blueprint('admin', __name__)

@bp.route('/manage_users')
@login_required
def manage_users():
    # Debugging logs
    print(f"Current user: {current_user.username}, Role: {current_user.role}")

    if current_user.role != 'admin':
        flash('Access restricted to admin only', 'danger')
        return redirect(url_for('dashboard.index'))

    try:
        users = User.query.all()
        print(f"Fetched users: {users}")
    except Exception as e:
        print(f"Error fetching users: {e}")
        flash('An error occurred while fetching users.', 'danger')
        return redirect(url_for('dashboard.index'))

    return render_template('manage_users.html', users=users)

@bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        flash('Access restricted to admin only', 'danger')
        return redirect(url_for('dashboard.index'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('admin.manage_users'))

    if request.method == 'POST':
        new_role = request.form.get('role')
        if new_role:
            user.role = new_role
            db.session.commit()
            flash('User role updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('edit_user.html', user=user)

@bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Access restricted to admin only', 'danger')
        return redirect(url_for('dashboard.index'))

    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('admin.manage_users'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        print(f"Error deleting user: {e}")
        flash('An error occurred while deleting the user.', 'danger')

    return redirect(url_for('admin.manage_users'))
