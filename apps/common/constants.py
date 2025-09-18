"""Project-wide constants used across models, views, tasks and admin."""

# Pagination
DEFAULT_PAGE_SIZE: int = 5
MAX_PAGE_SIZE: int = 100

# Throttling
THROTTLE_RATE_ANON: str = "20/min"
THROTTLE_RATE_USER: str = "120/min"
