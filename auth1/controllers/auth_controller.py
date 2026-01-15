from auth1.types import SigninRequest
from auth1.services.mailcow_provider import MailcowAuthProvider


class AuthController:
    @staticmethod
    async def signin(params: SigninRequest):
        if not params.email or not params.password:
            return {"error": "missing_credentials"}, 400

        if not await MailcowAuthProvider.authenticate(params.email, params.password):
            return {"error": "invalid_credentials"}, 401

        return {"email": params.email}, 200
