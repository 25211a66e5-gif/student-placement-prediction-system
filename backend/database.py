import sqlite3
from pathlib import Path


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATABASE = DATA_DIR / "careerpredict.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    # Enable foreign-key support
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_database():

    connection = get_connection()
    cursor = connection.cursor()


    # ========================================================
    # USERS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            first_name TEXT NOT NULL,

            last_name TEXT NOT NULL,

            email TEXT NOT NULL UNIQUE,

            phone TEXT NOT NULL,

            college TEXT NOT NULL,

            password_hash TEXT NOT NULL,

            role TEXT NOT NULL DEFAULT 'student',

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # ========================================================
    # STUDENT PROFILES
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_profiles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL UNIQUE,

            tenth_percentage REAL NOT NULL,

            twelfth_percentage REAL NOT NULL,

            cgpa REAL NOT NULL,

            graduation_year INTEGER NOT NULL,

            backlogs INTEGER NOT NULL DEFAULT 0,

            branch TEXT NOT NULL,

            target_job_role TEXT NOT NULL,

            technical_skills TEXT NOT NULL,

            certifications TEXT,

            projects TEXT,

            internships TEXT,

            github_url TEXT,

            linkedin_url TEXT,

            portfolio_url TEXT,

            resume_url TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)


    # ========================================================
    # QUESTIONS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            section TEXT NOT NULL,

            topic TEXT NOT NULL,

            question_text TEXT NOT NULL,

            option_a TEXT NOT NULL,

            option_b TEXT NOT NULL,

            option_c TEXT NOT NULL,

            option_d TEXT NOT NULL,

            correct_answer TEXT NOT NULL,

            explanation TEXT,

            difficulty TEXT NOT NULL DEFAULT 'Medium',

            branch TEXT,

            target_role TEXT,

            is_active INTEGER NOT NULL DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # ========================================================
    # ASSESSMENTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            branch TEXT NOT NULL,

            target_job_role TEXT NOT NULL,

            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            completed_at TIMESTAMP,

            status TEXT NOT NULL DEFAULT 'in_progress',

            total_questions INTEGER NOT NULL DEFAULT 0,

            answered_questions INTEGER NOT NULL DEFAULT 0,

            skipped_questions INTEGER NOT NULL DEFAULT 0,

            correct_answers INTEGER NOT NULL DEFAULT 0,

            wrong_answers INTEGER NOT NULL DEFAULT 0,

            score REAL NOT NULL DEFAULT 0,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)


    # ========================================================
    # QUESTION ATTEMPTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_attempts (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            assessment_id INTEGER NOT NULL,

            question_id INTEGER NOT NULL,

            selected_answer TEXT,

            status TEXT NOT NULL DEFAULT 'skipped',

            is_correct INTEGER NOT NULL DEFAULT 0,

            answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (assessment_id)
                REFERENCES assessments(id)
                ON DELETE CASCADE,

            FOREIGN KEY (question_id)
                REFERENCES questions(id)
                ON DELETE CASCADE,

            UNIQUE (
                assessment_id,
                question_id
            )
        )
    """)


    # ========================================================
    # ASSESSMENT RESULTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_results (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            assessment_id INTEGER NOT NULL UNIQUE,

            user_id INTEGER NOT NULL,

            technical_score REAL NOT NULL DEFAULT 0,

            aptitude_score REAL NOT NULL DEFAULT 0,

            logical_score REAL NOT NULL DEFAULT 0,

            communication_score REAL NOT NULL DEFAULT 0,

            coding_concepts_score REAL NOT NULL DEFAULT 0,

            coding_test_score REAL NOT NULL DEFAULT 0,

            overall_score REAL NOT NULL DEFAULT 0,

            readiness_score REAL NOT NULL DEFAULT 0,

            placement_probability REAL NOT NULL DEFAULT 0,

            strengths TEXT,

            weaknesses TEXT,

            recommendations TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (assessment_id)
                REFERENCES assessments(id)
                ON DELETE CASCADE,

            FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        )
    """)



    # ========================================================
    # CODING QUESTIONS
    # ========================================================

    cursor.execute("""
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


    # ========================================================
    # CODING ATTEMPTS
    # ========================================================

    cursor.execute("""
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


    # ========================================================
    # COMPANY REQUIREMENTS
    # ========================================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company_requirements (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            company_name TEXT NOT NULL UNIQUE,

            minimum_tenth_percentage REAL,

            minimum_twelfth_percentage REAL,

            minimum_cgpa REAL,

            maximum_backlogs INTEGER,

            eligible_branches TEXT,

            minimum_graduation_year INTEGER,

            maximum_graduation_year INTEGER,

            is_active INTEGER NOT NULL DEFAULT 1,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)



    # ========================================================
    # CODING ATTEMPTS MIGRATION
    # ========================================================
    # CREATE TABLE IF NOT EXISTS does not add columns to an
    # existing table. Add any newer coding-attempt columns safely.
    cursor.execute("PRAGMA table_info(coding_attempts)")
    coding_attempt_columns = {
        row["name"] for row in cursor.fetchall()
    }

    coding_attempt_migrations = {
        "language": "ALTER TABLE coding_attempts ADD COLUMN language TEXT",
        "submitted": (
            "ALTER TABLE coding_attempts "
            "ADD COLUMN submitted INTEGER NOT NULL DEFAULT 0"
        ),
        "score": (
            "ALTER TABLE coding_attempts "
            "ADD COLUMN score REAL NOT NULL DEFAULT 0"
        ),
        "started_at": (
            "ALTER TABLE coding_attempts "
            "ADD COLUMN started_at TIMESTAMP"
        ),
        "submitted_at": (
            "ALTER TABLE coding_attempts "
            "ADD COLUMN submitted_at TIMESTAMP"
        ),
    }

    for column_name, statement in coding_attempt_migrations.items():
        if column_name not in coding_attempt_columns:
            cursor.execute(statement)


    # ========================================================
    # INDEXES
    # ========================================================

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_questions_section
        ON questions(section)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_questions_branch
        ON questions(branch)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_questions_role
        ON questions(target_role)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_assessments_user
        ON assessments(user_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_attempts_assessment
        ON question_attempts(assessment_id)
    """)



    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_coding_questions_topic
        ON coding_questions(topic)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_coding_questions_difficulty
        ON coding_questions(difficulty)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_coding_attempts_user
        ON coding_attempts(user_id)
    """)


    # ========================================================
    # SAVE
    # ========================================================

    connection.commit()

    connection.close()


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    init_database()

    print(
        "CareerPredict database initialized successfully."
    )

    print(
        f"Database location: {DATABASE}"
    )