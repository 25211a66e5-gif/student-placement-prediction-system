from getpass import getpass
from database import get_connection
from auth import hash_password


def main():
    print("CareerPredict Admin Account Setup")
    email = input("Admin email: ").strip().lower()
    first_name = input("First name: ").strip() or "System"
    last_name = input("Last name: ").strip() or "Administrator"
    password = getpass("Admin password: ")
    confirm = getpass("Confirm password: ")

    if not email or not password:
        raise SystemExit("Email and password are required.")
    if password != confirm:
        raise SystemExit("Passwords do not match.")
    if len(password) < 8:
        raise SystemExit("Use a password of at least 8 characters.")

    connection = get_connection()
    try:
        existing = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing:
            connection.execute(
                "UPDATE users SET first_name=?, last_name=?, password_hash=?, role='admin' WHERE id=?",
                (first_name, last_name, hash_password(password), existing["id"])
            )
            print("Existing account promoted to administrator.")
        else:
            connection.execute("""
                INSERT INTO users
                (first_name, last_name, email, phone, college, password_hash, role)
                VALUES (?, ?, ?, '', '', ?, 'admin')
            """, (first_name, last_name, email, hash_password(password)))
            print("Administrator account created.")

        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
