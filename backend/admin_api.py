from flask import request, jsonify
from database import get_connection
import json


def ensure_company_requirements_table():
    connection = get_connection()
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS company_requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL UNIQUE,
                minimum_tenth_percentage REAL NOT NULL DEFAULT 0,
                minimum_twelfth_percentage REAL NOT NULL DEFAULT 0,
                minimum_cgpa REAL NOT NULL DEFAULT 0,
                maximum_backlogs INTEGER NOT NULL DEFAULT 999,
                eligible_branches TEXT,
                minimum_graduation_year INTEGER,
                maximum_graduation_year INTEGER,
                minimum_assessment_score REAL NOT NULL DEFAULT 0,
                minimum_coding_test_score REAL NOT NULL DEFAULT 0,
                minimum_interview_score REAL NOT NULL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Safe migration for databases created by earlier versions.
        columns = {row[1] for row in connection.execute("PRAGMA table_info(company_requirements)").fetchall()}
        migrations = {
            "minimum_assessment_score": "ALTER TABLE company_requirements ADD COLUMN minimum_assessment_score REAL NOT NULL DEFAULT 0",
            "minimum_coding_test_score": "ALTER TABLE company_requirements ADD COLUMN minimum_coding_test_score REAL NOT NULL DEFAULT 0",
            "minimum_interview_score": "ALTER TABLE company_requirements ADD COLUMN minimum_interview_score REAL NOT NULL DEFAULT 0",
        }
        for column, sql in migrations.items():
            if column not in columns:
                connection.execute(sql)
        connection.commit()
    finally:
        connection.close()


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


def parse_branches(value):
    if value is None:
        return None
    if isinstance(value, list):
        items = value
    else:
        raw = str(value).strip()
        if not raw:
            return None
        try:
            parsed = json.loads(raw)
            items = parsed if isinstance(parsed, list) else raw.split(",")
        except Exception:
            items = raw.split(",")
    cleaned = []
    for item in items:
        item = str(item).strip()
        if item and item not in cleaned:
            cleaned.append(item)
    return json.dumps(cleaned) if cleaned else None


def optional_year(value):
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    return int(value)


def company_public(row):
    branches = []
    if row["eligible_branches"]:
        try:
            parsed = json.loads(row["eligible_branches"])
            branches = parsed if isinstance(parsed, list) else []
        except Exception:
            branches = [x.strip() for x in str(row["eligible_branches"]).split(",") if x.strip()]
    return {
        "id": row["id"],
        "company_name": row["company_name"],
        "minimum_tenth_percentage": row["minimum_tenth_percentage"],
        "minimum_twelfth_percentage": row["minimum_twelfth_percentage"],
        "minimum_cgpa": row["minimum_cgpa"],
        "maximum_backlogs": row["maximum_backlogs"],
        "eligible_branches": branches,
        "minimum_graduation_year": row["minimum_graduation_year"],
        "maximum_graduation_year": row["maximum_graduation_year"],
        "minimum_assessment_score": row["minimum_assessment_score"],
        "minimum_coding_test_score": row["minimum_coding_test_score"],
        "minimum_interview_score": row["minimum_interview_score"],
        "is_active": bool(row["is_active"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def parse_criteria(data):
    try:
        values = {
            "tenth": float(data.get("minimum_tenth_percentage", 0)),
            "twelfth": float(data.get("minimum_twelfth_percentage", 0)),
            "cgpa": float(data.get("minimum_cgpa", 0)),
            "max_backlogs": int(data.get("maximum_backlogs", 999)),
            "min_year": optional_year(data.get("minimum_graduation_year")),
            "max_year": optional_year(data.get("maximum_graduation_year")),
            "assessment": float(data.get("minimum_assessment_score", 0)),
            "coding": float(data.get("minimum_coding_test_score", 0)),
            "interview": float(data.get("minimum_interview_score", 0)),
        }
    except (TypeError, ValueError):
        raise ValueError("Numeric company criteria are invalid.")
    if not (0 <= values["tenth"] <= 100 and 0 <= values["twelfth"] <= 100):
        raise ValueError("Percentage criteria must be between 0 and 100.")
    if not (0 <= values["cgpa"] <= 10):
        raise ValueError("CGPA must be between 0 and 10.")
    if values["max_backlogs"] < 0:
        raise ValueError("Maximum backlogs cannot be negative.")
    for key in ("assessment", "coding", "interview"):
        if not (0 <= values[key] <= 100):
            raise ValueError("Assessment, coding and interview criteria must be between 0 and 100.")
    if values["min_year"] is not None and values["max_year"] is not None and values["min_year"] > values["max_year"]:
        raise ValueError("Minimum graduation year cannot exceed maximum year.")
    return values


def register_admin_routes(app):
    ensure_company_requirements_table()

    @app.get("/api/admin/me")
    def admin_me():
        user, error = require_admin(request.args.get("user_id"))
        if error:
            return error
        return jsonify({"is_admin": True, "user": {"id": user["id"], "name": f'{user["first_name"]} {user["last_name"]}'.strip(), "email": user["email"], "role": user["role"]}}), 200

    @app.get("/api/admin/companies")
    def admin_companies():
        _, error = require_admin(request.args.get("user_id"))
        if error:
            return error
        connection = get_connection()
        try:
            rows = connection.execute("SELECT * FROM company_requirements ORDER BY company_name COLLATE NOCASE").fetchall()
            return jsonify({"companies": [company_public(row) for row in rows]}), 200
        finally:
            connection.close()

    @app.post("/api/admin/companies")
    def create_company():
        _, error = require_admin(request.args.get("user_id"))
        if error:
            return error
        data = request.get_json(silent=True) or {}
        name = str(data.get("company_name", "")).strip()
        if not name:
            return jsonify({"error": "Company name is required."}), 400
        try:
            c = parse_criteria(data)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        connection = get_connection()
        try:
            connection.execute("""
                INSERT INTO company_requirements (
                    company_name, minimum_tenth_percentage, minimum_twelfth_percentage,
                    minimum_cgpa, maximum_backlogs, eligible_branches,
                    minimum_graduation_year, maximum_graduation_year,
                    minimum_assessment_score, minimum_coding_test_score, minimum_interview_score,
                    is_active, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (name, c["tenth"], c["twelfth"], c["cgpa"], c["max_backlogs"], parse_branches(data.get("eligible_branches")), c["min_year"], c["max_year"], c["assessment"], c["coding"], c["interview"], 1 if data.get("is_active", True) else 0))
            connection.commit()
            row = connection.execute("SELECT * FROM company_requirements WHERE company_name = ?", (name,)).fetchone()
            return jsonify({"message": "Company criteria created.", "company": company_public(row)}), 201
        except Exception as exc:
            connection.rollback()
            if "UNIQUE" in str(exc).upper():
                return jsonify({"error": "A company with this name already exists."}), 409
            return jsonify({"error": "Unable to create company criteria."}), 500
        finally:
            connection.close()

    @app.put("/api/admin/companies/<int:company_id>")
    def update_company(company_id):
        _, error = require_admin(request.args.get("user_id"))
        if error:
            return error
        data = request.get_json(silent=True) or {}
        name = str(data.get("company_name", "")).strip()
        if not name:
            return jsonify({"error": "Company name is required."}), 400
        try:
            c = parse_criteria(data)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        connection = get_connection()
        try:
            existing = connection.execute("SELECT id FROM company_requirements WHERE id = ?", (company_id,)).fetchone()
            if existing is None:
                return jsonify({"error": "Company criteria not found."}), 404
            connection.execute("""
                UPDATE company_requirements SET company_name=?, minimum_tenth_percentage=?, minimum_twelfth_percentage=?,
                minimum_cgpa=?, maximum_backlogs=?, eligible_branches=?, minimum_graduation_year=?, maximum_graduation_year=?,
                minimum_assessment_score=?, minimum_coding_test_score=?, minimum_interview_score=?, is_active=?, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, (name, c["tenth"], c["twelfth"], c["cgpa"], c["max_backlogs"], parse_branches(data.get("eligible_branches")), c["min_year"], c["max_year"], c["assessment"], c["coding"], c["interview"], 1 if data.get("is_active", True) else 0, company_id))
            connection.commit()
            row = connection.execute("SELECT * FROM company_requirements WHERE id = ?", (company_id,)).fetchone()
            return jsonify({"message": "Company criteria updated.", "company": company_public(row)}), 200
        except Exception as exc:
            connection.rollback()
            if "UNIQUE" in str(exc).upper():
                return jsonify({"error": "A company with this name already exists."}), 409
            return jsonify({"error": "Unable to update company criteria."}), 500
        finally:
            connection.close()

    @app.patch("/api/admin/companies/<int:company_id>/status")
    def toggle_company(company_id):
        _, error = require_admin(request.args.get("user_id"))
        if error:
            return error
        data = request.get_json(silent=True) or {}
        connection = get_connection()
        try:
            row = connection.execute("SELECT is_active FROM company_requirements WHERE id=?", (company_id,)).fetchone()
            if row is None:
                return jsonify({"error": "Company criteria not found."}), 404
            active = bool(data.get("is_active", not bool(row["is_active"])))
            connection.execute("UPDATE company_requirements SET is_active=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (1 if active else 0, company_id))
            connection.commit()
            return jsonify({"message": "Company status updated.", "is_active": active}), 200
        finally:
            connection.close()

    @app.delete("/api/admin/companies/<int:company_id>")
    def delete_company(company_id):
        _, error = require_admin(request.args.get("user_id"))
        if error:
            return error
        connection = get_connection()
        try:
            cursor = connection.execute("DELETE FROM company_requirements WHERE id=?", (company_id,))
            if cursor.rowcount == 0:
                return jsonify({"error": "Company criteria not found."}), 404
            connection.commit()
            return jsonify({"message": "Company criteria deleted."}), 200
        finally:
            connection.close()
