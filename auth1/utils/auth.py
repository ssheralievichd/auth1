from typing import Optional
from fastapi import Request
from auth1.services.jwt_service import JWTService
from auth1.config import settings


def get_user_email_from_request(request: Request) -> Optional[str]:
    token = request.cookies.get(settings.session_token_name)
    if not token:
        return None
    return JWTService.decode_session_token(token)
