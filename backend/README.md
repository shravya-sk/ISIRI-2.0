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
```bash
copy .env.example .env
```

## Running the Server

Start the development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

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
