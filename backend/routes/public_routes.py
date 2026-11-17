from flask import Blueprint
from sqlalchemy import func
from models import db, User, Trek, Booking
from cache import cached_response

public_bp = Blueprint("public", __name__, url_prefix="/api/public")


@public_bp.route("/stats")
def public_stats():
    """Landing page numbers. No login needed, so no personal / sensitive data here."""

    def build():
        popular = (
            db.session.query(Trek.trek_name, func.count(Booking.id))
            .join(Booking, Booking.trek_id == Trek.id)
            .filter(Booking.status != "Cancelled")
            .group_by(Trek.id)
            .order_by(func.count(Booking.id).desc())
            .limit(5)
            .all()
        )
        return {
            "total_treks": Trek.query.filter(Trek.status.in_(["Approved", "Open", "Ongoing", "Completed"])).count(),
            "open_treks": Trek.query.filter_by(status="Open").count(),
            "completed_treks": Trek.query.filter_by(status="Completed").count(),
            "trekkers": User.query.filter_by(role="user").count(),
            "popular": [{"name": p[0], "count": p[1]} for p in popular],
        }

    return cached_response("public:stats", build)
    