# utils.py
from models import Role, RolePermission

def check_permission(user, table_name, permission):
    if not user or not hasattr(user, 'role') or not user.role:
        return False
    if user.role.role_name == 'Admin':
        return True
    return any(p.table_name == table_name and getattr(p, f'can_{permission}') for p in user.role.permissions)