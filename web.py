from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from auth1.routers import oauth_router, auth_router
from auth1.config import settings


app = FastAPI(title="Auth1", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(oauth_router.router, tags=["OAuth"])
app.include_router(auth_router.router, tags=["Auth"])


@app.get("/")
async def root():
    return RedirectResponse(url=settings.index_redirect_url)


@app.get("/health")
async def health():
    return {"status": "ok"}
