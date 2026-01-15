from datetime import datetime
from typing import Optional, Tuple, Dict
from auth1.types import AuthorizeRequest, TokenRequest
from auth1.db.connection import cleanup_expired
from auth1.db.repositories import ApplicationRepository, OAuthCodeRepository, AccessTokenRepository
from auth1.services.mailcow_provider import MailcowAuthProvider
from auth1.utils.validation import validate_redirect_uri


class OAuthController:
    @staticmethod
    def authorize(params: AuthorizeRequest, user_email: Optional[str] = None) -> Tuple[Dict, int]:
        cleanup_expired()

        if params.response_type != "code":
            return {"error": "unsupported_response_type"}, 400

        app_data = ApplicationRepository.get_by_client_id(params.client_id)
        if not app_data:
            return {"error": "invalid_client"}, 400

        if not validate_redirect_uri(app_data, params.redirect_uri):
            return {"error": "invalid_redirect_uri"}, 400

        if not user_email:
            if params.prompt == "none":
                return {
                    "redirect": f"{params.redirect_uri}?error=login_required&state={params.state}"
                }, 302

            return {"action": "show_signin"}, 200

        code = OAuthCodeRepository.create(
            params.client_id,
            user_email,
            params.redirect_uri,
            params.scope
        )

        return {
            "redirect": f"{params.redirect_uri}?code={code}&state={params.state}"
        }, 302

    @staticmethod
    def exchange_token(params: TokenRequest) -> Tuple[Dict, int]:
        if params.grant_type != "authorization_code":
            return {"error": "unsupported_grant_type"}, 400

        app_data = ApplicationRepository.get_by_client_id(params.client_id)
        if not app_data or app_data["client_secret"] != params.client_secret:
            return {"error": "invalid_client"}, 401

        oauth_code = OAuthCodeRepository.get_by_code(params.code)
        if not oauth_code:
            return {"error": "invalid_grant"}, 400

        if oauth_code["client_id"] != params.client_id:
            return {"error": "invalid_grant"}, 400

        if oauth_code["redirect_uri"] != params.redirect_uri:
            return {"error": "invalid_grant"}, 400

        OAuthCodeRepository.delete(params.code)

        token_data = AccessTokenRepository.create(
            params.client_id,
            oauth_code["user_email"],
            oauth_code["scope"]
        )

        expires_in = int((token_data["expires_at"] - datetime.utcnow()).total_seconds())

        return {
            "access_token": token_data["token"],
            "token_type": "Bearer",
            "expires_in": expires_in,
            "scope": oauth_code["scope"]
        }, 200

    @staticmethod
    def get_userinfo(token: str) -> Tuple[Dict, int]:
        access_token = AccessTokenRepository.get_by_token(token)

        if not access_token:
            return {"error": "invalid_token"}, 401

        return MailcowAuthProvider.get_user_info(access_token["user_email"]), 200
