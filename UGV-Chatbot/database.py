"""
database.py — Creates and seeds the SQLite database for UGV Smart Assistant
Run this once: python database.py
"""

import sqlite3
import os

DB_PATH = "database.db"

def get_connection():
    """Return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Rows behave like dicts
    return conn

def create_tables():
    """Create all required tables."""
    conn = get_connection()
    c = conn.cursor()

    # ── Departments ──────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS departments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        code TEXT NOT NULL,
        head TEXT,
        email TEXT,
        description TEXT
    )""")

    # ── Teachers ─────────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        designation TEXT,
        department TEXT,
        email TEXT,
        phone TEXT,
        expertise TEXT
    )""")

    # ── Exam Routine ─────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS exam_routine (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        department TEXT NOT NULL,
        semester INTEGER NOT NULL,
        course_code TEXT NOT NULL,
        course_name TEXT NOT NULL,
        exam_date TEXT NOT NULL,
        exam_time TEXT NOT NULL,
        room TEXT DEFAULT 'TBA',
        program TEXT DEFAULT 'Regular'
    )""")

    # ── Notices ──────────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS notices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        date TEXT NOT NULL,
        category TEXT DEFAULT 'General'
    )""")

    # ── Admissions ───────────────────────────────────────────────
    c.execute("""
    CREATE TABLE IF NOT EXISTS admissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    )""")

    conn.commit()
    conn.close()
    print("✅ Tables created.")

def seed_exam_routines():
    """
    Seed exam routine data from the official Winter-2026 routines
    (data extracted from the scanned routine images).
    """
    conn = get_connection()
    c = conn.cursor()

    # Clear existing data to avoid duplicates on re-run
    c.execute("DELETE FROM exam_routine")

    routines = [
        # ── 1st Semester (Morning 09:30–12:30) ──────────────────
        ("CSE", 1, "0613-1103", "Structured Programming",            "2026-05-20", "09:30am-12:30pm", "TBA"),
        ("CSE", 1, "0611-1101", "Computer Fundamentals",             "2026-05-23", "09:30am-12:30pm", "TBA"),
        ("CSE", 1, "0222-1101", "History of the Emergence of Independent Bangladesh", "2026-06-08", "09:30am-12:30pm", "TBA"),
        ("CSE", 1, "0541-1101", "Differential and Integral Calculus","2026-06-10", "09:30am-12:30pm", "TBA"),
        ("CSE", 1, "0533-1101", "Physics I-Electricity, Magnetism & Property of Matter", "2026-06-13", "09:30am-12:30pm", "TBA"),
        ("CSE", 1, "0531-1101", "Chemistry",                         "2026-06-15", "09:30am-12:30pm", "TBA"),

        # ── 2nd Semester (Afternoon 02:30–05:30) ─────────────────
        ("CSE", 2, "0613-1205", "Data Structure",                    "2026-05-20", "02:30pm-05:30pm", "TBA"),
        ("CSE", 2, "0541-1201", "Ordinary & Partial Differential Equations", "2026-06-07", "02:30pm-05:30pm", "TBA"),
        ("CSE", 2, "0541-1203", "Discrete Mathematics",              "2026-06-09", "02:30pm-05:30pm", "TBA"),
        ("CSE", 2, "0533-1201", "Physics II-Optics, Modern Physics, Waves & Oscillation", "2026-06-14", "02:30pm-05:30pm", "TBA"),
        ("CSE", 2, "0713-1201", "Electrical Circuits",               "2026-06-16", "02:30pm-05:30pm", "TBA"),
        ("CSE", 2, "0231-1204", "English for Professional Purpose",   "2026-06-17", "02:30pm-05:30pm", "TBA"),

        # ── 3rd Semester (Morning 09:30–12:30) ───────────────────
        ("CSE", 3, "CSE 0613-2103", "Algorithm Design",              "2026-05-21", "09:30am-12:30pm", "TBA"),
        ("CSE", 3, "CSE 0613-2101", "Theory of Computation",         "2026-06-07", "09:30am-12:30pm", "TBA"),
        ("CSE", 3, "CSE 0611-2105", "Computer Architecture",         "2026-06-09", "09:30am-12:30pm", "TBA"),
        ("CSE", 3, "EEE 0714-2101", "Principles of Electronics",     "2026-06-11", "09:30am-12:30pm", "TBA"),
        ("CSE", 3, "MAT 0541-2101", "Fourier Analysis, Laplace Transform, Linear Algebra", "2026-06-14", "09:30am-12:30pm", "TBA"),

        # ── 4th Semester (Morning 09:30–12:30) ───────────────────
        ("CSE", 4, "CSE 0613-2203", "Object Oriented Programming",   "2026-05-20", "09:30am-12:30pm", "TBA"),
        ("CSE", 4, "CSE 0613-2209", "Web Programming",               "2026-05-23", "09:30am-12:30pm", "TBA"),
        ("CSE", 4, "CSE 0612-2207", "Database Management System",    "2026-06-08", "09:30am-12:30pm", "TBA"),
        ("CSE", 4, "CSE 0613-2201", "System Analysis & Design",      "2026-06-10", "09:30am-12:30pm", "TBA"),
        ("CSE", 4, "CAN 0411-2201", "Accounting",                    "2026-06-13", "09:30am-12:30pm", "TBA"),
        ("CSE", 4, "MAT 0541-2201", "Complex Variable, Vector Analysis & Coordinate Geometry", "2026-06-15", "09:30am-12:30pm", "TBA"),
        ("CSE", 4, "CSE 0541-2205", "Numerical Methods",             "2026-06-17", "09:30am-12:30pm", "TBA"),

        # ── 5th Semester (Afternoon 02:30–05:30) ─────────────────
        ("CSE", 5, "CSE 0613-3103", "Compiler Design",               "2026-05-20", "02:30pm-05:30pm", "TBA"),
        ("CSE", 5, "CSE 0613-3101", "Microprocessors & Microcontrollers", "2026-06-07", "02:30pm-05:30pm", "TBA"),
        ("CSE", 5, "CSE 0613-3105", "Operating Systems",             "2026-06-09", "02:30pm-05:30pm", "TBA"),
        ("CSE", 5, "CSE 0613-3107", "Software Engineering & Project Management", "2026-06-14", "02:30pm-05:30pm", "TBA"),
        ("CSE", 5, "MAT 0541-3101", "Applied Statistics & Queuing Theory", "2026-06-16", "02:30pm-05:30pm", "TBA"),
        ("CSE", 5, "ECO 0311-3101", "Economics",                     "2026-06-17", "02:30pm-05:30pm", "TBA"),

        # ── 6th Semester (Morning 09:30–12:30) ───────────────────
        ("CSE", 6, "CSE-0612-3203", "Computer Networks and Security","2026-05-21", "09:30am-12:30pm", "TBA"),
        ("CSE", 6, "CSE 0714-3201", "Embedded Systems and Internet of Things", "2026-06-07", "09:30am-12:30pm", "TBA"),
        ("CSE", 6, "CSE 0613-3205", "Machine Learning",              "2026-06-09", "09:30am-12:30pm", "TBA"),
        ("CSE", 6, "CSE 0613-3207", "Computer Graphics and Image Processing", "2026-06-11", "09:30am-12:30pm", "TBA"),
        ("CSE", 6, "CSE 0613-3209", "Technical Writing and Research Methodology", "2026-06-14", "09:30am-12:30pm", "TBA"),
        ("CSE", 6, "HUM 0521-3201", "Environment and Disaster Management", "2026-06-16", "09:30am-12:30pm", "TBA"),

        # ── 7th Semester (Morning 09:30–12:30) ───────────────────
        ("CSE", 7, "CSE 0613-4101", "Pattern Recognition",           "2026-05-20", "09:30am-12:30pm", "TBA"),
        ("CSE", 7, "CSE 0613-4107", "Digital Signal Processing",     "2026-05-23", "09:30am-12:30pm", "TBA"),
        ("CSE", 7, "BDS 0321-4101", "Bangladesh Studies",            "2026-06-08", "09:30am-12:30pm", "TBA"),
        ("CSE", 7, "CSE 0613-4211", "Computer Vision",               "2026-06-10", "09:30am-12:30pm", "TBA"),
        ("CSE", 7, "CSE 0613-4135", "Data Mining",                   "2026-06-13", "09:30am-12:30pm", "TBA"),

        # ── 8th Semester (Afternoon 02:30–05:30) ─────────────────
        ("CSE", 8, "CSE-409",       "Pattern Recognition",           "2026-05-20", "02:30pm-05:30pm", "TBA"),
        ("CSE", 8, "CSE-506",       "Unix Programming",              "2026-06-07", "02:30pm-05:30pm", "TBA"),
        ("CSE", 8, "CSE-508",       "Fault Tolerant System",         "2026-06-09", "02:30pm-05:30pm", "TBA"),
        ("CSE", 8, "CSE-509",       "Digital Pulse Technique",       "2026-06-14", "02:30pm-05:30pm", "TBA"),
    ]

    c.executemany("""
        INSERT INTO exam_routine
        (department, semester, course_code, course_name, exam_date, exam_time, room)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, routines)

    conn.commit()
    conn.close()
    print(f"✅ Seeded {len(routines)} exam routine records.")

def seed_teachers():
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM teachers")

    teachers = [
        ("Md. Riadul Islam", "Head & Assistant Professor", "CSE", "riadul@ugv.edu.bd", "N/A", "Machine Learning, Algorithms"),
        ("TBA", "Lecturer", "CSE", "cse@ugv.edu.bd", "N/A", "Programming, Networks"),
    ]
    c.executemany("INSERT INTO teachers (name, designation, department, email, phone, expertise) VALUES (?,?,?,?,?,?)", teachers)
    conn.commit()
    conn.close()
    print("✅ Teachers seeded.")

def seed_admissions():
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM admissions")

    faqs = [
        ("What are the admission requirements?", "You need HSC or equivalent with minimum GPA 2.5 in both SSC and HSC."),
        ("How do I apply?", "Apply online at ugv.edu.bd, then appear for a written test and viva."),
        ("What is the application fee?", "The application fee is BDT 5,000."),
        ("When does admission start?", "UGV has two sessions: Summer (January) and Winter (July)."),
        ("What documents are required?", "SSC & HSC certificates, NID/Birth certificate, 4 photos, and a character certificate."),
        ("Is there any scholarship?", "Yes! Merit scholarship (50% waiver for CGPA 3.75+), Freedom Fighter quota (full waiver), and Sibling discount (10% per sibling)."),
        ("What departments are available?", "CSE, BBA, English, and more. Visit ugv.edu.bd for the full list."),
    ]
    c.executemany("INSERT INTO admissions (question, answer) VALUES (?,?)", faqs)
    conn.commit()
    conn.close()
    print("✅ Admission FAQs seeded.")

def seed_notices():
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM notices")

    notices = [
        ("Final Exam Winter-2026 Routine Published", "The final examination routine for Winter-2026 has been published for all CSE semesters. Please check the notice board.", "2026-04-26", "Exam"),
        ("Admission Open - Summer 2026", "Applications are now open for Summer 2026 semester. Apply before the deadline.", "2026-05-01", "Admission"),
        ("Library Closed on Eid Holiday", "The university library will remain closed during the Eid vacation.", "2026-05-10", "General"),
    ]
    c.executemany("INSERT INTO notices (title, content, date, category) VALUES (?,?,?,?)", notices)
    conn.commit()
    conn.close()
    print("✅ Notices seeded.")

if __name__ == "__main__":
    print("🚀 Setting up UGV Smart Assistant database...")
    create_tables()
    seed_exam_routines()
    seed_teachers()
    seed_admissions()
    seed_notices()
    print("\n🎉 Database ready! Run: python app.py")
