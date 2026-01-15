from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse, JSONResponse, FileResponse

from auth1.controllers.auth_controller import AuthController
from auth1.types import SigninRequest
from auth1.services.jwt_service import JWTService
from auth1.config import settings


router = APIRouter()


@router.get("/signin")
async def signin_page():
    return FileResponse("static/signin.html")


@router.post("/signin")
async def signin(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    params = SigninRequest(email=email, password=password)

    result, status = await AuthController.signin(params)

    if status == 200:
        session_token = JWTService.create_session_token(result["email"])

        return_url = request.cookies.get("oauth_return", "/")

        response = RedirectResponse(url=return_url, status_code=302)
        response.set_cookie(
            key=settings.session_token_name,
            value=session_token,
            httponly=True,
            samesite="lax",
            max_age=86400
        )
        response.delete_cookie(key="oauth_return")

        return response

    return JSONResponse(content=result, status_code=status)


@router.get("/logout")
async def logout(request: Request, redirect_uri: str = "/"):
    response = RedirectResponse(url=redirect_uri)
    response.delete_cookie(key=settings.session_token_name)
    return response
