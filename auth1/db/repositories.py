import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from auth1.db.connection import get_db
from auth1.db.models import Application, OAuthCode, AccessToken
from auth1.utils.validation import validate_redirect_uri


class ApplicationRepository:
    @staticmethod
    def get_by_client_id(client_id: str) -> Optional[Dict]:
        with get_db() as db:
            app = db.query(Application).filter(Application.client_id == client_id).first()
            if not app:
                return None
            return {
                "client_id": app.client_id,
                "client_secret": app.client_secret,
                "name": app.name,
                "allowed_hosts": app.allowed_hosts,
                "created_at": app.created_at
            }

    @staticmethod
    def create(name: str, allowed_hosts: str) -> Dict:
        client_id = secrets.token_urlsafe(16)
        client_secret = secrets.token_urlsafe(32)

        with get_db() as db:
            app = Application(
                client_id=client_id,
                client_secret=client_secret,
                name=name,
                allowed_hosts=allowed_hosts
            )
            db.add(app)
            db.commit()
            db.refresh(app)

        return {
            "client_id": client_id,
            "client_secret": client_secret,
            "name": name,
            "allowed_hosts": allowed_hosts
        }

    @staticmethod
    def list_all() -> List[Dict]:
        with get_db() as db:
            apps = db.query(Application).all()
            return [
                {
                    "client_id": app.client_id,
                    "name": app.name,
                    "allowed_hosts": app.allowed_hosts
                }
                for app in apps
            ]



class OAuthCodeRepository:
    @staticmethod
    def create(client_id: str, user_email: str, redirect_uri: str, scope: str) -> str:
        code = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        with get_db() as db:
            oauth_code = OAuthCode(
                code=code,
                client_id=client_id,
                user_email=user_email,
                redirect_uri=redirect_uri,
                scope=scope,
                expires_at=expires_at
            )
            db.add(oauth_code)
            db.commit()

        return code

    @staticmethod
    def get_by_code(code: str) -> Optional[Dict]:
        with get_db() as db:
            oauth_code = db.query(OAuthCode).filter(OAuthCode.code == code).first()

            if not oauth_code:
                return None

            if oauth_code.expires_at < datetime.utcnow():
                return None

            return {
                "code": oauth_code.code,
                "client_id": oauth_code.client_id,
                "user_email": oauth_code.user_email,
                "redirect_uri": oauth_code.redirect_uri,
                "scope": oauth_code.scope,
                "expires_at": oauth_code.expires_at
            }

    @staticmethod
    def delete(code: str):
        with get_db() as db:
            db.query(OAuthCode).filter(OAuthCode.code == code).delete()
            db.commit()


class AccessTokenRepository:
    @staticmethod
    def create(client_id: str, user_email: str, scope: str) -> Dict:
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        with get_db() as db:
            access_token = AccessToken(
                token=token,
                client_id=client_id,
                user_email=user_email,
                scope=scope,
                expires_at=expires_at
            )
            db.add(access_token)
            db.commit()

        return {
            "token": token,
            "expires_at": expires_at
        }

    @staticmethod
    def get_by_token(token: str) -> Optional[Dict]:
        with get_db() as db:
            access_token = db.query(AccessToken).filter(AccessToken.token == token).first()

            if not access_token:
                return None

            if access_token.expires_at < datetime.utcnow():
                return None

            return {
                "token": access_token.token,
                "client_id": access_token.client_id,
                "user_email": access_token.user_email,
                "scope": access_token.scope,
                "expires_at": access_token.expires_at
            }
