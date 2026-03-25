import os

RENDER_API_KEY = os.getenv("RENDER_API_KEY", "")
RENDER_API_BASE = os.getenv("RENDER_API_BASE", "").rstrip("/")

MAX_ACTIVE_JOBS = int(os.getenv("MAX_ACTIVE_JOBS", "10"))
LAUNCH_TIMEOUT_SEC = int(os.getenv("LAUNCH_TIMEOUT_SEC", "20"))

MIN_PROFIT_USD = float(os.getenv("MIN_PROFIT_USD", "0.50"))
PROFIT_MULTIPLIER = float(os.getenv("PROFIT_MULTIPLIER", "2.0"))
