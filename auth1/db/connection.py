from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import create_engine, Index
from sqlalchemy.orm import sessionmaker, Session
from auth1.config import settings
from auth1.db.models import Base, OAuthCode, AccessToken


engine = create_engine(
    f"sqlite:///{settings.db_path}",
    connect_args={"check_same_thread": False},
    echo=settings.debug
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        Index("idx_code_expires", OAuthCode.expires_at).create(conn, checkfirst=True)
        Index("idx_token_expires", AccessToken.expires_at).create(conn, checkfirst=True)


@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def cleanup_expired():
    with get_db() as db:
        now = datetime.utcnow()
        db.query(OAuthCode).filter(OAuthCode.expires_at < now).delete()
        db.query(AccessToken).filter(AccessToken.expires_at < now).delete()
        db.commit()
