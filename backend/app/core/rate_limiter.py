import time
from collections import defaultdict
from threading import Lock
from app.core.config import settings

class LoginRateLimiter:
    """
    Simple in-memory login rate limiter.

    Intended for a single API instance.

    For a multi-instance production deployment,
    replace this with Redis-backed state.
    """

    def __init__(
        self,
        max_attempts: int,
        window_seconds: int,
    ):
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds

        self._attempts = defaultdict(list)
        self._lock = Lock()

    def check(
        self,
        key: str,
    ) -> tuple[bool, int]:

        now = time.monotonic()

        with self._lock:

            attempts = self._attempts[key]

            # Remove attempts outside the window
            attempts[:] = [
                timestamp
                for timestamp in attempts
                if now - timestamp
                < self.window_seconds
            ]

            if len(attempts) >= self.max_attempts:

                oldest = attempts[0]

                retry_after = max(
                    1,
                    int(
                        self.window_seconds
                        - (now - oldest)
                    ),
                )

                return False, retry_after

            attempts.append(now)

            return True, 0

    def clear(
        self,
        key: str,
    ) -> None:

        with self._lock:
            self._attempts.pop(
                key,
                None,
            )


login_rate_limiter = LoginRateLimiter(
    max_attempts=settings.login_rate_limit_attempts,
    window_seconds=settings.login_rate_limit_window_seconds,
)