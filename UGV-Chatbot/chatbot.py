"""
chatbot.py — The AI brain of UGV Smart Assistant.
Combines database lookups with Gemini AI for smart responses.
"""

import sqlite3
import json
import os
import re
from datetime import datetime, date

# ── Load university data ─────────────────────────────────────────
with open("data/ugv_data.json", "r", encoding="utf-8") as f:
    UGV_DATA = json.load(f)

DB_PATH = "database.db"

# ── Gemini AI setup ──────────────────────────────────────────────
try:
    import google.generativeai as genai
    GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
    if GEMINI_KEY:
        genai.configure(api_key=GEMINI_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")
        AI_AVAILABLE = True
    else:
        AI_AVAILABLE = False
        print("⚠️  GEMINI_API_KEY not set. Running in rule-based mode.")
except ImportError:
    AI_AVAILABLE = False
    print("⚠️  google-generativeai not installed. Running in rule-based mode.")


def db_query(sql, params=()):
    """Execute a SQL query and return all results as dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    results = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in results]


# ────────────────────────────────────────────────────────────────
#  INTENT DETECTION
# ────────────────────────────────────────────────────────────────

def detect_intent(message: str):
    """Return the intent and any extracted entities from the message."""
    msg = message.lower().strip()

    # Exam routine keywords
    if any(k in msg for k in ["exam", "routine", "schedule", "পরীক্ষা", "রুটিন"]):
        # Extract semester number if mentioned
        sem = None
        for i in range(1, 9):
            if str(i) in msg or f"{i}th" in msg or f"{i}st" in msg or f"{i}nd" in msg or f"{i}rd" in msg:
                sem = i
                break
        # Extract specific course keywords
        course_hint = None
        for word in msg.split():
            if len(word) > 3 and word not in ["exam", "when", "what", "show", "routine", "schedule", "time"]:
                course_hint = word
                break
        return "exam_routine", {"semester": sem, "course_hint": course_hint, "raw": msg}

    # Admission keywords
    if any(k in msg for k in ["admission", "apply", "requirement", "ভর্তি", "আবেদন", "document"]):
        return "admission", {}

    # Teacher keywords
    if any(k in msg for k in ["teacher", "faculty", "professor", "head", "শিক্ষক"]):
        return "teacher", {}

    # Department keywords
    if any(k in msg for k in ["department", "cse", "bba", "english", "বিভাগ"]):
        return "department", {}

    # Scholarship keywords
    if any(k in msg for k in ["scholarship", "waiver", "bursary", "বৃত্তি"]):
        return "scholarship", {}

    # Notice keywords
    if any(k in msg for k in ["notice", "news", "announcement", "নোটিশ"]):
        return "notice", {}

    # Contact / location keywords
    if any(k in msg for k in ["contact", "address", "location", "email", "phone", "যোগাযোগ"]):
        return "contact", {}

    # Greeting
    if any(k in msg for k in ["hello", "hi", "hey", "হ্যালো", "নমস্কার", "আস্সালামু"]):
        return "greeting", {}

    return "general", {}


# ────────────────────────────────────────────────────────────────
#  RESPONSE BUILDERS
# ────────────────────────────────────────────────────────────────

def handle_greeting():
    return (
        "👋 **Assalamu Alaikum! Welcome to UGV Smart Assistant!**\n\n"
        "I can help you with:\n"
        "📚 Exam routines • 🎓 Admission info • 👩‍🏫 Teachers\n"
        "🏫 Departments • 📢 Notices • 🏆 Scholarships\n\n"
        "How can I assist you today?"
    )


def handle_exam_routine(entities: dict):
    semester = entities.get("semester")
    course_hint = entities.get("course_hint", "")
    raw = entities.get("raw", "")

    # Search by course name/code
    if course_hint and not semester:
        results = db_query(
            "SELECT * FROM exam_routine WHERE LOWER(course_name) LIKE ? OR LOWER(course_code) LIKE ? ORDER BY exam_date",
            (f"%{course_hint}%", f"%{course_hint}%")
        )
        if results:
            return _format_exam_results(results, f"Courses matching '{course_hint}'")
        return f"❌ No exam found matching **'{course_hint}'**. Try searching by course name or semester number."

    # Check for "tomorrow" or "today"
    if "tomorrow" in raw:
        tomorrow = (date.today().replace(day=date.today().day + 1)).strftime("%Y-%m-%d")
        results = db_query("SELECT * FROM exam_routine WHERE exam_date = ? ORDER BY exam_time", (tomorrow,))
        if results:
            return _format_exam_results(results, f"Exams on {tomorrow}")
        return f"✅ No exams scheduled for tomorrow ({tomorrow})."

    if "today" in raw:
        today = date.today().strftime("%Y-%m-%d")
        results = db_query("SELECT * FROM exam_routine WHERE exam_date = ? ORDER BY exam_time", (today,))
        if results:
            return _format_exam_results(results, f"Exams today ({today})")
        return f"✅ No exams scheduled for today ({today})."

    # Semester-specific
    if semester:
        results = db_query(
            "SELECT * FROM exam_routine WHERE semester = ? ORDER BY exam_date",
            (semester,)
        )
        if results:
            return _format_exam_results(results, f"Semester {semester} Exam Routine")
        return f"❌ No exam routine found for Semester {semester}."

    # Show all upcoming exams
    today = date.today().strftime("%Y-%m-%d")
    results = db_query(
        "SELECT * FROM exam_routine WHERE exam_date >= ? ORDER BY exam_date LIMIT 10",
        (today,)
    )
    if results:
        return _format_exam_results(results, "Upcoming Exams (Winter-2026)")
    return "❌ No upcoming exams found in the database."


def _format_exam_results(results: list, title: str):
    """Format exam results into a readable response."""
    lines = [f"📋 **{title}**\n"]
    current_sem = None
    for r in results:
        if r["semester"] != current_sem:
            current_sem = r["semester"]
            lines.append(f"\n**— Semester {current_sem} —**")
        # Format date nicely
        try:
            d = datetime.strptime(r["exam_date"], "%Y-%m-%d")
            date_str = d.strftime("%d %b %Y (%A)")
        except:
            date_str = r["exam_date"]

        lines.append(
            f"• **{r['course_name']}** ({r['course_code']})\n"
            f"  📅 {date_str}  🕐 {r['exam_time']}  🏫 Room: {r['room']}"
        )

    lines.append("\n\n💡 _Visit the Exam Routine page for full details and filters._")
    return "\n".join(lines)


def handle_admission():
    faqs = db_query("SELECT question, answer FROM admissions")
    uni = UGV_DATA["university"]
    text = (
        f"🎓 **Admission Info — {uni['name']}**\n\n"
    )
    for faq in faqs:
        text += f"**Q: {faq['question']}**\n{faq['answer']}\n\n"
    text += f"📧 Contact: {UGV_DATA['admission']['undergraduate']['contact']}"
    return text


def handle_teacher():
    teachers = db_query("SELECT * FROM teachers")
    if not teachers:
        return "👩‍🏫 Teacher data is being updated. Please contact the CSE department at cse@ugv.edu.bd."
    lines = ["👩‍🏫 **Faculty Members**\n"]
    for t in teachers:
        lines.append(
            f"• **{t['name']}** — {t['designation']}\n"
            f"  Dept: {t['department']} | 📧 {t['email']}\n"
            f"  Expertise: {t['expertise']}"
        )
    return "\n".join(lines)


def handle_department():
    depts = UGV_DATA["departments"]
    lines = ["🏫 **Departments at UGV**\n"]
    for d in depts:
        lines.append(
            f"• **{d['name']} ({d['code']})**\n"
            f"  Head: {d['head']} | 📧 {d['email']}\n"
            f"  {d['description']}"
        )
    return "\n".join(lines)


def handle_scholarship():
    scholarships = UGV_DATA["scholarships"]
    lines = ["🏆 **Scholarships at UGV**\n"]
    for s in scholarships:
        lines.append(f"• **{s['name']}**\n  Criteria: {s['criteria']}\n  Benefit: {s['benefit']}")
    return "\n".join(lines)


def handle_notice():
    notices = db_query("SELECT * FROM notices ORDER BY date DESC LIMIT 5")
    if not notices:
        return "📢 No notices available at the moment."
    lines = ["📢 **Latest Notices**\n"]
    for n in notices:
        lines.append(f"• **[{n['category']}] {n['title']}** ({n['date']})\n  {n['content']}")
    return "\n".join(lines)


def handle_contact():
    uni = UGV_DATA["university"]
    c = UGV_DATA["contact"]
    return (
        f"📞 **Contact UGV**\n\n"
        f"🌐 Website: {uni['website']}\n"
        f"📧 General: {uni['email']}\n"
        f"📱 Phone: {uni['phone']}\n"
        f"📍 Location: {uni['location']}\n\n"
        f"**Specific Contacts:**\n"
        f"• Registrar: {c['registrar']}\n"
        f"• Exam Controller: {c['exam_controller']}\n"
        f"• Library: {c['library']}"
    )


# ────────────────────────────────────────────────────────────────
#  AI FALLBACK
# ────────────────────────────────────────────────────────────────

def ai_response(user_message: str):
    """Send message to Gemini with UGV context."""
    if not AI_AVAILABLE:
        return (
            "🤖 I couldn't find specific information for your query in my database.\n"
            "Please contact UGV directly at info@ugv.edu.bd or visit ugv.edu.bd.\n\n"
            "You can also ask me about:\n"
            "• Exam routines (try: 'show semester 3 exams')\n"
            "• Admission info • Teachers • Scholarships • Notices"
        )

    context = f"""
You are the UGV Smart Assistant for the University of Global Village (UGV), Barishal, Bangladesh.
University info: {json.dumps(UGV_DATA, ensure_ascii=False)}
Answer only questions related to UGV. Be helpful, friendly, and concise.
If you don't know something specific, suggest contacting info@ugv.edu.bd.
Reply in the same language the user uses (English or Bengali).
"""
    try:
        response = model.generate_content(context + "\n\nUser: " + user_message)
        return response.text
    except Exception as e:
        return f"⚠️ AI service temporarily unavailable. Please try again or contact info@ugv.edu.bd.\n\nError: {str(e)}"


# ────────────────────────────────────────────────────────────────
#  MAIN ENTRY POINT
# ────────────────────────────────────────────────────────────────

def get_response(user_message: str) -> str:
    """Main function — detect intent and return appropriate response."""
    if not user_message or not user_message.strip():
        return "Please type a message! 😊"

    intent, entities = detect_intent(user_message)

    handlers = {
        "greeting":     handle_greeting,
        "exam_routine": lambda: handle_exam_routine(entities),
        "admission":    handle_admission,
        "teacher":      handle_teacher,
        "department":   handle_department,
        "scholarship":  handle_scholarship,
        "notice":       handle_notice,
        "contact":      handle_contact,
        "general":      lambda: ai_response(user_message),
    }

    handler = handlers.get(intent, lambda: ai_response(user_message))
    return handler()
