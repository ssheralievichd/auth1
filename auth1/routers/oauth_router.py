from fastapi import APIRouter, Request, Form, Header, Response
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse, HTMLResponse
from typing import Optional
from pathlib import Path

from auth1.controllers.oauth_controller import OAuthController
from auth1.types import AuthorizeRequest, TokenRequest
from auth1.utils.auth import get_user_email_from_request


router = APIRouter()


@router.get("/authorize")
async def authorize(
    request: Request,
    client_id: str,
    redirect_uri: str,
    state: str = "",
    response_type: str = "code",
    scope: str = "read",
    prompt: str = ""
):
    user_email = get_user_email_from_request(request)

    params = AuthorizeRequest(
        client_id=client_id,
        redirect_uri=redirect_uri,
        state=state,
        response_type=response_type,
        scope=scope,
        prompt=prompt
    )

    result, status = OAuthController.authorize(params, user_email)

    if status == 302:
        return RedirectResponse(url=result["redirect"], status_code=302)

    if status == 200 and result.get("action") == "show_signin":
        html_path = Path("static/signin.html")
        html_content = html_path.read_text()

        response = HTMLResponse(content=html_content)
        response.set_cookie(key="oauth_return", value=str(request.url), httponly=True, samesite="lax")
        return response

    return JSONResponse(content=result, status_code=status)


@router.post("/token")
async def token(
    grant_type: str = Form(...),
    code: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    redirect_uri: str = Form(...)
):
    params = TokenRequest(
        grant_type=grant_type,
        code=code,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri
    )

    result, status = OAuthController.exchange_token(params)
    return JSONResponse(content=result, status_code=status)


@router.get("/userinfo")
async def userinfo(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(content={"error": "invalid_token"}, status_code=401)

    token = authorization[7:]
    result, status = OAuthController.get_userinfo(token)
    return JSONResponse(content=result, status_code=status)
