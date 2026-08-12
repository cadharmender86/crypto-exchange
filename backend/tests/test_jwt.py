import sys

sys.path.insert(0, ".")

from jose import jwt
from app.core.config import settings

token = input("Paste ACCESS TOKEN:").strip()

print("Configured algorithm:", settings.jwt_algorithm)
print("Secret length:", len(settings.jwt_secret_key))

try:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )

    print("JWT VALID")
    print("Subject:", payload.get("sub"))
    print("Type:", payload.get("type"))
    print("Issued at:", payload.get("iat"))
    print("Expires:", payload.get("exp"))

except Exception as exc:
    print("JWT INVALID")
    print("Error:", type(exc).__name__)
    print("Message:", str(exc))
