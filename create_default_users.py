# create_default_users.py

from backend.database import SessionLocal, init_db
from backend.models.user import User, UserRole
from backend.utils.security import get_password_hash


def create_user(db, username: str, email: str, password: str, role: UserRole):
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"User '{username}' already exists (id={existing.id}, role={existing.role})")
        return

    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        full_name=username.capitalize(),
        role=role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"Created user '{username}' (id={user.id}, role={user.role})")


def main():
    # make sure tables exist
    init_db()

    db = SessionLocal()
    try:
        # default credentials shown on your login page
        create_user(db, "admin", "admin@example.com", "admin123", UserRole.ADMIN)
        create_user(db, "operator", "operator@example.com", "operator123", UserRole.OPERATOR)
    finally:
        db.close()


if __name__ == "__main__":
    main()

