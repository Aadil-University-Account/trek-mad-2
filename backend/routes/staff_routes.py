from flask import Blueprint, request, jsonify, g
from models import db, Trek, Booking, notify
from auth_utils import role_required

staff_bp = Blueprint("staff", __name__, url_prefix="/api/staff")

# status the staff is allowed to move a trek to (Pending -> Approved is done by admin)
ALLOWED_CHANGES = {
    "Approved": ["Open", "Closed"],
    "Open": ["Closed", "Ongoing"],
    "Closed": ["Open", "Ongoing"],
    "Ongoing": ["Completed"],
}


def my_trek(trek_id):
    """Return the trek only if it is assigned to the logged in staff."""
    profile = g.user.staff_profile
    trek = db.session.get(Trek, trek_id)
    if not trek or not profile or trek.assigned_staff_id != profile.id:
        return None
    return trek


@staff_bp.route("/treks")
@role_required("staff")
def assigned_treks():
    profile = g.user.staff_profile
    treks = Trek.query.filter_by(assigned_staff_id=profile.id).order_by(Trek.start_date).all()
    return jsonify([t.to_dict() for t in treks])


@staff_bp.route("/treks/<int:trek_id>/slots", methods=["PUT"])
@role_required("staff")
def update_slots(trek_id):
    trek = my_trek(trek_id)
    if not trek:
        return jsonify({"message": "This trek is not assigned to you"}), 403
    if trek.status in ("Ongoing", "Completed"):
        return jsonify({"message": "Slots cannot be changed now"}), 400

    try:
        slots = int((request.get_json() or {}).get("available_slots"))
    except (TypeError, ValueError):
        return jsonify({"message": "Enter a valid number"}), 400
    if slots < 0:
        return jsonify({"message": "Slots cannot be negative"}), 400

    booked = trek.total_slots - trek.available_slots
    trek.available_slots = slots
    trek.total_slots = booked + slots  # keep total = booked + available
    db.session.commit()
    return jsonify({"message": "Available slots updated"})


@staff_bp.route("/treks/<int:trek_id>/status", methods=["PUT"])
@role_required("staff")
def update_status(trek_id):
    trek = my_trek(trek_id)
    if not trek:
        return jsonify({"message": "This trek is not assigned to you"}), 403

    new_status = (request.get_json() or {}).get("status")
    if new_status not in ALLOWED_CHANGES.get(trek.status, []):
        return jsonify({"message": f"Cannot change status from {trek.status} to {new_status}"}), 400

    trek.status = new_status
    if new_status == "Completed":
        # everyone who is still booked has now completed the trek
        for b in trek.bookings:
            if b.status == "Booked":
                b.status = "Completed"
                notify(b.user_id, f"{trek.trek_name} is completed. Hope you enjoyed the trek!")
    db.session.commit()
    return jsonify({"message": f"Trek marked as {new_status}"})


@staff_bp.route("/treks/<int:trek_id>/participants")
@role_required("staff")
def participants(trek_id):
    trek = my_trek(trek_id)
    if not trek:
        return jsonify({"message": "This trek is not assigned to you"}), 403
    rows = []
    for b in trek.bookings:
        rows.append(
            {
                "booking_id": b.id,
                "name": b.user.name,
                "email": b.user.email,
                "phone": b.user.phone,
                "booking_date": b.booking_date.strftime("%Y-%m-%d %H:%M"),
                "status": b.status,
                "payment_status": b.payment_status,
            }
        )
    return jsonify(rows)


@staff_bp.route("/bookings/<int:booking_id>/cancel", methods=["PUT"])
@role_required("staff")
def remove_participant(booking_id):
    """Staff can remove a participant from their own trek."""
    booking = db.session.get(Booking, booking_id)
    if not booking or not my_trek(booking.trek_id):
        return jsonify({"message": "This booking is not for your trek"}), 403
    if booking.status != "Booked" or booking.trek.status in ("Ongoing", "Completed"):
        return jsonify({"message": "This booking cannot be cancelled"}), 400

    booking.status = "Cancelled"
    booking.trek.available_slots += 1
    notify(booking.user_id, f"Your booking for {booking.trek.trek_name} was cancelled by the trek staff.")
    db.session.commit()
    return jsonify({"message": "Participant removed and slot released"})