import re
from urllib.parse import unquote_plus
import httpx
from typing import Tuple, Optional, Dict
from auth1.config import settings


class MailcowAuthProvider:
    @staticmethod
    async def authenticate(email: str, password: str) -> bool:
        success, _ = await MailcowAuthProvider._validate_credentials(email, password)
        return success

    @staticmethod
    def get_user_info(email: str) -> Dict:
        return {
            "email": email,
            "sub": email,
            "email_verified": True
        }

    @staticmethod
    async def _validate_credentials(email: str, password: str) -> Tuple[bool, Optional[Dict]]:
        try:
            async with httpx.AsyncClient(follow_redirects=False, timeout=10.0) as client:
                response = await client.post(
                    settings.mailcow_url,
                    data={
                        'login_user': email,
                        'pass_user': password
                    },
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )

                if response.status_code != 302:
                    return False, None

                session_cookie = response.cookies.get('MCSESSID')
                if not session_cookie:
                    return False, None

                user_response = await client.get(
                    f"{settings.mailcow_url}/user",
                    cookies={'MCSESSID': session_cookie}
                )

                if user_response.status_code != 200:
                    return False, None

                html = user_response.text

                match = re.search(r'email=([^&]+)&amp;name=([^&]+)', html)
                if not match:
                    username = email.split('@')[0]
                    display_name = username.replace('.', ' ').replace('_', ' ').title()

                    return True, {
                        'email': email,
                        'username': username,
                        'display_name': display_name
                    }

                full_name = unquote_plus(match.group(2).replace('+', ' '))
                username = email.split('@')[0]

                return True, {
                    'email': email,
                    'username': username,
                    'display_name': full_name
                }

        except Exception as e:
            print(f"Error validating credentials: {e}")
            return False, None
