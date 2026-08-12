from sqlalchemy import create_engine, text
from passlib.context import CryptContext

DATABASE_URL = "postgresql+psycopg://bitnova:bitnova_password@localhost:5440/bitnova"

pwd_context = CryptContext(
    schemes=["argon2", "bcrypt"],
    deprecated="auto",
)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    row = conn.execute(
        text("""
            SELECT password_hash
            FROM users
            WHERE email = 'user1@example.com'
        """)
    ).first()

password_hash = row[0]

print("Hash prefix:", password_hash[:12])
print("Hash length:", len(password_hash))

password = input("Enter user1 password: ")

try:
    print("Password valid:", pwd_context.verify(password, password_hash))
except Exception as exc:
    print("Verification error:", type(exc).__name__, str(exc))