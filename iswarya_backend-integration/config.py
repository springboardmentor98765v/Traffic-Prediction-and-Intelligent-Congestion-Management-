import os
from dotenv import load_dotenv

load_dotenv()

# Centralized security configuration ensuring consistent keys across login and validation
SECRET_KEY = os.getenv("SECRET_KEY", "your-jwt-secret-key-here")
ALGORITHM = os.getenv("ALGORITHM", "HS256")