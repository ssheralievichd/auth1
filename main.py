#!/usr/bin/env python3
import uvicorn

from auth1.config import settings
from auth1.db.connection import init_db


if __name__ == "__main__":
    init_db()

    uvicorn.run(
        "web:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )
