import os
from datetime import date, timedelta
from flask import render_template_string
from sqlalchemy import func
from celery_worker import celery
from tasks.mail_helper import send_mail, send_gchat, BASE_DIR

REPORT_DIR = os.path.join(BASE_DIR, "static", "reports")

REPORT_HTML = """
<div style="font-family:Arial,sans-serif;max-width:640px;margin:auto;color:#0f172a">
  <h2 style="color:#0f766e">TrekMate - Monthly Activity Report</h2>
  <p style="color:#64748b">{{ month }}</p>
  <table cellpadding="12" style="width:100%;border-collapse:collapse;margin:16px 0">
    <tr>
      <td style="background:#e6f4f1;border-radius:8px"><b style="font-size:26px">{{ treks_conducted }}</b><br>Treks conducted</td>
      <td style="width:12px"></td>
      <td style="background:#e6f4f1;border-radius:8px"><b style="font-size:26px">{{ users_participated }}</b><br>Users participated</td>
      <td style="width:12px"></td>
      <td style="background:#e6f4f1;border-radius:8px"><b style="font-size:26px">{{ total_bookings }}</b><br>Bookings made</td>
    </tr>
  </table>
  <h3>Popular treks</h3>
  <table border="1" cellpadding="8" style="width:100%;border-collapse:collapse;border-color:#e5eaea">
    <tr style="background:#f8fafb"><th align="left">Trek</th><th align="left">Location</th><th>Bookings</th></tr>
    {% for t in popular %}
    <tr><td>{{ t[0] }}</td><td>{{ t[1] }}</td><td align="center">{{ t[2] }}</td></tr>
    {% else %}
    <tr><td colspan="3">No bookings in this month.</td></tr>
    {% endfor %}
  </table>
  <p style="color:#94a3b8;font-size:12px;margin-top:24px">Generated automatically by TrekMate.</p>
</div>
"""


@celery.task(name="tasks.reminder_tasks.daily_trek_reminder")
def daily_trek_reminder():
    """Runs every day. Reminds users whose trek starts in the next 3 days."""
    from app import app
    from models import db, Booking, Trek, notify

    with app.app_context():
        today = date.today()
        last_day = today + timedelta(days=3)
        bookings = (
            Booking.query.join(Trek)
            .filter(Booking.status == "Booked", Trek.start_date >= today, Trek.start_date <= last_day)
            .all()
        )
        for b in bookings:
            t = b.trek
            days_left = (t.start_date - today).days
            when = "today" if days_left == 0 else f"in {days_left} day(s)"
            html = f"""
            <h3>Hi {b.user.name}, your trek starts {when}!</h3>
            <p><b>{t.trek_name}</b> ({t.location})<br>Start date: {t.start_date} | Duration: {t.duration_days} day(s)</p>
            <p>Instructions: carry ID proof, water bottle, trekking shoes, warm clothes and reach the
            meeting point 30 minutes early. Your trek leader is {t.staff.user.name if t.staff else 'to be announced'}.</p>
            """
            send_mail(b.user.email, f"Reminder: {t.trek_name} starts {when}", html)
            send_gchat(f"Reminder for {b.user.name}: {t.trek_name} starts on {t.start_date}")
            notify(b.user_id, f"Reminder: {t.trek_name} starts {when} ({t.start_date}).")
        db.session.commit()
        print(f"Sent {len(bookings)} reminders")
        return len(bookings)


@celery.task(name="tasks.reminder_tasks.monthly_activity_report")
def monthly_activity_report():
    """Runs on the 1st of every month. Report is for the previous month."""
    from app import app
    from models import db, Booking, Trek, User

    with app.app_context():
        first_this_month = date.today().replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)

        # treks that were held in that month
        held = Trek.query.filter(
            Trek.start_date >= last_month_start,
            Trek.start_date <= last_month_end,
            Trek.status.in_(["Ongoing", "Completed"]),
        ).all()
        held_ids = [t.id for t in held]

        participants = set()
        if held_ids:
            rows = Booking.query.filter(Booking.trek_id.in_(held_ids), Booking.status == "Completed").all()
            participants = {b.user_id for b in rows}

        # popular treks = most (non cancelled) bookings made in that month
        popular = (
            db.session.query(Trek.trek_name, Trek.location, func.count(Booking.id))
            .join(Booking, Booking.trek_id == Trek.id)
            .filter(
                Booking.status != "Cancelled",
                func.date(Booking.booking_date) >= last_month_start,
                func.date(Booking.booking_date) <= last_month_end,
            )
            .group_by(Trek.id)
            .order_by(func.count(Booking.id).desc())
            .limit(5)
            .all()
        )
        total_bookings = Booking.query.filter(
            Booking.status != "Cancelled",
            func.date(Booking.booking_date) >= last_month_start,
            func.date(Booking.booking_date) <= last_month_end,
        ).count()

        html = render_template_string(
            REPORT_HTML,
            month=last_month_start.strftime("%B %Y"),
            treks_conducted=len(held),
            users_participated=len(participants),
            total_bookings=total_bookings,
            popular=popular,
        )

        os.makedirs(REPORT_DIR, exist_ok=True)
        filename = f"report_{last_month_start.strftime('%Y_%m')}.html"
        with open(os.path.join(REPORT_DIR, filename), "w", encoding="utf-8") as f:
            f.write(html)

        admin = User.query.filter_by(role="admin").first()
        send_mail(admin.email, f"Monthly trekking report - {last_month_start.strftime('%B %Y')}", html)
        return filename