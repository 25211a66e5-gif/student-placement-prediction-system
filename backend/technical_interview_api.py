from flask import request, jsonify
from database import get_connection
import json
import random
import re
from datetime import datetime

INTERVIEW_QUESTIONS = [{'id': 1, 'role': 'Software Developer', 'question': 'Explain the difference between an array and a linked list.', 'keywords': ['array', 'linked list', 'contiguous', 'node']}, {'id': 2, 'role': 'Software Developer', 'question': 'What is object-oriented programming? Explain encapsulation and inheritance.', 'keywords': ['object oriented', 'encapsulation', 'inheritance', 'class']}, {'id': 3, 'role': 'Software Developer', 'question': 'What is the time complexity of binary search and why?', 'keywords': ['o(log', 'logarithmic', 'sorted', 'divide']}, {'id': 4, 'role': 'Software Developer', 'question': 'How would you debug a program that works locally but fails in production?', 'keywords': ['logs', 'reproduce', 'environment', 'configuration', 'monitoring']}, {'id': 5, 'role': 'Software Developer', 'question': 'What is the purpose of Git and what is a branch?', 'keywords': ['version control', 'git', 'branch', 'merge']}, {'id': 6, 'role': 'Software Developer', 'question': 'How would you design a simple student placement application?', 'keywords': ['frontend', 'backend', 'database', 'api', 'authentication']}, {'id': 7, 'role': 'Software Developer', 'question': 'What is the difference between a process and a thread?', 'keywords': ['process', 'thread', 'memory', 'shared']}, {'id': 8, 'role': 'Software Developer', 'question': 'How do you handle an unexpected null or missing value in an application?', 'keywords': ['validation', 'null', 'default', 'exception', 'input']}, {'id': 9, 'role': 'Full-Stack Developer', 'question': 'What is the difference between frontend and backend development?', 'keywords': ['frontend', 'backend', 'browser', 'server']}, {'id': 10, 'role': 'Full-Stack Developer', 'question': 'What is a REST API and why is HTTP status code important?', 'keywords': ['rest', 'api', 'http', 'status', 'get', 'post']}, {'id': 11, 'role': 'Full-Stack Developer', 'question': 'Explain the difference between SQL and NoSQL databases.', 'keywords': ['sql', 'nosql', 'relational', 'document']}, {'id': 12, 'role': 'Full-Stack Developer', 'question': 'How would you secure a login API?', 'keywords': ['password', 'hash', 'authentication', 'authorization', 'https', 'token']}, {'id': 13, 'role': 'Full-Stack Developer', 'question': 'What happens when a browser requests a web page from a server?', 'keywords': ['dns', 'http', 'server', 'browser', 'response']}, {'id': 14, 'role': 'Full-Stack Developer', 'question': 'How would you improve a slow web application?', 'keywords': ['profiling', 'database', 'index', 'cache', 'frontend']}, {'id': 15, 'role': 'Full-Stack Developer', 'question': 'What is CORS and why can it appear during frontend-backend development?', 'keywords': ['cors', 'origin', 'browser', 'server']}, {'id': 16, 'role': 'Full-Stack Developer', 'question': 'How would you structure a production web application?', 'keywords': ['frontend', 'backend', 'database', 'api', 'logging', 'deployment']}, {'id': 17, 'role': 'Data Analyst', 'question': 'What is the difference between mean, median and mode?', 'keywords': ['mean', 'median', 'mode']}, {'id': 18, 'role': 'Data Analyst', 'question': 'How would you handle missing values in a dataset?', 'keywords': ['missing', 'remove', 'impute', 'median', 'mean']}, {'id': 19, 'role': 'Data Analyst', 'question': 'What is SQL GROUP BY used for?', 'keywords': ['group by', 'aggregate', 'count', 'sum', 'average']}, {'id': 20, 'role': 'Data Analyst', 'question': 'How do you identify an outlier?', 'keywords': ['outlier', 'iqr', 'standard deviation', 'distribution']}, {'id': 21, 'role': 'Data Analyst', 'question': 'What is the difference between correlation and causation?', 'keywords': ['correlation', 'causation', 'relationship']}, {'id': 22, 'role': 'Data Analyst', 'question': 'How would you present a business insight to a non-technical manager?', 'keywords': ['visualization', 'business', 'impact', 'simple', 'recommendation']}, {'id': 23, 'role': 'Data Analyst', 'question': 'Why is data cleaning important before analysis?', 'keywords': ['data quality', 'duplicate', 'missing', 'inconsistent']}, {'id': 24, 'role': 'Data Analyst', 'question': 'How would you validate a dashboard before sharing it?', 'keywords': ['accuracy', 'source', 'filter', 'calculation', 'validation']}, {'id': 25, 'role': 'Data Scientist', 'question': 'What is overfitting and how can you reduce it?', 'keywords': ['overfitting', 'regularization', 'cross validation', 'validation']}, {'id': 26, 'role': 'Data Scientist', 'question': 'Explain the difference between classification and regression.', 'keywords': ['classification', 'regression', 'categorical', 'continuous']}, {'id': 27, 'role': 'Data Scientist', 'question': 'What is train-test split used for?', 'keywords': ['train', 'test', 'generalization', 'unseen']}, {'id': 28, 'role': 'Data Scientist', 'question': 'What is precision and recall?', 'keywords': ['precision', 'recall', 'false positive', 'false negative']}, {'id': 29, 'role': 'Data Scientist', 'question': 'Why is feature scaling useful for some machine-learning algorithms?', 'keywords': ['scaling', 'normalization', 'standardization', 'distance']}, {'id': 30, 'role': 'Data Scientist', 'question': 'How would you handle an imbalanced classification dataset?', 'keywords': ['imbalanced', 'class weight', 'oversampling', 'undersampling', 'smote']}, {'id': 31, 'role': 'Data Scientist', 'question': 'How do you select useful features?', 'keywords': ['feature selection', 'correlation', 'importance', 'validation']}, {'id': 32, 'role': 'Data Scientist', 'question': 'How would you explain a machine-learning model to a business user?', 'keywords': ['interpretability', 'feature', 'impact', 'explain']}, {'id': 33, 'role': 'ML / AI Engineer', 'question': 'What is the difference between supervised and unsupervised learning?', 'keywords': ['supervised', 'unsupervised', 'label']}, {'id': 34, 'role': 'ML / AI Engineer', 'question': 'What is overfitting in machine learning?', 'keywords': ['overfitting', 'generalization', 'regularization']}, {'id': 35, 'role': 'ML / AI Engineer', 'question': 'Why do we split data into training and testing sets?', 'keywords': ['training', 'testing', 'unseen', 'generalization']}, {'id': 36, 'role': 'ML / AI Engineer', 'question': 'What is a confusion matrix?', 'keywords': ['confusion matrix', 'true positive', 'false positive', 'false negative']}, {'id': 37, 'role': 'ML / AI Engineer', 'question': 'What is gradient descent used for?', 'keywords': ['gradient descent', 'loss', 'optimization', 'learning rate']}, {'id': 38, 'role': 'ML / AI Engineer', 'question': 'How would you deploy a trained machine-learning model?', 'keywords': ['model', 'api', 'docker', 'deployment', 'monitoring']}, {'id': 39, 'role': 'ML / AI Engineer', 'question': 'What is data leakage and why is it dangerous?', 'keywords': ['data leakage', 'training', 'test', 'future', 'target']}, {'id': 40, 'role': 'ML / AI Engineer', 'question': 'How would you monitor an ML model after deployment?', 'keywords': ['drift', 'accuracy', 'latency', 'monitoring', 'data']}, {'id': 41, 'role': 'Backend Developer', 'question': 'What is an API?', 'keywords': ['api', 'application', 'interface', 'client', 'server']}, {'id': 42, 'role': 'Backend Developer', 'question': 'What is the difference between authentication and authorization?', 'keywords': ['authentication', 'authorization', 'identity', 'permission']}, {'id': 43, 'role': 'Backend Developer', 'question': 'Why are database indexes useful?', 'keywords': ['index', 'database', 'query', 'search']}, {'id': 44, 'role': 'Backend Developer', 'question': 'What is a transaction in a database?', 'keywords': ['transaction', 'commit', 'rollback', 'atomic']}, {'id': 45, 'role': 'Backend Developer', 'question': 'How do you protect an API from invalid input?', 'keywords': ['validation', 'sanitize', 'schema', 'input']}, {'id': 46, 'role': 'Backend Developer', 'question': 'What is caching and when would you use it?', 'keywords': ['cache', 'frequent', 'performance', 'stale']}, {'id': 47, 'role': 'Backend Developer', 'question': 'How would you investigate a slow API endpoint?', 'keywords': ['logs', 'latency', 'database', 'profiling', 'query']}, {'id': 48, 'role': 'Backend Developer', 'question': 'What is the purpose of environment variables?', 'keywords': ['environment', 'configuration', 'secret', 'deployment']}, {'id': 49, 'role': 'Frontend Developer', 'question': 'What is the DOM?', 'keywords': ['dom', 'document', 'html', 'tree']}, {'id': 50, 'role': 'Frontend Developer', 'question': 'What is the difference between HTML, CSS and JavaScript?', 'keywords': ['html', 'css', 'javascript', 'structure', 'style', 'behavior']}, {'id': 51, 'role': 'Frontend Developer', 'question': 'Why is responsive design important?', 'keywords': ['responsive', 'mobile', 'screen', 'layout']}, {'id': 52, 'role': 'Frontend Developer', 'question': 'What is an event listener in JavaScript?', 'keywords': ['event', 'listener', 'click', 'callback']}, {'id': 53, 'role': 'Frontend Developer', 'question': 'How would you improve a slow frontend page?', 'keywords': ['performance', 'image', 'lazy', 'bundle', 'cache']}, {'id': 54, 'role': 'Frontend Developer', 'question': 'What is component-based UI development?', 'keywords': ['component', 'reusable', 'ui', 'state']}, {'id': 55, 'role': 'Frontend Developer', 'question': 'How do you validate a form on the client side?', 'keywords': ['validation', 'input', 'required', 'error']}, {'id': 56, 'role': 'Frontend Developer', 'question': 'What is accessibility in web development?', 'keywords': ['accessibility', 'keyboard', 'screen reader', 'aria']}, {'id': 57, 'role': 'Embedded Engineer', 'question': 'What is a microcontroller?', 'keywords': ['microcontroller', 'cpu', 'memory', 'peripheral']}, {'id': 58, 'role': 'Embedded Engineer', 'question': 'What is the difference between RAM and ROM?', 'keywords': ['ram', 'rom', 'volatile', 'non volatile']}, {'id': 59, 'role': 'Embedded Engineer', 'question': 'What is an interrupt?', 'keywords': ['interrupt', 'cpu', 'handler', 'event']}, {'id': 60, 'role': 'Embedded Engineer', 'question': 'Why is C commonly used in embedded systems?', 'keywords': ['c', 'memory', 'hardware', 'performance']}, {'id': 61, 'role': 'Embedded Engineer', 'question': 'What is UART and where is it used?', 'keywords': ['uart', 'serial', 'communication', 'tx', 'rx']}, {'id': 62, 'role': 'Embedded Engineer', 'question': 'How would you debug a hardware-software integration problem?', 'keywords': ['debug', 'logs', 'signal', 'datasheet', 'test']}, {'id': 63, 'role': 'Embedded Engineer', 'question': 'What is an ADC?', 'keywords': ['adc', 'analog', 'digital', 'conversion']}, {'id': 64, 'role': 'Embedded Engineer', 'question': 'Why are memory constraints important in embedded systems?', 'keywords': ['memory', 'ram', 'flash', 'resource']}, {'id': 65, 'role': 'Other Technical Role', 'question': 'Explain the difference between an array and a linked list.', 'keywords': ['array', 'linked list', 'contiguous', 'node']}, {'id': 66, 'role': 'Other Technical Role', 'question': 'What is object-oriented programming? Explain encapsulation and inheritance.', 'keywords': ['object oriented', 'encapsulation', 'inheritance', 'class']}, {'id': 67, 'role': 'Other Technical Role', 'question': 'What is the time complexity of binary search and why?', 'keywords': ['o(log', 'logarithmic', 'sorted', 'divide']}, {'id': 68, 'role': 'Other Technical Role', 'question': 'How would you debug a program that works locally but fails in production?', 'keywords': ['logs', 'reproduce', 'environment', 'configuration', 'monitoring']}, {'id': 69, 'role': 'Other Technical Role', 'question': 'What is the purpose of Git and what is a branch?', 'keywords': ['version control', 'git', 'branch', 'merge']}, {'id': 70, 'role': 'Other Technical Role', 'question': 'How would you design a simple student placement application?', 'keywords': ['frontend', 'backend', 'database', 'api', 'authentication']}, {'id': 71, 'role': 'Other Technical Role', 'question': 'What is the difference between a process and a thread?', 'keywords': ['process', 'thread', 'memory', 'shared']}, {'id': 72, 'role': 'Other Technical Role', 'question': 'How do you handle an unexpected null or missing value in an application?', 'keywords': ['validation', 'null', 'default', 'exception', 'input']}]

QUESTION_COUNT = 8


def ensure_interview_tables():
    connection = get_connection()
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS technical_interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                assessment_id INTEGER NOT NULL UNIQUE,
                user_id INTEGER NOT NULL,
                target_job_role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'in_progress',
                total_questions INTEGER NOT NULL DEFAULT 0,
                answered_questions INTEGER NOT NULL DEFAULT 0,
                skipped_questions INTEGER NOT NULL DEFAULT 0,
                score REAL NOT NULL DEFAULT 0,
                started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS technical_interview_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interview_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                keywords TEXT NOT NULL,
                answer TEXT,
                status TEXT NOT NULL DEFAULT 'skipped',
                score REAL NOT NULL DEFAULT 0,
                feedback TEXT,
                answered_at TEXT,
                UNIQUE(interview_id, question_id),
                FOREIGN KEY (interview_id) REFERENCES technical_interviews(id) ON DELETE CASCADE
            )
        """)
        connection.commit()
    finally:
        connection.close()


def normalize(text):
    return re.sub(r"[^a-z0-9+#. ]+", " ", (text or "").lower())


def score_answer(answer, keywords):
    text = normalize(answer)
    if not text.strip():
        return 0, "Skipped. Review the model answer and practice explaining the concept in your own words."

    hits = []
    for keyword in keywords:
        k = normalize(keyword).strip()
        if k and k in text:
            hits.append(keyword)

    ratio = len(set(hits)) / max(1, len(keywords))
    # Require substance as well as keyword coverage.
    length_bonus = 1 if len(text.split()) >= 18 else 0
    score = min(100, round(ratio * 85 + length_bonus * 15))

    if score >= 80:
        feedback = "Strong response. You covered the main technical concepts expected for this question."
    elif score >= 55:
        feedback = "Good start, but your answer could be more complete. Add definitions, reasoning and a practical example."
    elif score > 0:
        feedback = "Partial answer. Revisit the core concept and explain the important terms more clearly."
    else:
        feedback = "The answer did not contain enough of the expected concepts. Review the model answer before retrying."

    return score, feedback


def public_attempt(row):
    return {
        "id": row["id"],
        "question_text": row["question_text"],
        "status": row["status"],
        "score": row["score"],
        "feedback": row["feedback"],
        "answer": row["answer"],
    }



def update_final_readiness(connection, assessment_id, interview_score):
    """
    Blend the existing assessment readiness with the technical interview score.
    The interview contributes 15% to the final readiness score.
    """
    row = connection.execute("""
        SELECT readiness_score
        FROM assessment_results
        WHERE assessment_id = ?
    """, (assessment_id,)).fetchone()

    if row is None:
        return None

    previous = float(row["readiness_score"] or 0)
    final_score = round(previous * 0.85 + float(interview_score) * 0.15, 2)

    connection.execute("""
        UPDATE assessment_results
        SET readiness_score = ?
        WHERE assessment_id = ?
    """, (final_score, assessment_id))

    return final_score


def register_technical_interview_routes(app):
    ensure_interview_tables()

    @app.post("/api/interview/start")
    def start_interview():
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        assessment_id = data.get("assessment_id")

        if not user_id or not assessment_id:
            return jsonify({"error": "user_id and assessment_id are required."}), 400

        connection = get_connection()
        try:
            assessment = connection.execute("""
                SELECT id, user_id, status
                FROM assessments
                WHERE id = ? AND user_id = ?
            """, (assessment_id, user_id)).fetchone()

            if assessment is None:
                return jsonify({"error": "Assessment not found."}), 404
            if assessment["status"] != "completed":
                return jsonify({"error": "Complete the assessment before starting the interview."}), 400

            profile = connection.execute("""
                SELECT target_job_role
                FROM student_profiles
                WHERE user_id = ?
            """, (user_id,)).fetchone()

            if profile is None:
                return jsonify({"error": "Student profile not found."}), 404

            existing = connection.execute("""
                SELECT *
                FROM technical_interviews
                WHERE assessment_id = ? AND user_id = ?
            """, (assessment_id, user_id)).fetchone()

            if existing:
                return jsonify({
                    "interview_id": existing["id"],
                    "status": existing["status"],
                    "total_questions": existing["total_questions"]
                })

            role = profile["target_job_role"] or "Software Developer"
            pool = [q for q in INTERVIEW_QUESTIONS if q["role"] == role]
            if len(pool) < QUESTION_COUNT:
                pool = [q for q in INTERVIEW_QUESTIONS if q["role"] == "Software Developer"]

            selected = random.sample(pool, QUESTION_COUNT)

            cursor = connection.execute("""
                INSERT INTO technical_interviews
                (assessment_id, user_id, target_job_role, status, total_questions)
                VALUES (?, ?, ?, 'in_progress', ?)
            """, (assessment_id, user_id, role, len(selected)))
            interview_id = cursor.lastrowid

            for q in selected:
                connection.execute("""
                    INSERT INTO technical_interview_attempts
                    (interview_id, question_id, question_text, keywords)
                    VALUES (?, ?, ?, ?)
                """, (
                    interview_id, q["id"], q["question"],
                    json.dumps(q["keywords"])
                ))

            connection.commit()
            return jsonify({
                "interview_id": interview_id,
                "status": "in_progress",
                "target_job_role": role,
                "total_questions": len(selected)
            }), 200
        finally:
            connection.close()

    @app.get("/api/interview/<int:interview_id>/questions")
    def get_interview_questions(interview_id):
        user_id = request.args.get("user_id")
        connection = get_connection()
        try:
            interview = connection.execute("""
                SELECT *
                FROM technical_interviews
                WHERE id = ? AND user_id = ?
            """, (interview_id, user_id)).fetchone()

            if interview is None:
                return jsonify({"error": "Interview not found."}), 404

            rows = connection.execute("""
                SELECT id, question_id, question_text, status, score, answer, feedback
                FROM technical_interview_attempts
                WHERE interview_id = ?
                ORDER BY id
            """, (interview_id,)).fetchall()

            return jsonify({
                "interview": {
                    "id": interview["id"],
                    "status": interview["status"],
                    "target_job_role": interview["target_job_role"],
                    "total_questions": interview["total_questions"],
                    "answered_questions": interview["answered_questions"],
                    "skipped_questions": interview["skipped_questions"],
                    "score": interview["score"],
                },
                "questions": [public_attempt(row) | {"question_id": row["question_id"]} for row in rows]
            }), 200
        finally:
            connection.close()

    @app.post("/api/interview/answer")
    def save_interview_answer():
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        interview_id = data.get("interview_id")
        question_id = data.get("question_id")
        answer = data.get("answer")

        if not user_id or not interview_id or not question_id:
            return jsonify({"error": "user_id, interview_id and question_id are required."}), 400

        connection = get_connection()
        try:
            interview = connection.execute("""
                SELECT *
                FROM technical_interviews
                WHERE id = ? AND user_id = ?
            """, (interview_id, user_id)).fetchone()

            if interview is None:
                return jsonify({"error": "Interview not found."}), 404
            if interview["status"] != "in_progress":
                return jsonify({"error": "This interview is already completed."}), 400

            row = connection.execute("""
                SELECT *
                FROM technical_interview_attempts
                WHERE interview_id = ? AND question_id = ?
            """, (interview_id, question_id)).fetchone()

            if row is None:
                return jsonify({"error": "Interview question not found."}), 404

            if answer is None or not str(answer).strip():
                score = 0
                status = "skipped"
                feedback = "Skipped. Review the model answer and practice this topic."
                clean_answer = None
            else:
                clean_answer = str(answer).strip()
                keywords = json.loads(row["keywords"])
                score, feedback = score_answer(clean_answer, keywords)
                status = "answered"

            connection.execute("""
                UPDATE technical_interview_attempts
                SET answer = ?, status = ?, score = ?, feedback = ?, answered_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (clean_answer, status, score, feedback, row["id"]))

            answered = connection.execute("""
                SELECT COUNT(*) AS c FROM technical_interview_attempts
                WHERE interview_id = ? AND status = 'answered'
            """, (interview_id,)).fetchone()["c"]

            skipped = connection.execute("""
                SELECT COUNT(*) AS c FROM technical_interview_attempts
                WHERE interview_id = ? AND status = 'skipped'
            """, (interview_id,)).fetchone()["c"]

            connection.execute("""
                UPDATE technical_interviews
                SET answered_questions = ?, skipped_questions = ?
                WHERE id = ?
            """, (answered, skipped, interview_id))

            connection.commit()

            return jsonify({
                "message": "Interview answer saved.",
                "status": status,
                "score": score,
                "feedback": feedback,
                "answered_questions": answered,
                "skipped_questions": skipped
            }), 200
        finally:
            connection.close()

    @app.post("/api/interview/finish")
    def finish_interview():
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")
        interview_id = data.get("interview_id")

        connection = get_connection()
        try:
            interview = connection.execute("""
                SELECT *
                FROM technical_interviews
                WHERE id = ? AND user_id = ?
            """, (interview_id, user_id)).fetchone()

            if interview is None:
                return jsonify({"error": "Interview not found."}), 404

            rows = connection.execute("""
                SELECT score, status
                FROM technical_interview_attempts
                WHERE interview_id = ?
            """, (interview_id,)).fetchall()

            total = len(rows)
            score = round(sum(r["score"] for r in rows) / total, 2) if total else 0
            answered = sum(1 for r in rows if r["status"] == "answered")
            skipped = total - answered

            connection.execute("""
                UPDATE technical_interviews
                SET status = 'completed',
                    answered_questions = ?,
                    skipped_questions = ?,
                    score = ?,
                    completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (answered, skipped, score, interview_id))

            final_readiness = update_final_readiness(
                connection,
                interview["assessment_id"],
                score
            )

            connection.commit()

            return jsonify({
                "message": "Technical interview completed.",
                "interview_id": interview_id,
                "score": score,
                "total_questions": total,
                "answered_questions": answered,
                "skipped_questions": skipped,
                "final_readiness_score": final_readiness
            }), 200
        finally:
            connection.close()

    @app.get("/api/interview/<int:interview_id>/result")
    def interview_result(interview_id):
        user_id = request.args.get("user_id")
        connection = get_connection()
        try:
            interview = connection.execute("""
                SELECT *
                FROM technical_interviews
                WHERE id = ? AND user_id = ?
            """, (interview_id, user_id)).fetchone()

            if interview is None:
                return jsonify({"error": "Interview not found."}), 404

            rows = connection.execute("""
                SELECT id, question_id, question_text, answer, status, score, feedback
                FROM technical_interview_attempts
                WHERE interview_id = ?
                ORDER BY id
            """, (interview_id,)).fetchall()

            # Model answers are generated from the rubric topics without exposing hidden scoring data.
            model_answers = {}
            for q in INTERVIEW_QUESTIONS:
                model_answers[q["id"]] = (
                    "A strong answer should clearly explain the core concept, "
                    "use the important technical terms, and include a practical example where appropriate."
                )

            review = []
            for row in rows:
                review.append({
                    "question_id": row["question_id"],
                    "question": row["question_text"],
                    "answer": row["answer"],
                    "status": row["status"],
                    "score": row["score"],
                    "feedback": row["feedback"],
                    "model_answer_guidance": model_answers.get(row["question_id"], "")
                })

            return jsonify({
                "interview": dict(interview),
                "review": review
            }), 200
        finally:
            connection.close()
