# Auth1

Minimal OAuth2 SSO server with mail server authentication.

## What is This?

OAuth2 authorization server that authenticates users against Mailcow web interface. Provides Single Sign-On for multiple applications without managing user databases.

## How SSO Works

### Traditional Login (Without SSO)
```
User → App A → Login Page → Database Check → Session
User → App B → Login Page → Database Check → Session
User → App C → Login Page → Database Check → Session
```
User must login separately to each application.

### SSO Login (With Auth1)
```
User → App A → Redirect to Auth1 → Login Once → Redirect Back
User → App B → Redirect to Auth1 → Already Logged In → Redirect Back
User → App C → Redirect to Auth1 → Already Logged In → Redirect Back
```
User logs in once, all apps share the authentication.

### The SSO Flow Step-by-Step

1. **User Visits App**: User clicks "Login" on your application
2. **App Redirects**: App redirects user to `auth.example.com/authorize?client_id=myapp`
3. **Check Session**: Auth1 checks if user already logged in (JWT cookie)
4. **Login or Continue**:
   - If not logged in → Show login form
   - If logged in → Skip to step 6
5. **User Authenticates**: User enters email/password, validated against mail server
6. **Create Session**: Auth1 creates JWT token, sets cookie
7. **Generate Code**: Creates one-time authorization code
8. **Redirect Back**: Sends user back to app with code: `app.example.com/callback?code=ABC123`
9. **Exchange Code**: App backend exchanges code for access token
10. **Get User Info**: App uses token to fetch user email from `/userinfo`
11. **Create App Session**: App creates its own session for the user

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    User's Browser                           │
│  - Stores JWT session cookie (httponly, secure)             │
│  - Navigates between apps and auth server                   │
└─────────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   App A      │  │   App B      │  │   App C      │
│              │  │              │  │              │
│ Client ID:   │  │ Client ID:   │  │ Client ID:   │
│   client123  │  │   client456  │  │   client789  │
│              │  │              │  │              │
│ Redirects to │  │ Redirects to │  │ Redirects to │
│ /authorize   │  │ /authorize   │  │ /authorize   │
└──────────────┘  └──────────────┘  └──────────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │   Auth1 Server          │
              │  (auth.example.com)     │
              │                         │
              │  Components:            │
              │  - OAuth Router         │
              │  - Auth Router          │
              │  - JWT Service          │
              │  - SQLite Database      │
              └─────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │  Mailcow Web Interface  │
              │ (mail.example.com)      │
              │                         │
              │  - User Authentication  │
              │  - Source of Truth      │
              └─────────────────────────┘
```

## Installation

```bash
# Install dependencies
uv sync

# Configure
cp .env.example .env
# Edit .env with your SECRET_KEY

# Run
python main.py
```

## Configuration

`.env` file:
```env
# Security
SECRET_KEY=your-secret-key-here-min-32-chars
SESSION_TOKEN_NAME=session_token

# Mailcow
MAILCOW_URL=https://mail.example.com

# Database
DB_PATH=auth.db

# Server
PORT=5000
DEBUG=false
INDEX_REDIRECT_URL=/docs
```

Generate secret key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Managing Applications

### Create Application
```bash
python cli.py create-app myapp app.example.com
```

Save the returned `client_id` and `client_secret`.

**Note**: Provide allowed hostnames (comma-separated for multiple), not full redirect URIs. The server will validate that redirect URIs match the registered hostnames.

**Example with multiple hosts**:
```bash
python cli.py create-app myapp "app.example.com,localhost:3000"
```

### List Applications
```bash
python cli.py list-apps
```

## OAuth2 Flow

### 1. Redirect to Authorization
```
https://auth.example.com/authorize?
  client_id=<your_client_id>
  &redirect_uri=https://yourapp.com/callback
  &response_type=code
  &state=<random_string>
  &scope=read
```

### 2. Exchange Code for Token
```bash
curl -X POST https://auth.example.com/token \
  -d grant_type=authorization_code \
  -d code=<code_from_redirect> \
  -d client_id=<your_client_id> \
  -d client_secret=<your_client_secret> \
  -d redirect_uri=https://yourapp.com/callback
```

Response:
```json
{
  "access_token": "...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "read"
}
```

### 3. Get User Info
```bash
curl https://auth.example.com/userinfo \
  -H "Authorization: Bearer <access_token>"
```

Response:
```json
{
  "email": "user@example.com",
  "sub": "user@example.com",
  "email_verified": true
}
```

## Silent Authentication

Add `prompt=none` parameter to check authentication without showing login page:

```
/authorize?client_id=...&redirect_uri=...&prompt=none
```

If user has session: redirects with code
If no session: redirects with `error=login_required`

## API Endpoints

- `GET /authorize` - Start OAuth flow
- `POST /token` - Exchange code for token
- `GET /userinfo` - Get user email
- `GET /signin` - Login page
- `POST /signin` - Process login
- `GET /logout` - Clear session
- `GET /health` - Health check
- `GET /docs` - API documentation

## Project Structure

```
auth1/
├── config.py              # Settings
├── types.py               # Pydantic schemas
├── controllers/           # Business logic
│   ├── oauth_controller.py
│   └── auth_controller.py
├── routers/               # HTTP endpoints
│   ├── oauth_router.py
│   └── auth_router.py
├── services/              # External integrations
│   ├── jwt_service.py
│   └── mailcow_provider.py
├── utils/                 # Utility functions
│   ├── auth.py           # Auth helpers
│   └── validation.py     # Validation helpers
└── db/                    # Data access
    ├── connection.py
    ├── models.py
    └── repositories.py
```

## Production Deployment

### Using Uvicorn
```bash
uvicorn web:app --host 0.0.0.0 --port 5000 --workers 4
```

### Using Gunicorn
```bash
gunicorn web:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000
```

### Nginx Proxy
```nginx
server {
    listen 443 ssl http2;
    server_name auth.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Security

- JWT tokens signed with HS256
- HttpOnly cookies prevent XSS
- SameSite=Lax for CSRF protection
- No password storage (Mailcow web auth)
- Token expiration: 24h session, 10min codes, 1h access tokens
- Redirect URI validation

## Development

```bash
# Run with auto-reload
DEBUG=true python main.py

# API docs
http://localhost:5000/docs

# Database migrations
alembic upgrade head
alembic revision -m "description"
```

## Troubleshooting

**Login failed**: Check MAILCOW_URL in .env and ensure Mailcow is accessible

**Invalid client**: Run `python cli.py list-apps` to verify client_id

**Invalid redirect URI**: Ensure redirect_uri hostname matches registered allowed hosts

**JWT errors**: Verify SECRET_KEY hasn't changed, clear browser cookies

## Stack

- FastAPI - Web framework
- SQLAlchemy - ORM
- Pydantic - Validation
- PyJWT - Token handling
- SQLite - Database
- Uvicorn - ASGI server
