import jwt
from datetime import datetime, timedelta

# In a real production app, this secret key would be hidden in a .env file!
SECRET_KEY = "trafficvision-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict) -> str:
    """Generates a new JWT access token with an expiration time."""
    to_encode = data.copy()
    
    # Set the token to expire in 60 minutes
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Create and return the encoded token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt