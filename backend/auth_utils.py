from functools import wraps
from flask import jsonify, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User


def role_required(*roles):
    """Protect a route: user must be logged in (JWT) and have one of the given roles."""

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def inner(*args, **kwargs):
            user = db.session.get(User, int(get_jwt_identity()))
            if not user:
                return jsonify({"message": "User not found"}), 401
            if user.is_blacklisted or not user.is_active:
                return jsonify({"message": "Your account is deactivated"}), 403
            if user.role not in roles:
                return jsonify({"message": "Access denied"}), 403
            g.user = user  # available inside the route
            return fn(*args, **kwargs)

        return inner

    return decorator