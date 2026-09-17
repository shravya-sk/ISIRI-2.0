# ISIRI 2.0 Backend

FastAPI backend for the Intelligent Speech Interface for Regional Interaction.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # Main FastAPI application
│   ├── api/              # API routes
│   ├── services/         # Business logic
│   ├── models/           # Data models
│   └── core/             # Core configuration
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
└── README.md            # This file
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file from the example:
- Windows:
```bat
copy .env.example .env
```
- Linux/Mac:
```bash
cp .env.example .env
```

Then edit `backend/.env` and set `RPI_HOST` for the door lock — see
`hardware/README.md`.

## Running the Server

Run this **from the repository root**, not from `backend/`:

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

`main.py` uses absolute imports (`from backend.app...`), so `uvicorn app.main:app`
launched inside `backend/` cannot resolve them.

The API will be available at `http://localhost:8000`

On startup the console prints a banner naming the build and the configured
Raspberry Pi address — check it matches what you expect:

```text
==============================================================
ISIRI 2.0 backend  |  build b887447
RPI_HOST           |  127.0.0.1:5000
simulation         |  false
lock route         |  /device/lock/diag
lock route         |  /device/lock/status
lock route         |  /device/lock/{state}
==============================================================
```

### If a route returns `{"detail":"Not Found"}`

That is FastAPI answering, so the server is alive — it is just running **different
code than what is on disk**. Almost always a stale `uvicorn` still holding port
8000 while the new one failed to bind.

```bash
curl http://127.0.0.1:8000/health      # compare "commit" with: git log --oneline -1
```

Windows recovery:
```bat
netstat -ano | findstr :8000
taskkill /PID <pid> /F
```
Kill every PID listed, then start one instance from the repo root and watch the
console for `Application startup complete` with no traceback and no
*"address already in use"*.

## API Documentation

Once the server is running, access:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### GET /
Returns a welcome message.

**Response:**
```json
{
    "message": "Welcome to ISIRI 2.0 Backend"
}
```

## Development

The project follows a clean architecture pattern:
- **api/**: API route definitions
- **services/**: Business logic and service layer
- **models/**: Pydantic models and database schemas
- **core/**: Configuration, security, and shared utilities
