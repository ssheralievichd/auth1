FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
COPY auth1 auth1/
COPY static static/
COPY web.py .
COPY .env .

RUN pip install --no-cache-dir -e .

RUN sqlite3 auth.db < /dev/null

EXPOSE 13000

CMD ["uvicorn", "web:app", "--host", "0.0.0.0", "--port", "13000"]
