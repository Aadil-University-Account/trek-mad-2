# TrekMate - Trekking Management Application (V2)

Modern Application Development II (MAD-II) project.
A role based web application to manage trekking activities for **Admin**, **Trek Staff** and **Users (Trekkers)**.

| Layer | Technology |
|-------|-----------|
| API | Flask + Flask-SQLAlchemy |
| Authentication | JWT (Flask-JWT-Extended) |
| UI | Vue 3 (Vite) + Vue Router + Axios |
| Styling | Bootstrap 5 (+ a small custom theme) |
| Database | SQLite (created from code) |
| Cache | Redis |
| Batch jobs | Celery + Celery Beat + Redis |
| Charts | Chart.js |

## Features

**Admin** (created automatically): dashboard (treks, users, staff, bookings), create/update/delete treks, approve treks,
add staff, assign staff to treks, search treks/staff/users, deactivate or blacklist users and staff,
view all bookings and history, charts and monthly reports.

**Trek Staff** (created by admin): see only assigned treks, registered count, update available slots,
open/close booking, start trek, mark completed, view and remove participants.

**User (Trekker)**: register/login, edit profile, browse approved/open treks, search and filter
(difficulty, location, duration), book a trek, cancel, pay (simulated), see booking status and full history,
export history as CSV (async job), notifications.

**Rules implemented**: no overbooking, booking only when trek is *Open*, no duplicate booking, only the
assigned staff can manage a trek, users see only their own bookings.

**Background jobs (Celery)**: daily reminder (9:00 AM), monthly HTML report (1st of month, 8:00 AM),
user triggered CSV export.  **Redis caching**: trek list, locations and public stats (60 s expiry, cleared on change).

## Folder structure

```
trekking-management-app-v2/
├── backend/
│   ├── app.py              # Flask app, DB creation, admin creation, blueprints
│   ├── models.py           # User, StaffProfile, Trek, Booking, Notification
│   ├── auth_utils.py       # role_required decorator (RBAC)
│   ├── cache.py            # Redis cache helper
│   ├── celery_worker.py    # Celery app + beat schedule
│   ├── seed.py             # optional demo data
│   ├── requirements.txt
│   ├── routes/             # auth, admin, staff, user, booking, job, public
│   ├── tasks/              # reminder, monthly report, csv export, mail helper
│   └── static/             # exports/ and reports/ (generated files)
├── frontend/
│   ├── index.html, vite.config.js, package.json
│   ├── public/             # PWA manifest, service worker, icons
│   └── src/
│       ├── main.js, App.vue, api.js, auth.js
│       ├── router/index.js
│       ├── views/          # Landing, Login, Register, Admin, Staff, User
│       └── components/     # all dashboards, tables, charts, modal ...
└── README.md
```

## How to run (local)

You need: **Python 3.10+, Node.js 18+, Redis**.

### 1. Redis
```bash
redis-server            # Linux/Mac/WSL      (check with: redis-cli ping -> PONG)
```

### 2. Backend (terminal 1)
```bash
cd backend
python -m venv env
source env/bin/activate          # Windows: env\Scripts\activate
pip install -r requirements.txt
python seed.py                   # optional demo data
python app.py                    # API on http://127.0.0.1:5000
```
The database file (`backend/instance/trekking.sqlite3`) and the admin user are created by the code on first start.

### 3. Celery worker (terminal 2) and beat (terminal 3)
```bash
cd backend && source env/bin/activate
celery -A celery_worker worker --loglevel=info -P solo      # -P solo works on Windows too
celery -A celery_worker beat --loglevel=info                # scheduled jobs
```

### 4. Frontend (terminal 4)
```bash
cd frontend
npm install
npm run dev                      # open http://localhost:5173
```

### 5. (Optional) See the e-mails
Mails are sent to a local SMTP server on port 1025 (for example [MailHog](https://github.com/mailhog/MailHog)).
If no SMTP server is running, every mail is still saved as an HTML file in `backend/outbox/`.
To also send reminders to Google Chat: `export GCHAT_WEBHOOK_URL="<your webhook url>"` before starting the worker.

## Login details

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@trek.com | admin123 |
| Staff (after `seed.py`) | staff1@trek.com | staff123 |
| User (after `seed.py`) | user1@trek.com | user123 |


## API summary

| Method | Endpoint | Who |
|--------|----------|-----|
| POST | /api/register, /api/login | public |
| GET | /api/me | any |
| GET | /api/admin/dashboard, /stats, /treks, /staff, /users, /bookings | admin |
| POST/PUT/DELETE | /api/admin/treks, /treks/<id>, /treks/<id>/approve, /treks/<id>/assign | admin |
| POST/PUT | /api/admin/staff, /staff/<id> | admin |
| PUT | /api/admin/accounts/<user_id>/status | admin |
| POST | /api/admin/report, /api/admin/reminders | admin |
| GET | /api/admin/reports, /api/admin/reports/<file> | admin |
| GET | /api/staff/treks, /treks/<id>/participants | staff |
| PUT | /api/staff/treks/<id>/slots, /treks/<id>/status, /bookings/<id>/cancel | staff |
| GET | /api/treks, /api/locations, /api/my-bookings, /api/profile | user |
| POST | /api/bookings | user |
| PUT | /api/bookings/<id>/cancel, /bookings/<id>/pay, /api/profile | user |
| GET/PUT | /api/notifications, /notifications/read | user |
| POST/GET | /api/export, /export/status/<task_id>, /export/download/<file> | user |
| GET | /api/public/stats | public |

