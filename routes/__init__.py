from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from models import User, RolePermission, db


def has_permission(table_name, action):
    """Check if the logged-in user has permission for a specific action (read/write/update/delete)."""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Get the user_id from JWT identity
            user_id = get_jwt_identity()

            # Fetch the user from the database
            user = User.query.filter_by(id=user_id).first()

            # If user not found, return 403 Forbidden error
            if not user:
                return jsonify({"error": "User not found"}), 403

            # Fetch the user's role and the associated permissions
            role_id = user.role_id
            permission = RolePermission.query.filter_by(role_id=role_id, table_name=table_name).first()

            # If no permissions are found or the user is not allowed to perform the action, deny access
            if not permission or not getattr(permission, f"can_{action}", False):
                return jsonify({"error": "Access denied"}), 403

            # If all checks pass, proceed with the original function
            return f(*args, **kwargs)

        return wrapper

    return decorator

