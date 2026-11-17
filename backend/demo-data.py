from datetime import date, datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app
from models import db, User, StaffProfile, Trek, Booking

today = date.today()


def add_user(name, email, password, role, phone):
    user = User(name=name, email=email, role=role, phone=phone, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.flush()
    return user


def add_trek(name, location, difficulty, days, slots, price, start_offset, status, staff, text):
    start = today + timedelta(days=start_offset)
    trek = Trek(
        trek_name=name, location=location, difficulty=difficulty, duration_days=days,
        total_slots=slots, available_slots=slots, price=price, description=text,
        start_date=start, end_date=start + timedelta(days=days - 1), status=status,
        assigned_staff_id=staff.id if staff else None,
    )
    db.session.add(trek)
    db.session.flush()
    return trek


def add_booking(user, trek, status="Booked", paid=False, days_ago=0):
    b = Booking(
        user_id=user.id, trek_id=trek.id, status=status,
        payment_status="Paid" if paid else "Pending",
        booking_date=datetime.utcnow() - timedelta(days=days_ago),
    )
    if status != "Cancelled":
        trek.available_slots -= 1
    db.session.add(b)


with app.app_context():
    if Trek.query.count() > 0:
        print("Database already has data. Seed skipped.")
        raise SystemExit

    s1 = add_user("Arjun Rawat", "staff1@trek.com", "staff123", "staff", "9000000001")
    s2 = add_user("Meera Sherpa", "staff2@trek.com", "staff123", "staff", "9000000002")
    p1 = StaffProfile(user_id=s1.id, experience_years=8, specialization="Himalayan treks")
    p2 = StaffProfile(user_id=s2.id, experience_years=5, specialization="Western Ghats & forest treks")
    db.session.add_all([p1, p2])
    db.session.flush()

    users = [add_user(f"Trekker {i}", f"user{i}@trek.com", "user123", "user", f"98000000{i:02d}") for i in range(1, 7)]

    # treks in different stages
    t_done1 = add_trek("Triund Trek", "Himachal Pradesh", "Easy", 2, 10, 2500, -40, "Completed", p1, "Short trek with views of Dhauladhar range.")
    t_done2 = add_trek("Valley of Flowers", "Uttarakhand", "Moderate", 5, 8, 7500, -35, "Completed", p1, "A UNESCO valley full of alpine flowers.")
    t_open1 = add_trek("Kedarkantha Winter Trek", "Uttarakhand", "Moderate", 6, 12, 9500, 20, "Open", p1, "Snow trek with a summit sunrise.")
    t_open2 = add_trek("Kudremukh Peak", "Karnataka", "Easy", 2, 15, 3000, 8, "Open", p2, "Grassy hills and shola forests.")
    t_open3 = add_trek("Roopkund Expedition", "Uttarakhand", "Hard", 9, 6, 15500, 30, "Open", p1, "High altitude mystery lake trek.")
    t_appr = add_trek("Harishchandragad", "Maharashtra", "Moderate", 2, 20, 2200, 45, "Approved", p2, "Cliffs, caves and the Konkan Kada.")
    t_pend = add_trek("Chadar Trek", "Ladakh", "Hard", 8, 8, 24000, 90, "Pending", None, "Walk on the frozen Zanskar river.")

    # bookings (some old ones so that charts and monthly report have data)
    add_booking(users[0], t_done1, "Completed", True, 50)
    add_booking(users[1], t_done1, "Completed", True, 48)
    add_booking(users[2], t_done1, "Completed", True, 45)
    add_booking(users[0], t_done2, "Completed", True, 40)
    add_booking(users[3], t_done2, "Completed", True, 38)
    add_booking(users[0], t_open1, "Booked", True, 5)
    add_booking(users[1], t_open1, "Booked", False, 3)
    add_booking(users[2], t_open2, "Booked", False, 1)
    add_booking(users[0], t_open2, "Booked", False, 1)
    add_booking(users[4], t_open3, "Cancelled", False, 2)
    db.session.commit()
    print("Demo data added.")
    print("  Staff : staff1@trek.com / staff123  (and staff2@trek.com)")
    print("  User  : user1@trek.com / user123   (user1 .. user6)")