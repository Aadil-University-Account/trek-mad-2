from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='user')
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='user', lazy=True)
    staff_profile = db.relationship('StaffProfile', backref='user', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'phone': self.phone,
            'is_active': self.is_active,
            'is_blacklisted': self.is_blacklisted,
            'created_at': self.created_at.strftime("%Y-%m-%d"),
        }

class StaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    experience_years = db.Column(db.Integer, default=0)
    specialization = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default="Active") 

    treks = db.relationship("Trek", backref="staff", lazy=True)


    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.user.name,
            "email": self.user.email,
            "phone": self.user.phone,
            "experience_years": self.experience_years,
            "specialization": self.specialization,
            "status": self.status,
            "is_active": self.user.is_active,
            "is_blacklisted": self.user.is_blacklisted,
            "assigned_treks": [t.trek_name for t in self.treks],
        }
class Trek(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trek_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    difficulty_level = db.Column(db.String(50), nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)


     # Pending / Approved / Open / Closed / Ongoing / Completed
    status = db.Column(db.String(20), default="Pending")

    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('staff_profile.id'), nullable=True)

    bookings = db.relationship('Booking', backref='trek', lazy=True)

    def to_dict(self):
        booked = len([b for b in self.bookings if b.status != "Cancelled"])
        return {
            "id": self.id,
            "trek_name": self.trek_name,
            "location": self.location,
            "difficulty": self.difficulty,
            "duration_days": self.duration_days,
            "total_slots": self.total_slots,
            "available_slots": self.available_slots,
            "price": self.price,
            "description": self.description,
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d"),
            "status": self.status,
            "assigned_staff_id": self.assigned_staff_id,
            "staff_name": self.staff.user.name if self.staff else None,
            "registered_count": booked,
        }

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("trek.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Booked")  # Booked / Cancelled / Completed
    payment_status = db.Column(db.String(20), default="Pending")  # Pending / Paid

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "user_name": self.user.name,
            "user_email": self.user.email,
            "trek_id": self.trek_id,
            "trek_name": self.trek.trek_name,
            "location": self.trek.location,
            "trek_status": self.trek.status,
            "start_date": self.trek.start_date.strftime("%Y-%m-%d"),
            "end_date": self.trek.end_date.strftime("%Y-%m-%d"),
            "price": self.trek.price,
            "booking_date": self.booking_date.strftime("%Y-%m-%d %H:%M"),
            "status": self.status,
            "payment_status": self.payment_status,
        }


# Simple in-app notifications (booking confirmed / cancelled / export ready ...)
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    message = db.Column(db.String(300), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.strftime("%d %b %H:%M"),
        }


def notify(user_id, message):
    """Add a notification (the caller commits)."""
    db.session.add(Notification(user_id=user_id, message=message))