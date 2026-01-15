from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    secret_key: str
    mailcow_url: str
    db_path: str = "auth.db"
    port: int = 5000
    debug: bool = False
    session_token_name: str = "session_token"
    index_redirect_url: str = "/docs"


settings = Settings()
