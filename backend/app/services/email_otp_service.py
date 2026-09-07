from datetime import datetime, timedelta, timezone
from hashlib import sha256
from random import randint

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_otp import EmailOTP
from app.models.user import User


class EmailOTPService:
    OTP_EXPIRY_MINUTES = 10
    MAX_ATTEMPTS = 5

    @staticmethod
    def _generate_otp() -> str:
        return f"{randint(0, 999999):06d}"

    @staticmethod
    def _hash_otp(otp: str) -> str:
        return sha256(otp.encode()).hexdigest()

    @staticmethod
    async def generate_register_otp(
        db: AsyncSession,
        user: User,
    ) -> None:
        """
        Generate a fresh email verification OTP.
        Development mode prints OTP to terminal.
        """

        # Remove previous unused OTPs.
        await db.execute(
            delete(EmailOTP).where(
                EmailOTP.user_id == user.id,
                EmailOTP.purpose == "REGISTER",
                EmailOTP.verified_at.is_(None),
            )
        )

        otp = EmailOTPService._generate_otp()

        record = EmailOTP(
            user_id=user.id,
            email=user.email,
            otp_hash=EmailOTPService._hash_otp(otp),
            purpose="REGISTER",
            attempts=0,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=EmailOTPService.OTP_EXPIRY_MINUTES),
        )

        db.add(record)
        await db.commit()

        print("\n" + "=" * 60)
        print(" BitNova DEV EMAIL OTP")
        print(f" Email   : {user.email}")
        print(f" OTP     : {otp}")
        print(
            f" Expires : {EmailOTPService.OTP_EXPIRY_MINUTES} minutes"
        )
        print("=" * 60 + "\n")

    @staticmethod
    async def verify_register_otp(
        db: AsyncSession,
        *,
        email: str,
        otp: str,
    ) -> User:

        result = await db.execute(
            select(EmailOTP)
            .where(
                EmailOTP.email == email.lower(),
                EmailOTP.purpose == "REGISTER",
                EmailOTP.verified_at.is_(None),
            )
            .order_by(EmailOTP.created_at.desc())
        )

        record = result.scalar_one_or_none()

        if record is None:
            raise ValueError("OTP not found.")

        if record.expires_at < datetime.now(timezone.utc):
            raise ValueError("OTP has expired.")

        if record.attempts >= EmailOTPService.MAX_ATTEMPTS:
            raise ValueError("Maximum OTP attempts exceeded.")

        record.attempts += 1

        if record.otp_hash != EmailOTPService._hash_otp(otp):
            await db.commit()
            raise ValueError("Invalid OTP.")

        record.verified_at = datetime.now(timezone.utc)

        user = await db.get(User, record.user_id)

        if user:
            user.is_verified = True

        await db.commit()

        return user

    @staticmethod
    async def resend_register_otp(
        db: AsyncSession,
        *,
        email: str,
    ) -> None:

        result = await db.execute(
            select(User).where(User.email == email.lower())
        )

        user = result.scalar_one_or_none()

        if user is None:
            raise ValueError("User not found.")

        if user.is_verified:
            raise ValueError("Email already verified.")

        await EmailOTPService.generate_register_otp(db, user)