"""
app.py — Main Flask application for UGV Smart Assistant.
Run: python app.py
Then open: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import sqlite3
import os

from chatbot import get_response
from database import get_connection

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "ugv-secret-2026")


# ── Helper ────────────────────────────────────────────────────────
def db_query(sql, params=()):
    conn = get_connection()
    results = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in results]


# ── Pages ─────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Main chat page."""
    return render_template("index.html")


@app.route("/exam-routine")
def exam_routine():
    """Exam routine browser page."""
    semesters = db_query(
        "SELECT DISTINCT semester FROM exam_routine ORDER BY semester"
    )
    return render_template("exam_routine.html", semesters=semesters)


@app.route("/admin")
def admin():
    """Admin panel page."""
    return render_template("admin.html")


# ── API Endpoints ─────────────────────────────────────────────────

@app.route("/api/chat", methods=["POST"])
def chat():
    """Receive user message, return chatbot response."""
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "No message provided"}), 400

    user_message = data["message"].strip()
    response = get_response(user_message)
    return jsonify({"response": response})


@app.route("/api/exam-routine")
def api_exam_routine():
    """Return exam routine data with optional filters."""
    semester = request.args.get("semester")
    search = request.args.get("search", "").strip()

    sql = "SELECT * FROM exam_routine WHERE 1=1"
    params = []

    if semester and semester.isdigit():
        sql += " AND semester = ?"
        params.append(int(semester))

    if search:
        sql += " AND (LOWER(course_name) LIKE ? OR LOWER(course_code) LIKE ?)"
        params.extend([f"%{search.lower()}%", f"%{search.lower()}%"])

    sql += " ORDER BY semester, exam_date"
    results = db_query(sql, params)
    return jsonify(results)


@app.route("/api/notices")
def api_notices():
    """Return latest notices."""
    results = db_query("SELECT * FROM notices ORDER BY date DESC LIMIT 10")
    return jsonify(results)


@app.route("/api/teachers")
def api_teachers():
    """Return teacher list."""
    results = db_query("SELECT * FROM teachers ORDER BY name")
    return jsonify(results)


# ── Admin API ─────────────────────────────────────────────────────

@app.route("/api/admin/exam", methods=["POST"])
def admin_add_exam():
    """Add a new exam routine entry."""
    data = request.get_json()
    required = ["department", "semester", "course_code", "course_name", "exam_date", "exam_time"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_connection()
    conn.execute("""
        INSERT INTO exam_routine (department, semester, course_code, course_name, exam_date, exam_time, room)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        data["department"], data["semester"], data["course_code"],
        data["course_name"], data["exam_date"], data["exam_time"],
        data.get("room", "TBA")
    ))
    conn.commit()
    conn.close()
    return jsonify({"success": True, "message": "Exam added successfully!"})


@app.route("/api/admin/exam/<int:exam_id>", methods=["DELETE"])
def admin_delete_exam(exam_id):
    """Delete an exam routine entry."""
    conn = get_connection()
    conn.execute("DELETE FROM exam_routine WHERE id = ?", (exam_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


# ── Run ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Check if database exists
    if not os.path.exists("database.db"):
        print("⚠️  Database not found. Run: python database.py")
    app.run(debug=True, host="0.0.0.0", port=5000)
