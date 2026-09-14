from flask import request, jsonify
from database import get_connection
from auth import hash_password


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


def safe_json_text(value):
    if value is None:
        return ""
    return str(value)


def user_public(row):
    return {
        "id": row["id"],
        "first_name": row["first_name"],
        "last_name": row["last_name"],
        "name": f'{row["first_name"]} {row["last_name"]}'.strip(),
        "email": row["email"],
        "phone": row["phone"],
        "college": row["college"],
        "role": row["role"],
        "created_at": row["created_at"],
        "has_profile": bool(row["has_profile"]),
        "assessment_count": int(row["assessment_count"] or 0),
    }


def register_user_admin_routes(app):
    @app.get("/api/admin/users")
    def admin_users():
        _, error = require_admin(request.args.get("user_id"))
        if error:
            return error

        search = request.args.get("search", "").strip()
        role = request.args.get("role", "").strip().lower()

        query = """
            SELECT
                u.id, u.first_name, u.last_name, u.email, u.phone, u.college,
                u.role, u.created_at,
                CASE WHEN sp.user_id IS NULL THEN 0 ELSE 1 END AS has_profile,
                (SELECT COUNT(*) FROM assessments a WHERE a.user_id = u.id) AS assessment_count
            FROM users u
            LEFT JOIN student_profiles sp ON sp.user_id = u.id
            WHERE 1=1
        """
        params = []

        if search:
            query += " AND (u.first_name LIKE ? OR u.last_name LIKE ? OR u.email LIKE ? OR u.college LIKE ? OR u.phone LIKE ?)"
            like = f"%{search}%"
            params.extend([like, like, like, like, like])

        if role in ("student", "admin"):
            query += " AND LOWER(u.role) = ?"
            params.append(role)

        query += " ORDER BY u.created_at DESC, u.id DESC"

        connection = get_connection()
        try:
            rows = connection.execute(query, params).fetchall()
            stats = connection.execute("""
                SELECT
                    COUNT(*) AS total_users,
                    SUM(CASE WHEN LOWER(role) = 'student' THEN 1 ELSE 0 END) AS total_students,
                    SUM(CASE WHEN LOWER(role) = 'admin' THEN 1 ELSE 0 END) AS total_admins,
                    (SELECT COUNT(*) FROM student_profiles) AS profiles_completed
                FROM users
            """).fetchone()

            return jsonify({
                "users": [user_public(row) for row in rows],
                "total": len(rows),
                "stats": {
                    "total_users": int(stats["total_users"] or 0),
                    "total_students": int(stats["total_students"] or 0),
                    "total_admins": int(stats["total_admins"] or 0),
                    "profiles_completed": int(stats["profiles_completed"] or 0),
                }
            }), 200
        finally:
            connection.close()

    @app.get("/api/admin/users/<int:user_id>")
    def admin_user_detail(user_id):
        _, error = require_admin(request.args.get("user_id"))
        if error:
            return error

        connection = get_connection()
        try:
            user = connection.execute("""
                SELECT id, first_name, last_name, email, phone, college, role, created_at
                FROM users WHERE id = ?
            """, (user_id,)).fetchone()
            if user is None:
                return jsonify({"error": "User not found."}), 404

            profile = connection.execute("""
                SELECT tenth_percentage, twelfth_percentage, cgpa, graduation_year,
                       backlogs, branch, target_job_role, technical_skills,
                       certifications, projects, internships, github_url,
                       linkedin_url, portfolio_url, resume_url
                FROM student_profiles WHERE user_id = ?
            """, (user_id,)).fetchone()

            latest = connection.execute("""
                SELECT id, status, score, correct_answers, wrong_answers,
                       skipped_questions, started_at, completed_at
                FROM assessments
                WHERE user_id = ?
                ORDER BY id DESC LIMIT 5
            """, (user_id,)).fetchall()

            return jsonify({
                "user": dict(user),
                "profile": dict(profile) if profile else None,
                "assessments": [dict(row) for row in latest]
            }), 200
        finally:
            connection.close()

    @app.patch("/api/admin/users/<int:user_id>/role")
    def admin_change_role(user_id):
        admin, error = require_admin(request.args.get("user_id"))
        if error:
            return error

        data = request.get_json(silent=True) or {}
        new_role = str(data.get("role", "")).strip().lower()
        if new_role not in ("student", "admin"):
            return jsonify({"error": "Role must be student or admin."}), 400

        if int(admin["id"]) == user_id and new_role != "admin":
            return jsonify({"error": "You cannot remove your own administrator role."}), 400

        connection = get_connection()
        try:
            target = connection.execute(
                "SELECT id, role FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if target is None:
                return jsonify({"error": "User not found."}), 404

            if str(target["role"]).lower() == "admin" and new_role == "student":
                admins = connection.execute(
                    "SELECT COUNT(*) AS count FROM users WHERE LOWER(role) = 'admin'"
                ).fetchone()["count"]
                if int(admins) <= 1:
                    return jsonify({"error": "At least one administrator account must remain."}), 400

            connection.execute(
                "UPDATE users SET role = ? WHERE id = ?",
                (new_role, user_id)
            )
            connection.commit()
            return jsonify({"message": "User role updated successfully.", "role": new_role}), 200
        except Exception as exc:
            connection.rollback()
            return jsonify({"error": "Unable to update user role.", "message": str(exc)}), 500
        finally:
            connection.close()

    @app.patch("/api/admin/users/<int:user_id>/password")
    def admin_reset_password(user_id):
        admin, error = require_admin(request.args.get("user_id"))
        if error:
            return error

        data = request.get_json(silent=True) or {}
        password = str(data.get("password", ""))
        if len(password) < 8:
            return jsonify({"error": "Password must be at least 8 characters."}), 400

        connection = get_connection()
        try:
            target = connection.execute(
                "SELECT id FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if target is None:
                return jsonify({"error": "User not found."}), 404

            connection.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (hash_password(password), user_id)
            )
            connection.commit()
            return jsonify({"message": "Password reset successfully."}), 200
        except Exception as exc:
            connection.rollback()
            return jsonify({"error": "Unable to reset password.", "message": str(exc)}), 500
        finally:
            connection.close()

    @app.delete("/api/admin/users/<int:user_id>")
    def admin_delete_user(user_id):
        admin, error = require_admin(request.args.get("user_id"))
        if error:
            return error

        if int(admin["id"]) == user_id:
            return jsonify({"error": "You cannot delete your own administrator account."}), 400

        connection = get_connection()
        try:
            target = connection.execute(
                "SELECT id, role, email FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if target is None:
                return jsonify({"error": "User not found."}), 404

            if str(target["role"]).lower() == "admin":
                admins = connection.execute(
                    "SELECT COUNT(*) AS count FROM users WHERE LOWER(role) = 'admin'"
                ).fetchone()["count"]
                if int(admins) <= 1:
                    return jsonify({"error": "At least one administrator account must remain."}), 400

            connection.execute("DELETE FROM users WHERE id = ?", (user_id,))
            connection.commit()
            return jsonify({"message": "User deleted successfully."}), 200
        except Exception as exc:
            connection.rollback()
            return jsonify({
                "error": "Unable to delete user. Existing linked records may prevent deletion.",
                "message": str(exc)
            }), 409
        finally:
            connection.close()
