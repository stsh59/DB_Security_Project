# utils.py
from models import Role, RolePermission
from models import AuditLog, db
from flask import request

def check_permission(user, table_name, permission):
    if not user or not hasattr(user, 'role') or not user.role:
        return False
    if user.role.role_name == 'Admin':
        return True
    return any(p.table_name == table_name and getattr(p, f'can_{permission}') for p in user.role.permissions)

def log_audit(user, action, table_name, record_id=None):
    if not user:
        return

    log = AuditLog(
        username=user.username,
        role=user.role.role_name,
        action=action,
        table_name=table_name,
        record_id=str(record_id) if record_id else None,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()
