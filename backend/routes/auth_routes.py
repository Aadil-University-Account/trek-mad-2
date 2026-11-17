from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from auth_utils import role_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api")


@auth_bp.route("/register", methods=["POST"])
def register():
    """Only trekkers can self register."""
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    phone = (data.get("phone") or "").strip()

    if not name or not email or not password:
        return jsonify({"message": "Name, email and password are required"}), 400
    if "@" not in email:
        return jsonify({"message": "Enter a valid email"}), 400
    if len(password) < 6:
        return jsonify({"message": "Password must be at least 6 characters"}), 400
    if phone and (not phone.isdigit() or len(phone) != 10):
        return jsonify({"message": "Phone must be 10 digits"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 400

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        phone=phone,
        role="user",
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Registered successfully. Please login."}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """Same login for admin, staff and trekkers."""
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"message": "Invalid email or password"}), 401
    if user.is_blacklisted or not user.is_active:
        return jsonify({"message": "Your account is deactivated. Contact admin."}), 403

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "role": user.role, "name": user.name, "id": user.id})


@auth_bp.route("/me")
@role_required("admin", "staff", "user")
def me():
    return jsonify(g.user.to_dict())