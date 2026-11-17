from datetime import date
from flask import Blueprint, request, jsonify, g
from werkzeug.security import generate_password_hash
from models import db, Trek, Booking
from auth_utils import role_required

user_bp = Blueprint("user", __name__, url_prefix="/api")

VISIBLE_STATUS = ["Approved", "Open"]  # trekkers can see only approved / open treks


# ------------------------------------------------------------------- treks
@user_bp.route("/treks")
@role_required("user", "admin", "staff")
def list_treks():
    """Search + filter by difficulty, location and duration."""
    q = (request.args.get("q") or "").strip()
    difficulty = request.args.get("difficulty")
    location = (request.args.get("location") or "").strip()
    duration_min = request.args.get("duration_min", type=int)
    duration_max = request.args.get("duration_max", type=int)

    query = Trek.query.filter(Trek.status.in_(VISIBLE_STATUS))
    if q:
        query = query.filter(Trek.trek_name.ilike(f"%{q}%") | Trek.location.ilike(f"%{q}%"))
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location == location)
    if duration_min:
        query = query.filter(Trek.duration_days >= duration_min)
    if duration_max:
        query = query.filter(Trek.duration_days <= duration_max)

    treks = query.order_by(Trek.start_date).all()
    return jsonify([t.to_dict() for t in treks])


@user_bp.route("/locations")
@role_required("user", "admin", "staff")
def locations():
    rows = db.session.query(Trek.location).filter(Trek.status.in_(VISIBLE_STATUS)).distinct().all()
    return jsonify(sorted(r[0] for r in rows))


# ----------------------------------------------------------------- booking
@user_bp.route("/bookings", methods=["POST"])
@role_required("user")
def book_trek():
    trek_id = (request.get_json() or {}).get("trek_id")
    trek = db.session.get(Trek, int(trek_id)) if trek_id else None
    if not trek:
        return jsonify({"message": "Trek not found"}), 404

    # booking rules
    if trek.status != "Open":
        return jsonify({"message": "Booking is not open for this trek"}), 400
    if trek.start_date < date.today():
        return jsonify({"message": "This trek has already started"}), 400

    already = Booking.query.filter(
        Booking.user_id == g.user.id, Booking.trek_id == trek.id, Booking.status != "Cancelled"
    ).first()
    if already:
        return jsonify({"message": "You have already booked this trek"}), 400

    if trek.available_slots <= 0:
        return jsonify({"message": "Sorry, this trek is full"}), 400

    booking = Booking(user_id=g.user.id, trek_id=trek.id, status="Booked", payment_status="Pending")
    trek.available_slots -= 1
    db.session.add(booking)
    db.session.commit()
    return jsonify({"message": "Trek booked successfully!", "booking": booking.to_dict()}), 201


@user_bp.route("/my-bookings")
@role_required("user")
def my_bookings():
    """Only the logged in user's own bookings."""
    rows = Booking.query.filter_by(user_id=g.user.id).order_by(Booking.id.desc()).all()
    return jsonify([b.to_dict() for b in rows])


# ----------------------------------------------------------------- profile
@user_bp.route("/profile")
@role_required("user")
def get_profile():
    return jsonify(g.user.to_dict())


@user_bp.route("/profile", methods=["PUT"])
@role_required("user")
def update_profile():
    data = request.get_json() or {}
    name = (data.get("name") or "").strip()
    phone = (data.get("phone") or "").strip()

    if not name:
        return jsonify({"message": "Name is required"}), 400
    if phone and (not phone.isdigit() or len(phone) != 10):
        return jsonify({"message": "Phone must be 10 digits"}), 400

    g.user.name = name
    g.user.phone = phone
    if data.get("password"):
        if len(data["password"]) < 6:
            return jsonify({"message": "Password must be at least 6 characters"}), 400
        g.user.password_hash = generate_password_hash(data["password"])
    db.session.commit()
    return jsonify({"message": "Profile updated", "name": g.user.name})