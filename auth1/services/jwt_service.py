import jwt
from datetime import datetime, timedelta
from typing import Optional
from auth1.config import settings


class JWTService:
    @staticmethod
    def create_session_token(email: str, expires_hours: int = 24) -> str:
        payload = {
            "email": email,
            "exp": datetime.utcnow() + timedelta(hours=expires_hours),
            "iat": datetime.utcnow(),
            "type": "session"
        }
        return jwt.encode(payload, settings.secret_key, algorithm="HS256")

    @staticmethod
    def decode_session_token(token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
            if payload.get("type") != "session":
                return None
            return payload.get("email")
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
