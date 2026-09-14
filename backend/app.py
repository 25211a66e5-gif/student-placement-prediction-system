from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import get_connection
from auth import hash_password, verify_password
from assessment_api import register_assessment_routes
from career_analysis_api import register_career_analysis_routes
from resume_analysis_api import register_resume_routes
from technical_interview_api import register_technical_interview_routes
from account_api import register_account_routes
from admin_api import register_admin_routes
from question_admin_api import register_question_admin_routes
from user_admin_api import register_user_admin_routes

from pathlib import Path

import subprocess
import base64
import json
import random

app = Flask(__name__)
CORS(app)

register_assessment_routes(app)
register_career_analysis_routes(app)
register_resume_routes(app)
register_technical_interview_routes(app)
register_account_routes(app)
register_admin_routes(app)
register_question_admin_routes(app)
register_user_admin_routes(app)


# ============================================================
# FRONTEND SERVING
# ============================================================

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
PAGES_DIR = FRONTEND_DIR / "pages"
ASSETS_DIR = FRONTEND_DIR / "assets"
CSS_DIR = FRONTEND_DIR / "css"
JS_DIR = FRONTEND_DIR / "js"


@app.route("/")
def frontend_home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/index.html")
def frontend_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/pages/<path:filename>")
def frontend_page(filename):
    return send_from_directory(PAGES_DIR, filename)


@app.route("/assets/<path:filename>")
def frontend_asset(filename):
    return send_from_directory(ASSETS_DIR, filename)


@app.route("/css/<path:filename>")
def frontend_css(filename):
    return send_from_directory(CSS_DIR, filename)


@app.route("/js/<path:filename>")
def frontend_js(filename):
    return send_from_directory(JS_DIR, filename)



TIMEOUT_SECONDS = 5
MAX_CODE_CHARS = 20000


# ============================================================
# CODING LANGUAGE CONFIGURATION
# ============================================================

LANGUAGE_CONFIG = {
    "Python": {
        "image": "python:3.12-alpine",
        "filename": "Main.py",
    },
    "Java": {
        "image": "eclipse-temurin:21-jdk-alpine",
        "filename": "Main.java",
    },
    "C++": {
        "image": "gcc:14",
        "filename": "Main.cpp",
    },
    "C": {
        "image": "gcc:14",
        "filename": "Main.c",
    },
    "JavaScript": {
        "image": "node:22-alpine",
        "filename": "Main.js",
    },
}


# ============================================================
# CODING TEST CASES
# ============================================================

TESTS = [
    {
        "input": "4\n4 9 2 7\n",
        "expected": "9"
    },
    {
        "input": "4\n-5 -2 -11 -1\n",
        "expected": "-1"
    },
    {
        "input": "3\n100 25 75\n",
        "expected": "100"
    },
    {
        "input": "1\n8\n",
        "expected": "8"
    }
]


# ============================================================
# DOCKER CODE EXECUTION
# ============================================================

def docker_run(language, code, stdin_data):

    config = LANGUAGE_CONFIG[language]

    code64 = base64.b64encode(code.encode()).decode()
    input64 = base64.b64encode(stdin_data.encode()).decode()

    filename = config["filename"]

    if language == "Python":

        runner = (
            f"cd /workspace && "
            f"echo {code64} | base64 -d > {filename} && "
            f"echo {input64} | base64 -d > /tmp/input.txt && "
            f"timeout 4s python {filename} < /tmp/input.txt"
        )

    elif language == "Java":

        runner = (
            f"cd /workspace && "
            f"echo {code64} | base64 -d > {filename} && "
            f"echo {input64} | base64 -d > /tmp/input.txt && "
            f"javac {filename} && "
            f"timeout 4s java Main < /tmp/input.txt"
        )

    elif language == "C++":

        runner = (
            f"cd /workspace && "
            f"echo {code64} | base64 -d > {filename} && "
            f"echo {input64} | base64 -d > /tmp/input.txt && "
            f"g++ {filename} -O2 -std=c++17 -o Main && "
            f"timeout 4s ./Main < /tmp/input.txt"
        )

    elif language == "C":

        runner = (
            f"cd /workspace && "
            f"echo {code64} | base64 -d > {filename} && "
            f"echo {input64} | base64 -d > /tmp/input.txt && "
            f"gcc {filename} -O2 -std=c11 -o Main && "
            f"timeout 4s ./Main < /tmp/input.txt"
        )

    else:

        runner = (
            f"cd /workspace && "
            f"echo {code64} | base64 -d > {filename} && "
            f"echo {input64} | base64 -d > /tmp/input.txt && "
            f"timeout 4s node {filename} < /tmp/input.txt"
        )

    cmd = [
        "docker",
        "run",
        "--rm",
        "-i",

        "--network",
        "none",

        "--memory",
        "128m",

        "--cpus",
        "0.5",

        "--pids-limit",
        "64",

        "--read-only",

        "--tmpfs",
        "/tmp:rw,nosuid,size=64m",

        "--tmpfs",
        "/workspace:rw,nosuid,size=64m",

        config["image"],

        "sh",
        "-c",
        runner
    ]

    try:

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS + 3
        )

        return (
            result.returncode,
            result.stdout.strip(),
            result.stderr.strip()
        )

    except FileNotFoundError:

        return (
            -999,
            "",
            "Docker is not installed or is not available in PATH."
        )

    except subprocess.TimeoutExpired:

        return (
            -998,
            "",
            "Execution timed out."
        )


# ============================================================
# REGISTER
# ============================================================

@app.post("/api/register")
def register():

    data = request.get_json(silent=True) or {}

    first_name = str(data.get("first_name", "")).strip()
    last_name = str(data.get("last_name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    phone = str(data.get("phone", "")).strip()
    college = str(data.get("college", "")).strip()
    password = str(data.get("password", ""))

    if not first_name:
        return jsonify({
            "error": "First name is required."
        }), 400

    if not last_name:
        return jsonify({
            "error": "Last name is required."
        }), 400

    if not email:
        return jsonify({
            "error": "Email is required."
        }), 400

    if "@" not in email or "." not in email:

        return jsonify({
            "error": "Please enter a valid email address."
        }), 400

    if not phone:
        return jsonify({
            "error": "Phone number is required."
        }), 400

    if not college:
        return jsonify({
            "error": "College or university is required."
        }), 400

    if len(password) < 8:

        return jsonify({
            "error": "Password must contain at least 8 characters."
        }), 400

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:

            return jsonify({
                "error": "An account with this email already exists."
            }), 409

        password_hash = hash_password(password)

        cursor.execute(
            """
            INSERT INTO users
            (
                first_name,
                last_name,
                email,
                phone,
                college,
                password_hash,
                role
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                first_name,
                last_name,
                email,
                phone,
                college,
                password_hash,
                "student"
            )
        )

        connection.commit()

        user_id = cursor.lastrowid

        return jsonify({

            "message": "Student account created successfully.",

            "user": {
                "id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "role": "student"
            }

        }), 201

    except Exception as error:

        connection.rollback()

        return jsonify({
            "error": "Registration failed.",
            "message": str(error)
        }), 500

    finally:

        connection.close()


# ============================================================
# LOGIN
# ============================================================

@app.post("/api/login")
def login():

    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not email:

        return jsonify({
            "error": "Email is required."
        }), 400

    if not password:

        return jsonify({
            "error": "Password is required."
        }), 400

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                first_name,
                last_name,
                email,
                phone,
                college,
                password_hash,
                role
            FROM users
            WHERE email = ?
            """,
            (email,)
        )

        user = cursor.fetchone()

        if user is None:

            return jsonify({
                "error": "Invalid email or password."
            }), 401

        if not verify_password(
            password,
            user["password_hash"]
        ):

            return jsonify({
                "error": "Invalid email or password."
            }), 401

        return jsonify({

            "message": "Login successful.",

            "user": {
                "id": user["id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "phone": user["phone"],
                "college": user["college"],
                "role": user["role"]
            }

        }), 200

    except Exception as error:

        return jsonify({
            "error": "Login failed.",
            "message": str(error)
        }), 500

    finally:

        connection.close()


# ============================================================
# SAVE / UPDATE STUDENT PROFILE
# ============================================================

@app.post("/api/profile")
def save_profile():

    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")

    # --------------------------------------------------------
    # USER ID
    # --------------------------------------------------------

    if not user_id:

        return jsonify({
            "error": "User ID is required."
        }), 400

    # --------------------------------------------------------
    # REQUIRED PROFILE FIELDS
    # --------------------------------------------------------

    tenth_percentage = data.get("tenth_percentage")
    twelfth_percentage = data.get("twelfth_percentage")
    cgpa = data.get("cgpa")
    graduation_year = data.get("graduation_year")
    backlogs = data.get("backlogs")

    branch = str(
        data.get("branch", "")
    ).strip()

    target_job_role = str(
        data.get("target_job_role", "")
    ).strip()

    technical_skills = str(
        data.get("technical_skills", "")
    ).strip()

    # --------------------------------------------------------
    # OPTIONAL PROFILE FIELDS
    # --------------------------------------------------------

    certifications = str(
        data.get("certifications", "")
    ).strip()

    projects = str(
        data.get("projects", "")
    ).strip()

    internships = str(
        data.get("internships", "")
    ).strip()

    github_url = str(
        data.get("github_url", "")
    ).strip()

    linkedin_url = str(
        data.get("linkedin_url", "")
    ).strip()

    portfolio_url = str(
        data.get("portfolio_url", "")
    ).strip()

    resume_url = str(
        data.get("resume_url", "")
    ).strip()

    # ========================================================
    # REQUIRED FIELD VALIDATION
    # ========================================================

    if tenth_percentage is None or str(tenth_percentage).strip() == "":
        return jsonify({
            "error": "10th percentage is required."
        }), 400

    if twelfth_percentage is None or str(twelfth_percentage).strip() == "":
        return jsonify({
            "error": "12th percentage is required."
        }), 400

    if cgpa is None or str(cgpa).strip() == "":
        return jsonify({
            "error": "B.Tech/B.E. CGPA is required."
        }), 400

    if graduation_year is None or str(graduation_year).strip() == "":
        return jsonify({
            "error": "Graduation year is required."
        }), 400

    if backlogs is None or str(backlogs).strip() == "":
        return jsonify({
            "error": "Current backlogs is required."
        }), 400

    if not branch:

        return jsonify({
            "error": "Engineering branch is required."
        }), 400

    if not target_job_role:

        return jsonify({
            "error": "Target job role is required."
        }), 400

    if not technical_skills:

        return jsonify({
            "error": "At least one technical skill is required."
        }), 400

    # ========================================================
    # NUMERIC VALIDATION
    # ========================================================

    try:

        tenth_percentage = float(
            tenth_percentage
        )

        twelfth_percentage = float(
            twelfth_percentage
        )

        cgpa = float(cgpa)

        graduation_year = int(
            graduation_year
        )

        backlogs = int(backlogs)

    except (ValueError, TypeError):

        return jsonify({
            "error": "Please enter valid academic values."
        }), 400

    # ========================================================
    # RANGE VALIDATION
    # ========================================================

    if tenth_percentage < 0 or tenth_percentage > 100:

        return jsonify({
            "error": "10th percentage must be between 0 and 100."
        }), 400

    if twelfth_percentage < 0 or twelfth_percentage > 100:

        return jsonify({
            "error": "12th percentage must be between 0 and 100."
        }), 400

    if cgpa < 0 or cgpa > 10:

        return jsonify({
            "error": "CGPA must be between 0 and 10."
        }), 400

    if backlogs < 0:

        return jsonify({
            "error": "Backlogs cannot be negative."
        }), 400

    # Graduation year validation
    if graduation_year < 2000 or graduation_year > 2100:

        return jsonify({
            "error": "Please enter a valid graduation year."
        }), 400

    # ========================================================
    # DATABASE
    # ========================================================

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            "SELECT id FROM users WHERE id = ?",
            (user_id,)
        )

        user = cursor.fetchone()

        if user is None:

            return jsonify({
                "error": "Student account not found."
            }), 404

        cursor.execute(
            """
            SELECT id
            FROM student_profiles
            WHERE user_id = ?
            """,
            (user_id,)
        )

        existing_profile = cursor.fetchone()

        # ----------------------------------------------------
        # UPDATE EXISTING PROFILE
        # ----------------------------------------------------

        if existing_profile:

            cursor.execute(
                """
                UPDATE student_profiles
                SET
                    tenth_percentage = ?,
                    twelfth_percentage = ?,
                    cgpa = ?,
                    graduation_year = ?,
                    backlogs = ?,
                    branch = ?,
                    target_job_role = ?,
                    technical_skills = ?,
                    certifications = ?,
                    projects = ?,
                    internships = ?,
                    github_url = ?,
                    linkedin_url = ?,
                    portfolio_url = ?,
                    resume_url = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
                """,
                (
                    tenth_percentage,
                    twelfth_percentage,
                    cgpa,
                    graduation_year,
                    backlogs,
                    branch,
                    target_job_role,
                    technical_skills,
                    certifications,
                    projects,
                    internships,
                    github_url,
                    linkedin_url,
                    portfolio_url,
                    resume_url,
                    user_id
                )
            )

            message = (
                "Student profile updated successfully."
            )

        # ----------------------------------------------------
        # CREATE NEW PROFILE
        # ----------------------------------------------------

        else:

            cursor.execute(
                """
                INSERT INTO student_profiles
                (
                    user_id,
                    tenth_percentage,
                    twelfth_percentage,
                    cgpa,
                    graduation_year,
                    backlogs,
                    branch,
                    target_job_role,
                    technical_skills,
                    certifications,
                    projects,
                    internships,
                    github_url,
                    linkedin_url,
                    portfolio_url,
                    resume_url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    tenth_percentage,
                    twelfth_percentage,
                    cgpa,
                    graduation_year,
                    backlogs,
                    branch,
                    target_job_role,
                    technical_skills,
                    certifications,
                    projects,
                    internships,
                    github_url,
                    linkedin_url,
                    portfolio_url,
                    resume_url
                )
            )

            message = (
                "Student profile created successfully."
            )

        connection.commit()

        return jsonify({

            "message": message,

            "profile": {
                "user_id": user_id,
                "branch": branch,
                "target_job_role": target_job_role
            }

        }), 200

    except Exception as error:

        connection.rollback()

        return jsonify({
            "error": "Unable to save profile.",
            "message": str(error)
        }), 500

    finally:

        connection.close()


# ============================================================
# GET STUDENT PROFILE
# ============================================================

@app.get("/api/profile/<int:user_id>")
def get_profile(user_id):

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                id,
                user_id,
                tenth_percentage,
                twelfth_percentage,
                cgpa,
                graduation_year,
                backlogs,
                branch,
                target_job_role,
                technical_skills,
                certifications,
                projects,
                internships,
                github_url,
                linkedin_url,
                portfolio_url,
                resume_url
            FROM student_profiles
            WHERE user_id = ?
            """,
            (user_id,)
        )

        profile = cursor.fetchone()

        if profile is None:

            return jsonify({
                "error": "Profile not found."
            }), 404

        return jsonify({
            "profile": dict(profile)
        }), 200

    except Exception as error:

        return jsonify({
            "error": "Unable to retrieve profile.",
            "message": str(error)
        }), 500

    finally:

        connection.close()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/api/health")
def health():

    return jsonify({
        "status": "ok",
        "service": "Student Placement Prediction coding engine"
    })



# ============================================================
# RANDOMIZED CODING ASSESSMENT
# ============================================================

def public_coding_question(row):
    """Return only question data that is safe to expose to the student."""
    return {
        "id": row["id"],
        "title": row["title"],
        "topic": row["topic"],
        "difficulty": row["difficulty"],
        "description": row["description"],
        "input_format": row["input_format"],
        "output_format": row["output_format"],
        "sample_input": row["sample_input"],
        "sample_output": row["sample_output"],
    }


def ensure_coding_tables(connection):
    """Create coding tables if an older database.py has not done so yet."""
    connection.execute("""
        CREATE TABLE IF NOT EXISTS coding_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            topic TEXT NOT NULL,
            difficulty TEXT NOT NULL DEFAULT 'Easy',
            description TEXT NOT NULL,
            input_format TEXT,
            output_format TEXT,
            sample_input TEXT,
            sample_output TEXT,
            hidden_tests TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS coding_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL UNIQUE,
            user_id INTEGER NOT NULL,
            coding_question_id INTEGER NOT NULL,
            language TEXT,
            submitted INTEGER NOT NULL DEFAULT 0,
            score REAL NOT NULL DEFAULT 0,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            submitted_at TIMESTAMP,
            FOREIGN KEY (assessment_id)
                REFERENCES assessments(id)
                ON DELETE CASCADE,
            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,
            FOREIGN KEY (coding_question_id)
                REFERENCES coding_questions(id)
                ON DELETE CASCADE
        )
    """)


def get_or_create_coding_attempt(connection, assessment_id, user_id):
    """
    Get the coding question assigned to this assessment.
    If none exists, assign one random active question.

    A student will not receive a question already used in a previous
    coding assessment, unless all active questions have already been used.
    """
    ensure_coding_tables(connection)
    cursor = connection.cursor()

    # 1. Reuse the question already assigned to this assessment.
    cursor.execute("""
        SELECT
            ca.*,
            cq.title,
            cq.topic,
            cq.difficulty,
            cq.description,
            cq.input_format,
            cq.output_format,
            cq.sample_input,
            cq.sample_output,
            cq.hidden_tests
        FROM coding_attempts ca
        JOIN coding_questions cq
            ON cq.id = ca.coding_question_id
        WHERE ca.assessment_id = ?
          AND ca.user_id = ?
        LIMIT 1
    """, (assessment_id, user_id))

    attempt = cursor.fetchone()
    if attempt:
        return attempt

    # 2. Count active questions directly from the same connection.
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM coding_questions
        WHERE is_active = 1
    """)
    active_count = int(cursor.fetchone()["total"])

    if active_count == 0:
        return None

    # 3. Prefer an active question this student has NOT seen before.
    cursor.execute("""
        SELECT id
        FROM coding_questions
        WHERE is_active = 1
          AND id NOT IN (
              SELECT coding_question_id
              FROM coding_attempts
              WHERE user_id = ?
          )
        ORDER BY RANDOM()
        LIMIT 1
    """, (user_id,))

    question = cursor.fetchone()

    # 4. If the student has seen every active question, start a new
    # randomized cycle.
    if question is None:
        cursor.execute("""
            SELECT id
            FROM coding_questions
            WHERE is_active = 1
            ORDER BY RANDOM()
            LIMIT 1
        """)
        question = cursor.fetchone()

    if question is None:
        return None

    # 5. Assign the selected question to this assessment.
    try:
        cursor.execute("""
            INSERT INTO coding_attempts
            (
                assessment_id,
                user_id,
                coding_question_id
            )
            VALUES (?, ?, ?)
        """, (
            assessment_id,
            user_id,
            question["id"]
        ))
        connection.commit()

    except Exception:
        connection.rollback()

        # Another request may have assigned the question at the same time.
        cursor.execute("""
            SELECT
                ca.*,
                cq.title,
                cq.topic,
                cq.difficulty,
                cq.description,
                cq.input_format,
                cq.output_format,
                cq.sample_input,
                cq.sample_output,
                cq.hidden_tests
            FROM coding_attempts ca
            JOIN coding_questions cq
                ON cq.id = ca.coding_question_id
            WHERE ca.assessment_id = ?
              AND ca.user_id = ?
            LIMIT 1
        """, (assessment_id, user_id))

        attempt = cursor.fetchone()
        if attempt:
            return attempt

        raise

    # 6. Return the complete assigned question.
    cursor.execute("""
        SELECT
            ca.*,
            cq.title,
            cq.topic,
            cq.difficulty,
            cq.description,
            cq.input_format,
            cq.output_format,
            cq.sample_input,
            cq.sample_output,
            cq.hidden_tests
        FROM coding_attempts ca
        JOIN coding_questions cq
            ON cq.id = ca.coding_question_id
        WHERE ca.assessment_id = ?
          AND ca.user_id = ?
        LIMIT 1
    """, (assessment_id, user_id))

    return cursor.fetchone()


@app.get("/api/coding/question")
def get_coding_question():

    assessment_id = request.args.get("assessment_id", type=int)
    user_id = request.args.get("user_id", type=int)

    if not assessment_id or not user_id:
        return jsonify({
            "error": "assessment_id and user_id are required."
        }), 400

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, user_id, status
            FROM assessments
            WHERE id = ?
        """, (assessment_id,))

        assessment = cursor.fetchone()

        if assessment is None:
            return jsonify({
                "error": "Assessment not found."
            }), 404

        if assessment["user_id"] != user_id:
            return jsonify({
                "error": "You do not have access to this assessment."
            }), 403

        if assessment["status"] != "completed":
            return jsonify({
                "error": "Complete the MCQ assessment before taking the coding test."
            }), 400

        attempt = get_or_create_coding_attempt(
            connection,
            assessment_id,
            user_id
        )

        if attempt is None:
            return jsonify({
                "error": "No active coding questions are available."
            }), 404

        return jsonify({
            "assessment_id": assessment_id,
            "submitted": bool(attempt["submitted"]),
            "language": attempt["language"],
            "question": public_coding_question(attempt)
        }), 200

    except Exception as error:
        return jsonify({
            "error": "Unable to load coding question.",
            "message": str(error)
        }), 500

    finally:
        connection.close()


@app.post("/api/coding/submit")
def submit_coding_solution():

    data = request.get_json(silent=True) or {}

    assessment_id = data.get("assessment_id")
    user_id = data.get("user_id")
    language = str(data.get("language", "")).strip()

    # The frontend uses lowercase language IDs (python, java, c, c++, javascript).
    # Normalize them to the backend language names used by LANGUAGE_CONFIG.
    language_map = {
        "python": "Python",
        "java": "Java",
        "c++": "C++",
        "c": "C",
        "javascript": "JavaScript"
    }

    language = language_map.get(
        language.lower(),
        language
    )

    code = str(data.get("code", ""))

    if not assessment_id or not user_id:
        return jsonify({
            "error": "assessment_id and user_id are required."
        }), 400

    if language not in LANGUAGE_CONFIG:
        return jsonify({
            "error": "Unsupported language."
        }), 400

    if not code.strip():
        return jsonify({
            "error": "Code cannot be empty."
        }), 400

    if len(code) > MAX_CODE_CHARS:
        return jsonify({
            "error": "Code is too long."
        }), 400

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, user_id, status
            FROM assessments
            WHERE id = ?
        """, (assessment_id,))

        assessment = cursor.fetchone()

        if assessment is None:
            return jsonify({
                "error": "Assessment not found."
            }), 404

        if assessment["user_id"] != user_id:
            return jsonify({
                "error": "You do not have access to this assessment."
            }), 403

        if assessment["status"] != "completed":
            return jsonify({
                "error": "Complete the MCQ assessment before submitting the coding test."
            }), 400

        attempt = get_or_create_coding_attempt(
            connection,
            assessment_id,
            user_id
        )

        if attempt is None:
            return jsonify({
                "error": "Coding question not available."
            }), 404

        if attempt["submitted"]:
            return jsonify({
                "error": "Coding solution has already been submitted."
            }), 409

        hidden_tests = json.loads(attempt["hidden_tests"])

        results = []
        passed = 0

        for index, test in enumerate(hidden_tests, 1):

            rc, output, error = docker_run(
                language,
                code,
                test["input"]
            )

            if rc == -999:
                return jsonify({
                    "error": "Coding engine unavailable.",
                    "message": error
                }), 503

            if rc == -998:
                results.append({
                    "test": index,
                    "passed": False,
                    "message": "Time limit exceeded."
                })
                continue

            ok = (
                rc == 0
                and output.strip() == str(test["expected"]).strip()
            )

            if ok:
                passed += 1

            # Do NOT expose hidden expected output.
            results.append({
                "test": index,
                "passed": ok,
                "received": output.strip(),
                "error": error if rc != 0 else ""
            })

        total = len(hidden_tests)
        score = round((passed / total) * 100) if total else 0

        cursor.execute("""
            UPDATE coding_attempts
            SET
                language = ?,
                submitted = 1,
                score = ?,
                submitted_at = CURRENT_TIMESTAMP
            WHERE assessment_id = ?
              AND user_id = ?
        """, (
            language,
            score,
            assessment_id,
            user_id
        ))

        # Coding score is incorporated into the existing result record.
        cursor.execute("""
            SELECT
                technical_score,
                aptitude_score,
                logical_score,
                communication_score,
                coding_concepts_score
            FROM assessment_results
            WHERE assessment_id = ?
        """, (assessment_id,))

        result_row = cursor.fetchone()

        overall_score = None
        readiness_score = None

        if result_row:
            from ml.readiness_model import calculate_readiness_score

            readiness_score = calculate_readiness_score(
                technical_score=result_row["technical_score"],
                aptitude_score=result_row["aptitude_score"],
                logical_score=result_row["logical_score"],
                communication_score=result_row["communication_score"],
                coding_concepts_score=result_row["coding_concepts_score"],
                coding_test_score=score
            )

            section_values = [
                result_row["technical_score"],
                result_row["aptitude_score"],
                result_row["logical_score"],
                result_row["communication_score"],
                result_row["coding_concepts_score"],
                score
            ]

            overall_score = round(
                sum(section_values) / len(section_values),
                2
            )

            cursor.execute("""
                UPDATE assessment_results
                SET
                    coding_test_score = ?,
                    overall_score = ?,
                    readiness_score = ?
                WHERE assessment_id = ?
            """, (
                score,
                overall_score,
                readiness_score,
                assessment_id
            ))

            cursor.execute("""
                UPDATE assessments
                SET score = ?
                WHERE id = ?
            """, (
                overall_score,
                assessment_id
            ))

        connection.commit()

        return jsonify({
            "message": "Coding solution submitted successfully.",
            "score": score,
            "passed": passed,
            "total": total,
            "overall_score": overall_score,
            "readiness_score": readiness_score,
            "results": results
        }), 200

    except json.JSONDecodeError:
        connection.rollback()
        return jsonify({
            "error": "Coding question test data is invalid."
        }), 500

    except Exception as error:
        connection.rollback()
        return jsonify({
            "error": "Unable to submit coding solution.",
            "message": str(error)
        }), 500

    finally:
        connection.close()



# ============================================================
# RUN CODE
# ============================================================

@app.post("/api/run")
def run_code():

    data = request.get_json(silent=True) or {}

    language = str(
        data.get("language", "")
    ).strip()

    language_map = {
        "python": "Python",
        "java": "Java",
        "c++": "C++",
        "c": "C",
        "javascript": "JavaScript"
    }

    language = language_map.get(
        language.lower(),
        language
    )

    code = data.get("code", "")
    assessment_id = data.get("assessment_id")
    user_id = data.get("user_id")

    if language not in LANGUAGE_CONFIG:
        return jsonify({
            "error": "Unsupported language."
        }), 400

    if not code.strip():
        return jsonify({
            "error": "Code cannot be empty."
        }), 400

    if len(code) > MAX_CODE_CHARS:
        return jsonify({
            "error": "Code is too long."
        }), 400

    # For an assessment coding test, Run Sample executes ONLY
    # the assigned question's public sample. Hidden tests remain
    # server-side and are evaluated only on final submission.
    if assessment_id:
        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    ca.assessment_id,
                    ca.user_id,
                    cq.sample_input,
                    cq.sample_output
                FROM coding_attempts ca
                JOIN coding_questions cq
                    ON cq.id = ca.coding_question_id
                WHERE ca.assessment_id = ?
            """, (assessment_id,))

            coding_attempt = cursor.fetchone()

            if coding_attempt is None:
                return jsonify({
                    "error": "Coding question is not assigned to this assessment."
                }), 404

            if user_id is not None and int(coding_attempt["user_id"]) != int(user_id):
                return jsonify({
                    "error": "You do not have access to this coding assessment."
                }), 403

            sample_input = coding_attempt["sample_input"] or ""
            expected = coding_attempt["sample_output"] or ""

        finally:
            connection.close()

        rc, output, error = docker_run(
            language,
            code,
            sample_input
        )

        if rc == -999:
            return jsonify({
                "error": "Coding engine unavailable.",
                "message": error,
                "setup": (
                    "Install Docker Desktop, "
                    "then run the backend again."
                )
            }), 503

        if rc == -998:
            return jsonify({
                "passed": 0,
                "total": 1,
                "score": 0,
                "results": [{
                    "test": 1,
                    "passed": False,
                    "message": "Time limit exceeded."
                }]
            }), 200

        normalized = output.strip()
        expected_normalized = str(expected).strip()
        ok = rc == 0 and normalized == expected_normalized

        return jsonify({
            "passed": 1 if ok else 0,
            "total": 1,
            "score": 100 if ok else 0,
            "results": [{
                "test": 1,
                "passed": ok,
                "received": normalized,
                "error": error if rc != 0 else ""
            }]
        }), 200

    # Backward-compatible fallback when /api/run is used without
    # an assessment ID.
    results = []
    passed = 0

    for i, test in enumerate(TESTS, 1):

        rc, output, error = docker_run(
            language,
            code,
            test["input"]
        )

        if rc == -999:
            return jsonify({
                "error": "Coding engine unavailable.",
                "message": error,
                "setup": (
                    "Install Docker Desktop, "
                    "then run the backend again."
                )
            }), 503

        if rc == -998:
            results.append({
                "test": i,
                "passed": False,
                "message": "Time limit exceeded."
            })
            continue

        normalized = output.strip()

        ok = (
            rc == 0
            and normalized == test["expected"]
        )

        if ok:
            passed += 1

        results.append({
            "test": i,
            "passed": ok,
            "expected": test["expected"],
            "received": normalized,
            "error": error if rc != 0 else ""
        })

    score = round(
        passed / len(TESTS) * 100
    )

    return jsonify({
        "passed": passed,
        "total": len(TESTS),
        "score": score,
        "results": results
    })


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )