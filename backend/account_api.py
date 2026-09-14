from flask import request, jsonify
from database import get_connection
from auth import hash_password
import os
import secrets
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta

OTP_EXPIRY_MINUTES = 10
OTP_RESEND_SECONDS = 60
MAX_OTP_ATTEMPTS = 5


def ensure_password_reset_table():
    connection = get_connection()
    try:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_otps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email TEXT NOT NULL,
                otp_hash TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                used INTEGER NOT NULL DEFAULT 0,
                last_sent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_password_reset_email
            ON password_reset_otps(email, used, expires_at)
        """)
        connection.commit()
    finally:
        connection.close()


def _hash_otp(otp):
    import hashlib
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def _send_otp_email(email, otp):
    host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME", "")
    password = os.getenv("SMTP_PASSWORD", "")
    sender = os.getenv("SMTP_FROM", username)

    if not username or not password or not sender:
        raise RuntimeError(
            "Email service is not configured. Set SMTP_USERNAME, "
            "SMTP_PASSWORD and SMTP_FROM in the backend environment."
        )

    message = EmailMessage()
    message["Subject"] = "CareerPredict Password Reset OTP"
    message["From"] = sender
    message["To"] = email
    message.set_content(
        f"""CareerPredict Password Reset

Your password reset OTP is: {otp}

This OTP is valid for {OTP_EXPIRY_MINUTES} minutes and can be used only once.

If you did not request a password reset, you can safely ignore this email.
"""
    )

    with smtplib.SMTP(host, port, timeout=20) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(message)


def register_account_routes(app):
    ensure_password_reset_table()

    @app.get("/api/account/profile/<int:user_id>")
    def get_account_profile(user_id):
        connection = get_connection()
        try:
            user = connection.execute("""
                SELECT id, first_name, last_name, email, phone, college, role
                FROM users
                WHERE id = ?
            """, (user_id,)).fetchone()

            if user is None:
                return jsonify({"error": "User account not found."}), 404

            profile = connection.execute("""
                SELECT
                    tenth_percentage, twelfth_percentage, cgpa,
                    graduation_year, backlogs, branch, target_job_role,
                    technical_skills, certifications, projects, internships,
                    github_url, linkedin_url, portfolio_url, resume_url
                FROM student_profiles
                WHERE user_id = ?
            """, (user_id,)).fetchone()

            return jsonify({
                "user": dict(user),
                "profile": dict(profile) if profile else None
            }), 200
        finally:
            connection.close()

    @app.post("/api/account/profile")
    def update_account_profile():
        data = request.get_json(silent=True) or {}
        user_id = data.get("user_id")

        if not user_id:
            return jsonify({"error": "User ID is required."}), 400

        connection = get_connection()
        try:
            user = connection.execute(
                "SELECT id FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            if user is None:
                return jsonify({"error": "User account not found."}), 404

            first_name = str(data.get("first_name", "")).strip()
            last_name = str(data.get("last_name", "")).strip()
            phone = str(data.get("phone", "")).strip()
            college = str(data.get("college", "")).strip()

            if not first_name or not last_name:
                return jsonify({"error": "First and last name are required."}), 400
            if not phone:
                return jsonify({"error": "Phone number is required."}), 400
            if not college:
                return jsonify({"error": "College or university is required."}), 400

            connection.execute("""
                UPDATE users
                SET first_name = ?, last_name = ?, phone = ?, college = ?
                WHERE id = ?
            """, (first_name, last_name, phone, college, user_id))

            profile = connection.execute("""
                SELECT id FROM student_profiles WHERE user_id = ?
            """, (user_id,)).fetchone()

            if profile:
                fields = [
                    "tenth_percentage", "twelfth_percentage", "cgpa",
                    "graduation_year", "backlogs", "branch", "target_job_role",
                    "technical_skills", "certifications", "projects", "internships",
                    "github_url", "linkedin_url", "portfolio_url", "resume_url"
                ]
                values = [data.get(field) for field in fields]

                if any(v is not None for v in values):
                    connection.execute("""
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
                    """, tuple(values) + (user_id,))

            connection.commit()

            updated = connection.execute("""
                SELECT id, first_name, last_name, email, phone, college, role
                FROM users WHERE id = ?
            """, (user_id,)).fetchone()

            return jsonify({
                "message": "Profile updated successfully.",
                "user": dict(updated)
            }), 200
        except Exception as error:
            connection.rollback()
            return jsonify({
                "error": "Profile update failed.",
                "message": str(error)
            }), 500
        finally:
            connection.close()

    @app.post("/api/password/forgot")
    def request_password_reset():
        data = request.get_json(silent=True) or {}
        email = str(data.get("email", "")).strip().lower()

        if not email:
            return jsonify({"error": "Email is required."}), 400

        connection = get_connection()
        try:
            user = connection.execute("""
                SELECT id, email FROM users WHERE email = ?
            """, (email,)).fetchone()

            # Do not reveal whether an account exists.
            if user is None:
                return jsonify({
                    "message": "If an account exists for this email, an OTP has been sent."
                }), 200

            latest = connection.execute("""
                SELECT last_sent_at
                FROM password_reset_otps
                WHERE user_id = ? AND used = 0
                ORDER BY id DESC LIMIT 1
            """, (user["id"],)).fetchone()

            if latest:
                try:
                    sent_at = datetime.fromisoformat(
                        latest["last_sent_at"].replace("Z", "")
                    )
                    if datetime.utcnow() - sent_at < timedelta(seconds=OTP_RESEND_SECONDS):
                        return jsonify({
                            "error": "Please wait before requesting another OTP."
                        }), 429
                except ValueError:
                    pass

            otp = f"{secrets.randbelow(1000000):06d}"
            otp_hash = _hash_otp(otp)
            expires_at = (datetime.utcnow() + timedelta(
                minutes=OTP_EXPIRY_MINUTES
            )).isoformat(timespec="seconds")

            connection.execute("""
                UPDATE password_reset_otps
                SET used = 1
                WHERE user_id = ? AND used = 0
            """, (user["id"],))

            connection.execute("""
                INSERT INTO password_reset_otps
                (user_id, email, otp_hash, expires_at, attempts, used)
                VALUES (?, ?, ?, ?, 0, 0)
            """, (user["id"], email, otp_hash, expires_at))

            connection.commit()

            try:
                _send_otp_email(email, otp)
            except Exception:
                connection.rollback()
                raise

            return jsonify({
                "message": "If an account exists for this email, an OTP has been sent.",
                "expires_in_seconds": OTP_EXPIRY_MINUTES * 60
            }), 200

        except Exception as error:
            connection.rollback()
            return jsonify({
                "error": "Unable to send OTP.",
                "message": str(error)
            }), 500
        finally:
            connection.close()

    @app.post("/api/password/verify-otp")
    def verify_reset_otp():
        data = request.get_json(silent=True) or {}
        email = str(data.get("email", "")).strip().lower()
        otp = str(data.get("otp", "")).strip()

        if not email or not otp:
            return jsonify({"error": "Email and OTP are required."}), 400

        connection = get_connection()
        try:
            row = connection.execute("""
                SELECT *
                FROM password_reset_otps
                WHERE email = ? AND used = 0
                ORDER BY id DESC LIMIT 1
            """, (email,)).fetchone()

            if row is None:
                return jsonify({"error": "Invalid or expired OTP."}), 400

            if datetime.utcnow() > datetime.fromisoformat(row["expires_at"]):
                return jsonify({"error": "OTP has expired. Request a new OTP."}), 400

            if row["attempts"] >= MAX_OTP_ATTEMPTS:
                return jsonify({"error": "Too many OTP attempts. Request a new OTP."}), 429

            if not secrets.compare_digest(_hash_otp(otp), row["otp_hash"]):
                connection.execute("""
                    UPDATE password_reset_otps
                    SET attempts = attempts + 1
                    WHERE id = ?
                """, (row["id"],))
                connection.commit()
                return jsonify({"error": "Invalid or expired OTP."}), 400

            return jsonify({
                "message": "OTP verified successfully.",
                "reset_token": secrets.token_urlsafe(32)
            }), 200
        finally:
            connection.close()

    @app.post("/api/password/reset")
    def reset_password():
        data = request.get_json(silent=True) or {}
        email = str(data.get("email", "")).strip().lower()
        otp = str(data.get("otp", "")).strip()
        new_password = str(data.get("new_password", ""))

        if not email or not otp or not new_password:
            return jsonify({
                "error": "Email, OTP and new password are required."
            }), 400

        if len(new_password) < 8:
            return jsonify({
                "error": "Password must contain at least 8 characters."
            }), 400

        connection = get_connection()
        try:
            row = connection.execute("""
                SELECT *
                FROM password_reset_otps
                WHERE email = ? AND used = 0
                ORDER BY id DESC LIMIT 1
            """, (email,)).fetchone()

            if row is None:
                return jsonify({"error": "Invalid or expired OTP."}), 400

            if datetime.utcnow() > datetime.fromisoformat(row["expires_at"]):
                return jsonify({"error": "OTP has expired. Request a new OTP."}), 400

            if row["attempts"] >= MAX_OTP_ATTEMPTS:
                return jsonify({"error": "Too many OTP attempts."}), 429

            if not secrets.compare_digest(_hash_otp(otp), row["otp_hash"]):
                connection.execute("""
                    UPDATE password_reset_otps
                    SET attempts = attempts + 1
                    WHERE id = ?
                """, (row["id"],))
                connection.commit()
                return jsonify({"error": "Invalid or expired OTP."}), 400

            connection.execute("""
                UPDATE users
                SET password_hash = ?
                WHERE id = ?
            """, (hash_password(new_password), row["user_id"]))

            connection.execute("""
                UPDATE password_reset_otps
                SET used = 1
                WHERE id = ?
            """, (row["id"],))

            connection.commit()

            return jsonify({
                "message": "Password reset successfully. You can now log in."
            }), 200
        except Exception as error:
            connection.rollback()
            return jsonify({
                "error": "Password reset failed.",
                "message": str(error)
            }), 500
        finally:
            connection.close()
