from flask import request, jsonify
from database import get_connection
import json


SECTIONS = [
    "Technical",
    "Aptitude",
    "Logical Reasoning",
    "Communication",
    "Coding Concepts",
]

DIFFICULTIES = ["Easy", "Medium", "Hard"]


def require_admin(user_id):
    if not user_id:
        return None, (jsonify({"error": "Administrator authentication is required."}), 401)

    connection = get_connection()
    try:
        user = connection.execute(
            "SELECT id, first_name, last_name, email, role FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()
    finally:
        connection.close()

    if user is None or str(user["role"]).lower() != "admin":
        return None, (jsonify({"error": "Administrator access required."}), 403)

    return user, None


def public_question(row):
    return {
        "id": row["id"],
        "section": row["section"],
        "topic": row["topic"],
        "question_text": row["question_text"],
        "option_a": row["option_a"],
        "option_b": row["option_b"],
        "option_c": row["option_c"],
        "option_d": row["option_d"],
        "correct_answer": row["correct_answer"],
        "explanation": row["explanation"] or "",
        "difficulty": row["difficulty"],
        "branch": row["branch"] or "",
        "target_role": row["target_role"] or "",
        "is_active": bool(row["is_active"]),
        "created_at": row["created_at"],
    }


def validate_question(data):
    section = str(data.get("section", "")).strip()
    topic = str(data.get("topic", "")).strip()
    question_text = str(data.get("question_text", "")).strip()
    options = {
        "A": str(data.get("option_a", "")).strip(),
        "B": str(data.get("option_b", "")).strip(),
        "C": str(data.get("option_c", "")).strip(),
        "D": str(data.get("option_d", "")).strip(),
    }
    correct = str(data.get("correct_answer", "")).strip().upper()
    difficulty = str(data.get("difficulty", "Medium")).strip().title()
    branch = str(data.get("branch", "")).strip() or None
    target_role = str(data.get("target_role", "")).strip() or None
    explanation = str(data.get("explanation", "")).strip() or None

    if section not in SECTIONS:
        return None, "Select a valid assessment section."
    if not topic:
        return None, "Topic is required."
    if not question_text:
        return None, "Question text is required."
    if any(not value for value in options.values()):
        return None, "All four options are required."
    if correct not in options:
        return None, "Correct answer must be A, B, C or D."
    if difficulty not in DIFFICULTIES:
        return None, "Difficulty must be Easy, Medium or Hard."

    return {
        "section": section,
        "topic": topic,
        "question_text": question_text,
        "option_a": options["A"],
        "option_b": options["B"],
        "option_c": options["C"],
        "option_d": options["D"],
        "correct_answer": correct,
        "explanation": explanation,
        "difficulty": difficulty,
        "branch": branch,
        "target_role": target_role,
        "is_active": 1 if data.get("is_active", True) else 0,
    }, None


def register_question_admin_routes(app):

    @app.get("/api/admin/questions")
    def list_admin_questions():
        _, error = require_admin(request.args.get("user_id"))
        if error:
            return error

        section = request.args.get("section", "").strip()
        difficulty = request.args.get("difficulty", "").strip()
        search = request.args.get("search", "").strip()
        active = request.args.get("active", "").strip()

        query = "SELECT * FROM questions WHERE 1=1"
        params = []

        if section and section in SECTIONS:
            query += " AND section = ?"
            params.append(section)

        if difficulty and difficulty in DIFFICULTIES:
            query += " AND difficulty = ?"
            params.append(difficulty)

        if active in ("0", "1"):
            query += " AND is_active = ?"
            params.append(int(active))

        if search:
            query += " AND (question_text LIKE ? OR topic LIKE ? OR branch LIKE ? OR target_role LIKE ?)"
            like = f"%{search}%"
            params.extend([like, like, like, like])

        query += " ORDER BY id DESC"

        connection = get_connection()
        try:
            rows = connection.execute(query, params).fetchall()
            return jsonify({
                "questions": [public_question(row) for row in rows],
                "total": len(rows),
                "sections": SECTIONS,
                "difficulties": DIFFICULTIES,
            }), 200
        finally:
            connection.close()

    @app.get("/api/admin/questions/<int:question_id>")
    def get_admin_question(question_id):
        _, error = require_admin(request.args.get("user_id"))
        if error:
            return error

        connection = get_connection()
        try:
            row = connection.execute(
                "SELECT * FROM questions WHERE id = ?",
                (question_id,)
            ).fetchone()
            if row is None:
                return jsonify({"error": "Question not found."}), 404
            return jsonify({"question": public_question(row)}), 200
        finally:
            connection.close()

    @app.post("/api/admin/questions")
    def create_admin_question():
        _, error = require_admin(request.args.get("user_id"))
        if error:
            return error

        data = request.get_json(silent=True) or {}
        payload, validation_error = validate_question(data)
        if validation_error:
            return jsonify({"error": validation_error}), 400

        connection = get_connection()
        try:
            cursor = connection.execute("""
                INSERT INTO questions (
                    section, topic, question_text,
                    option_a, option_b, option_c, option_d,
                    correct_answer, explanation, difficulty,
                    branch, target_role, is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                payload["section"], payload["topic"], payload["question_text"],
                payload["option_a"], payload["option_b"],
                payload["option_c"], payload["option_d"],
                payload["correct_answer"], payload["explanation"],
                payload["difficulty"], payload["branch"],
                payload["target_role"], payload["is_active"],
            ))
            connection.commit()

            row = connection.execute(
                "SELECT * FROM questions WHERE id = ?",
                (cursor.lastrowid,)
            ).fetchone()

            return jsonify({
                "message": "Question created successfully.",
                "question": public_question(row)
            }), 201
        except Exception as exc:
            connection.rollback()
            return jsonify({
                "error": "Unable to create question.",
                "message": str(exc)
            }), 500
        finally:
            connection.close()

    @app.put("/api/admin/questions/<int:question_id>")
    def update_admin_question(question_id):
        _, error = require_admin(request.args.get("user_id"))
        if error:
            return error

        data = request.get_json(silent=True) or {}
        payload, validation_error = validate_question(data)
        if validation_error:
            return jsonify({"error": validation_error}), 400

        connection = get_connection()
        try:
            existing = connection.execute(
                "SELECT id FROM questions WHERE id = ?",
                (question_id,)
            ).fetchone()
            if existing is None:
                return jsonify({"error": "Question not found."}), 404

            connection.execute("""
                UPDATE questions
                SET section = ?,
                    topic = ?,
                    question_text = ?,
                    option_a = ?,
                    option_b = ?,
                    option_c = ?,
                    option_d = ?,
                    correct_answer = ?,
                    explanation = ?,
                    difficulty = ?,
                    branch = ?,
                    target_role = ?,
                    is_active = ?
                WHERE id = ?
            """, (
                payload["section"], payload["topic"], payload["question_text"],
                payload["option_a"], payload["option_b"],
                payload["option_c"], payload["option_d"],
                payload["correct_answer"], payload["explanation"],
                payload["difficulty"], payload["branch"],
                payload["target_role"], payload["is_active"],
                question_id,
            ))
            connection.commit()

            row = connection.execute(
                "SELECT * FROM questions WHERE id = ?",
                (question_id,)
            ).fetchone()

            return jsonify({
                "message": "Question updated successfully.",
                "question": public_question(row)
            }), 200
        except Exception as exc:
            connection.rollback()
            return jsonify({
                "error": "Unable to update question.",
                "message": str(exc)
            }), 500
        finally:
            connection.close()

    @app.patch("/api/admin/questions/<int:question_id>/status")
    def toggle_question_status(question_id):
        _, error = require_admin(request.args.get("user_id"))
        if error:
            return error

        data = request.get_json(silent=True) or {}
        is_active = bool(data.get("is_active"))

        connection = get_connection()
        try:
            cursor = connection.execute(
                "UPDATE questions SET is_active = ? WHERE id = ?",
                (1 if is_active else 0, question_id)
            )
            if cursor.rowcount == 0:
                return jsonify({"error": "Question not found."}), 404
            connection.commit()

            return jsonify({
                "message": "Question status updated.",
                "is_active": is_active
            }), 200
        finally:
            connection.close()

    @app.delete("/api/admin/questions/<int:question_id>")
    def delete_admin_question(question_id):
        _, error = require_admin(request.args.get("user_id"))
        if error:
            return error

        connection = get_connection()
        try:
            row = connection.execute(
                "SELECT id FROM questions WHERE id = ?",
                (question_id,)
            ).fetchone()
            if row is None:
                return jsonify({"error": "Question not found."}), 404

            # Never destroy historical assessment attempts. Use deactivate instead.
            used = connection.execute(
                "SELECT COUNT(*) AS count FROM question_attempts WHERE question_id = ?",
                (question_id,)
            ).fetchone()["count"]

            if used:
                return jsonify({
                    "error": "This question has historical assessment attempts and cannot be permanently deleted.",
                    "suggestion": "Deactivate the question instead.",
                    "attempt_count": used
                }), 409

            connection.execute(
                "DELETE FROM questions WHERE id = ?",
                (question_id,)
            )
            connection.commit()
            return jsonify({"message": "Question deleted successfully."}), 200
        finally:
            connection.close()
