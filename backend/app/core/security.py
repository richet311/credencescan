from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Shared rate limiter, keyed by client IP. Applied per-route via @limiter.limit(...).
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.rate_limit_default])
