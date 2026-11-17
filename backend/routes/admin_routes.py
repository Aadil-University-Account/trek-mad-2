from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from models import db, User, StaffProfile, Trek, Booking
from auth_utils import role_required
from cache import clear_trek_cache

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

DIFFICULTY = ["Easy", "Moderate", "Hard"]


# ---------------------------------------------------------------- dashboard
@admin_bp.route("/dashboard")
@role_required("admin")
def dashboard():
    return jsonify(
        {
            "total_treks": Trek.query.count(),
            "total_users": User.query.filter_by(role="user").count(),
            "total_staff": User.query.filter_by(role="staff").count(),
            "total_bookings": Booking.query.count(),
        }
    )


# -------------------------------------------------------------------- treks
def read_trek_data(data):
    """Validate trek form data. Returns (clean_data, error_message)."""
    try:
        clean = {
            "trek_name": (data.get("trek_name") or "").strip(),
            "location": (data.get("location") or "").strip(),
            "difficulty": data.get("difficulty"),
            "duration_days": int(data.get("duration_days")),
            "total_slots": int(data.get("total_slots")),
            "price": float(data.get("price") or 0),
            "description": (data.get("description") or "").strip(),
            "start_date": datetime.strptime(data.get("start_date"), "%Y-%m-%d").date(),
        }
    except (TypeError, ValueError):
        return None, "Please fill all fields with valid values"

    if not clean["trek_name"] or not clean["location"]:
        return None, "Trek name and location are required"
    if clean["difficulty"] not in DIFFICULTY:
        return None, "Difficulty must be Easy, Moderate or Hard"
    if clean["duration_days"] < 1 or clean["total_slots"] < 1 or clean["price"] < 0:
        return None, "Duration and slots must be at least 1, price cannot be negative"

    clean["end_date"] = clean["start_date"] + timedelta(days=clean["duration_days"] - 1)
    return clean, None


def active_booking_count(trek):
    return len([b for b in trek.bookings if b.status != "Cancelled"])


@admin_bp.route("/treks")
@role_required("admin")
def list_treks():
    q = (request.args.get("q") or "").strip()
    query = Trek.query
    if q:
        if q.isdigit():
            query = query.filter(Trek.id == int(q))
        else:
            query = query.filter(Trek.trek_name.ilike(f"%{q}%") | Trek.location.ilike(f"%{q}%"))
    return jsonify([t.to_dict() for t in query.order_by(Trek.id.desc()).all()])


@admin_bp.route("/treks", methods=["POST"])
@role_required("admin")
def create_trek():
    clean, error = read_trek_data(request.get_json() or {})
    if error:
        return jsonify({"message": error}), 400

    trek = Trek(**clean, available_slots=clean["total_slots"], status="Pending")
    staff_id = (request.get_json() or {}).get("assigned_staff_id")
    if staff_id:
        if not db.session.get(StaffProfile, int(staff_id)):
            return jsonify({"message": "Staff not found"}), 404
        trek.assigned_staff_id = int(staff_id)

    db.session.add(trek)
    db.session.commit()
    clear_trek_cache()
    return jsonify({"message": "Trek created (status: Pending)", "trek": trek.to_dict()}), 201


@admin_bp.route("/treks/<int:trek_id>", methods=["PUT"])
@role_required("admin")
def update_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    clean, error = read_trek_data(request.get_json() or {})
    if error:
        return jsonify({"message": error}), 400

    booked = active_booking_count(trek)
    if clean["total_slots"] < booked:
        return jsonify({"message": f"{booked} users already booked. Slots cannot be less than that."}), 400

    for key, value in clean.items():
        setattr(trek, key, value)
    trek.available_slots = clean["total_slots"] - booked
    db.session.commit()
    clear_trek_cache()
    return jsonify({"message": "Trek updated", "trek": trek.to_dict()})


@admin_bp.route("/treks/<int:trek_id>", methods=["DELETE"])
@role_required("admin")
def delete_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404
    if trek.bookings:
        return jsonify({"message": "This trek has bookings, so it cannot be removed. Close it instead."}), 400
    db.session.delete(trek)
    db.session.commit()
    clear_trek_cache()
    return jsonify({"message": "Trek removed"})


@admin_bp.route("/treks/<int:trek_id>/approve", methods=["POST"])
@role_required("admin")
def approve_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404
    if trek.status != "Pending":
        return jsonify({"message": "Only pending treks can be approved"}), 400
    trek.status = "Approved"
    db.session.commit()
    clear_trek_cache()
    return jsonify({"message": "Trek approved. Staff can now open it for booking."})


@admin_bp.route("/treks/<int:trek_id>/assign", methods=["POST"])
@role_required("admin")
def assign_staff(trek_id):
    trek = db.session.get(Trek, trek_id)
    staff = db.session.get(StaffProfile, int((request.get_json() or {}).get("staff_id") or 0))
    if not trek or not staff:
        return jsonify({"message": "Trek or staff not found"}), 404
    if staff.user.is_blacklisted or not staff.user.is_active:
        return jsonify({"message": "This staff account is deactivated"}), 400
    trek.assigned_staff_id = staff.id
    db.session.commit()
    clear_trek_cache()
    return jsonify({"message": f"{staff.user.name} assigned to {trek.trek_name}"})


# -------------------------------------------------------------------- staff
@admin_bp.route("/staff")
@role_required("admin")
def list_staff():
    q = (request.args.get("q") or "").strip()
    query = StaffProfile.query.join(User)
    if q:
        if q.isdigit():
            query = query.filter(StaffProfile.id == int(q))
        else:
            query = query.filter(User.name.ilike(f"%{q}%") | User.email.ilike(f"%{q}%"))
    return jsonify([s.to_dict() for s in query.all()])


@admin_bp.route("/staff", methods=["POST"])
@role_required("admin")
def create_staff():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    phone = (data.get("phone") or "").strip()

    if not name or "@" not in email or len(password) < 6:
        return jsonify({"message": "Name, valid email and password (min 6) are required"}), 400
    if phone and (not phone.isdigit() or len(phone) != 10):
        return jsonify({"message": "Phone must be 10 digits"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    user = User(name=name, email=email, phone=phone, role="staff", password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.flush()  # get user.id
    profile = StaffProfile(
        user_id=user.id,
        experience_years=int(data.get("experience_years") or 0),
        specialization=(data.get("specialization") or "").strip(),
    )
    db.session.add(profile)
    db.session.commit()
    clear_trek_cache()
    return jsonify({"message": "Staff created", "staff": profile.to_dict()}), 201


@admin_bp.route("/staff/<int:staff_id>", methods=["PUT"])
@role_required("admin")
def update_staff(staff_id):
    profile = db.session.get(StaffProfile, staff_id)
    if not profile:
        return jsonify({"message": "Staff not found"}), 404
    data = request.get_json() or {}

    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()
    if not name:
        return jsonify({"message": "Name is required"}), 400
    if phone and (not phone.isdigit() or len(phone) != 10):
        return jsonify({"message": "Phone must be 10 digits"}), 400

    profile.user.name = name
    profile.user.phone = phone
    profile.experience_years = int(data.get("experience_years") or 0)
    profile.specialization = (data.get("specialization") or "").strip()
    if data.get("password"):
        if len(data["password"]) < 6:
            return jsonify({"message": "Password must be at least 6 characters"}), 400
        profile.user.password_hash = generate_password_hash(data["password"])
    db.session.commit()
    clear_trek_cache()
    return jsonify({"message": "Staff updated"})


# ------------------------------------------------------------ users / accounts
@admin_bp.route("/users")
@role_required("admin")
def list_users():
    q = (request.args.get("q") or "").strip()
    query = User.query.filter_by(role="user")
    if q:
        if q.isdigit():
            query = query.filter(User.id == int(q))
        else:
            query = query.filter(User.name.ilike(f"%{q}%") | User.email.ilike(f"%{q}%"))
    return jsonify([u.to_dict() for u in query.order_by(User.id.desc()).all()])


@admin_bp.route("/accounts/<int:user_id>/status", methods=["PUT"])
@role_required("admin")
def change_account_status(user_id):
    """Deactivate / blacklist (or restore) a user or a staff account."""
    user = db.session.get(User, user_id)
    if not user or user.role == "admin":
        return jsonify({"message": "Account not found"}), 404

    data = request.get_json() or {}
    if "is_active" in data:
        user.is_active = bool(data["is_active"])
    if "is_blacklisted" in data:
        user.is_blacklisted = bool(data["is_blacklisted"])

    if user.staff_profile:
        blocked = user.is_blacklisted or not user.is_active
        user.staff_profile.status = "Inactive" if blocked else "Active"
    db.session.commit()
    clear_trek_cache()
    return jsonify({"message": "Account updated"})


# ----------------------------------------------------------------- bookings
@admin_bp.route("/bookings")
@role_required("admin")
def all_bookings():
    """All booking records = complete trekking history of the system."""
    q = (request.args.get("q") or "").strip()
    status = request.args.get("status")
    query = Booking.query.join(User).join(Trek)
    if q:
        if q.isdigit():
            query = query.filter((Booking.id == int(q)) | (Booking.user_id == int(q)))
        else:
            query = query.filter(User.name.ilike(f"%{q}%") | Trek.trek_name.ilike(f"%{q}%"))
    if status:
        query = query.filter(Booking.status == status)
    return jsonify([b.to_dict() for b in query.order_by(Booking.id.desc()).all()])