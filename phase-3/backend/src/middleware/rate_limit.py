"""T038: Chat-specific rate limiter.

Extends Phase II rate limiting with endpoint-specific configuration
for the chat endpoint (10 msg/min per user).
"""

import time
from collections import defaultdict


class ChatRateLimiter:
    """Simple in-memory sliding window rate limiter for chat messages.

    Args:
        max_requests: Maximum messages allowed per window.
        window_seconds: Time window in seconds.
    """

    def __init__(self, max_requests: int = 10, window_seconds: int = 60) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, user_id: str) -> bool:
        """Check if the user is within rate limits.

        Args:
            user_id: The user making the request.

        Returns:
            True if the request is allowed, False if rate limited.
        """
        now = time.monotonic()
        window_start = now - self.window_seconds

        # Clean old entries
        self._requests[user_id] = [
            t for t in self._requests[user_id] if t > window_start
        ]

        if len(self._requests[user_id]) >= self.max_requests:
            return False

        self._requests[user_id].append(now)
        return True

    def get_retry_after(self, user_id: str) -> int:
        """Get seconds until the user can send another message.

        Args:
            user_id: The user to check.

        Returns:
            Seconds to wait before retrying.
        """
        if not self._requests.get(user_id):
            return 0

        now = time.monotonic()
        oldest_in_window = min(self._requests[user_id])
        retry_after = int(self.window_seconds - (now - oldest_in_window)) + 1
        return max(0, retry_after)


# Global chat rate limiter instance
chat_rate_limiter = ChatRateLimiter(
    max_requests=10,
    window_seconds=60,
)
