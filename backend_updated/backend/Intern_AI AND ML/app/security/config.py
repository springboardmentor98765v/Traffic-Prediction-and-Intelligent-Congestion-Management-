import os
from dotenv import load_dotenv

load_dotenv()

# Centralized security configuration. The service must not start with a known key.
SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY environment variable is required")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
