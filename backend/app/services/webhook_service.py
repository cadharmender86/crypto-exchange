import hashlib
import hmac

from app.core.config import settings


class CashfreeWebhookService:
    @staticmethod
    def verify_signature(
        body: bytes,
        signature: str,
        timestamp: str,
    ) -> bool:
        """
        Verify Cashfree webhook signature.
        """

        signed_payload = timestamp + body.decode("utf-8")

        generated_signature = hmac.new(
            settings.cashfree_secret_key.encode(),
            signed_payload.encode(),
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(
            generated_signature,
            signature,
        )