from flask import Blueprint, jsonify, g
from models import db, Booking, Notification, notify
from auth_utils import role_required

booking_bp = Blueprint("booking", __name__, url_prefix="/api")


@booking_bp.route("/bookings/<int:booking_id>/cancel", methods=["PUT"])
@role_required("user")
def cancel_booking(booking_id):
    booking = db.session.get(Booking, booking_id)
    # users can only touch their own bookings
    if not booking or booking.user_id != g.user.id:
        return jsonify({"message": "Booking not found"}), 404
    if booking.status != "Booked":
        return jsonify({"message": f"A {booking.status} booking cannot be cancelled"}), 400
    if booking.trek.status in ("Ongoing", "Completed"):
        return jsonify({"message": "The trek has already started"}), 400

    booking.status = "Cancelled"
    booking.trek.available_slots += 1  # release the slot
    notify(g.user.id, f"Booking cancelled for {booking.trek.trek_name}.")
    db.session.commit()
    return jsonify({"message": "Booking cancelled"})


# --------------------------------------------------------------- notifications
@booking_bp.route("/notifications")
@role_required("user")
def my_notifications():
    rows = Notification.query.filter_by(user_id=g.user.id).order_by(Notification.id.desc()).limit(20).all()
    return jsonify([n.to_dict() for n in rows])


@booking_bp.route("/notifications/read", methods=["PUT"])
@role_required("user")
def mark_read():
    Notification.query.filter_by(user_id=g.user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return jsonify({"message": "ok"})