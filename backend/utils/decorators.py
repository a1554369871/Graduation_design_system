from functools import wraps
from flask_jwt_extended import get_jwt_identity
from flask import jsonify
from models.user import User


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({'msg': '用户不存在或已禁用'}), 401
            if user.role not in roles:
                return jsonify({'msg': '权限不足'}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator
