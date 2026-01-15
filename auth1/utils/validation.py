from typing import Dict
from urllib.parse import urlparse


def validate_redirect_uri(app: Dict, redirect_uri: str) -> bool:
    try:
        parsed = urlparse(redirect_uri)
        redirect_host = parsed.netloc

        if not redirect_host:
            return False

        allowed_hosts = app["allowed_hosts"].split(",")
        for allowed_host in allowed_hosts:
            if redirect_host == allowed_host.strip():
                return True

        return False
    except Exception:
        return False
