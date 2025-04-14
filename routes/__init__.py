from functools import wraps
from flask import jsonify, redirect, url_for, flash
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_login import current_user
from models import User, RolePermission

def has_permission(table_name, action):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                # ✅ Try to use JWT first if present
                verify_jwt_in_request(optional=True)
                user_id = get_jwt_identity()
                if user_id:
                    user = User.query.get(user_id)
                else:
                    user = current_user if current_user.is_authenticated else None
            except:
                user = current_user if current_user.is_authenticated else None

            if not user:
                return jsonify({"error": "User not authenticated"}), 403

            # ✅ Admins bypass permission checks
            if user.role.role_name == 'Admin':
                return f(*args, **kwargs)

            # ✅ Check permission
            permission = RolePermission.query.filter_by(role_id=user.role_id, table_name=table_name).first()
            if not permission or not getattr(permission, f"can_{action}", False):
                return jsonify({"error": "Access denied"}), 403

            return f(*args, **kwargs)
        return wrapper
    return decorator
