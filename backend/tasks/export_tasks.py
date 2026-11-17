import os
import csv
from celery_worker import celery
from tasks.mail_helper import BASE_DIR

EXPORT_DIR = os.path.join(BASE_DIR, "static", "exports")


@celery.task(name="tasks.export_tasks.export_history")
def export_history(user_id):
    """User triggered job: write the user's trekking history to a CSV file."""
    from app import app
    from models import db, Booking, notify

    with app.app_context():
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.id).all()

        os.makedirs(EXPORT_DIR, exist_ok=True)
        filename = f"trek_history_user_{user_id}.csv"
        with open(os.path.join(EXPORT_DIR, filename), "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["User ID", "Trek Name", "Location", "Booking Status", "Booking Date", "Start Date", "End Date"])
            for b in bookings:
                writer.writerow(
                    [b.user_id, b.trek.trek_name, b.trek.location, b.status,
                     b.booking_date.strftime("%Y-%m-%d"), b.trek.start_date, b.trek.end_date]
                )

        notify(user_id, "Your trekking history CSV export is ready to download.")
        db.session.commit()
        return filename