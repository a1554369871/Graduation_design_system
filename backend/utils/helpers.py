from extensions import db
from models.system import SystemLog


def log_system(user_id, action, target_type=None, target_id=None, detail=None, ip_address=None):
    log = SystemLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        detail=detail,
        ip_address=ip_address,
    )
    db.session.add(log)
    db.session.commit()
