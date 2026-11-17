import os
from celery.result import AsyncResult
from flask import Blueprint, jsonify, g, send_from_directory
from auth_utils import role_required
from celery_worker import celery

job_bp = Blueprint("jobs", __name__, url_prefix="/api")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(BASE_DIR, "static", "exports")
REPORT_DIR = os.path.join(BASE_DIR, "static", "reports")


# ------------------------------------------------ user: export booking history
@job_bp.route("/export", methods=["POST"])
@role_required("user")
def start_export():
    task = celery.send_task("tasks.export_tasks.export_history", args=[g.user.id])
    return jsonify({"task_id": task.id, "message": "Export started"}), 202


@job_bp.route("/export/status/<task_id>")
@role_required("user")
def export_status(task_id):
    result = AsyncResult(task_id, app=celery)
    if result.successful():
        return jsonify({"state": "SUCCESS", "filename": result.result})
    return jsonify({"state": "FAILURE" if result.failed() else "PENDING"})


@job_bp.route("/export/download/<filename>")
@role_required("user")
def download_export(filename):
    # a user can download only his own file
    if filename != f"trek_history_user_{g.user.id}.csv":
        return jsonify({"message": "Access denied"}), 403
    return send_from_directory(EXPORT_DIR, filename, as_attachment=True)


# ------------------------------------------------------- admin: reports / jobs
@job_bp.route("/admin/report", methods=["POST"])
@role_required("admin")
def run_report_now():
    celery.send_task("tasks.reminder_tasks.monthly_activity_report")
    return jsonify({"message": "Report job started. Refresh the list in a few seconds."}), 202


@job_bp.route("/admin/reminders", methods=["POST"])
@role_required("admin")
def run_reminders_now():
    celery.send_task("tasks.reminder_tasks.daily_trek_reminder")
    return jsonify({"message": "Reminder job started."}), 202


@job_bp.route("/admin/reports")
@role_required("admin")
def list_reports():
    os.makedirs(REPORT_DIR, exist_ok=True)
    files = sorted([f for f in os.listdir(REPORT_DIR) if f.endswith(".html")], reverse=True)
    return jsonify(files)


@job_bp.route("/admin/reports/<filename>")
@role_required("admin")
def view_report(filename):
    return send_from_directory(REPORT_DIR, filename)