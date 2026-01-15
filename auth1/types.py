from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class AuthorizeRequest(BaseModel):
    client_id: str
    redirect_uri: str
    state: str = ""
    response_type: str = "code"
    scope: str = "read"
    prompt: str = ""


class TokenRequest(BaseModel):
    grant_type: str
    code: str
    client_id: str
    client_secret: str
    redirect_uri: str


class SigninRequest(BaseModel):
    email: EmailStr
    password: str


class ApplicationSchema(BaseModel):
    client_id: str
    client_secret: str
    name: str
    allowed_hosts: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OAuthCodeSchema(BaseModel):
    code: str
    client_id: str
    user_email: str
    redirect_uri: str
    scope: Optional[str] = None
    expires_at: datetime
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AccessTokenSchema(BaseModel):
    token: str
    client_id: str
    user_email: str
    scope: Optional[str] = None
    expires_at: datetime
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInfoResponse(BaseModel):
    email: str
    sub: str
    email_verified: bool = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    scope: str
