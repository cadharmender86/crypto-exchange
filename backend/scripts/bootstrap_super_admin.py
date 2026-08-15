"""Bootstrap the first SUPER_ADMIN account.

Usage:
    python -m scripts.bootstrap_super_admin

The command never accepts a password as a CLI argument. It prompts securely
for the password, hashes it with the application's existing password hasher,
and creates the admin account only if the email does not already exist.
"""

import asyncio
import getpass
import re

from sqlalchemy import select

from app.api.v1.auth import hash_password
from app.core.database import AsyncSessionLocal
from app.models.admin import AdminRole, AdminUser, admin_user_roles


EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
MIN_PASSWORD_LENGTH = 12


async def bootstrap_super_admin() -> None:
    email = input("Super admin email: ").strip().lower()
    full_name = input("Super admin full name: ").strip()

    if not EMAIL_RE.fullmatch(email):
        raise SystemExit("Invalid email address.")

    if not full_name:
        raise SystemExit("Full name is required.")

    password = getpass.getpass("Super admin password: ")
    confirmation = getpass.getpass("Confirm password: ")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise SystemExit(
            f"Password must contain at least {MIN_PASSWORD_LENGTH} characters."
        )

    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    async with AsyncSessionLocal() as db:
        existing = await db.scalar(
            select(AdminUser).where(AdminUser.email == email)
        )
        if existing is not None:
            raise SystemExit("An admin account with this email already exists.")

        role = await db.scalar(
            select(AdminRole).where(AdminRole.name == "SUPER_ADMIN")
        )
        if role is None:
            raise SystemExit(
                "SUPER_ADMIN role is missing. Run 'alembic upgrade head' first."
            )

        admin = AdminUser(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
            is_active=True,
            is_locked=False,
            failed_login_attempts=0,
        )
        db.add(admin)
        await db.flush()

        await db.execute(
            admin_user_roles.insert().values(
                admin_user_id=admin.id,
                role_id=role.id,
            )
        )
        await db.commit()

        print("SUPER_ADMIN created successfully.")
        print(f"Admin ID: {admin.id}")
        print(f"Email: {admin.email}")


if __name__ == "__main__":
    asyncio.run(bootstrap_super_admin())
