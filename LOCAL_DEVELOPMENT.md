# Local Development Guide

## Running the FastAPI Application Locally

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Copy `.env.local.example` to `.env` and fill in your values:

```bash
cp .env.local.example .env
```

### 3. Run the Application

#### Using Uvicorn (Recommended)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Using Python directly

```bash
python -m uvicorn app.main:app --reload
```

### 4. Access the Application

- **API Root**: http://localhost:8000/
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### 5. Test Endpoints

#### Test Health Endpoint

```bash
curl http://localhost:8000/health
```

#### Test Bot Info

```bash
curl http://localhost:8000/bot-info
```

#### Test Webhook (simulate Telegram update)

```bash
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456789,
    "message": {
      "message_id": 1,
      "from": {
        "id": 123456789,
        "is_bot": false,
        "first_name": "Test"
      },
      "chat": {
        "id": 123456789,
        "type": "private"
      },
      "date": 1234567890,
      "text": "/start"
    }
  }'
```

### 6. Interactive API Documentation

Visit http://localhost:8000/docs to:
- View all available endpoints
- Test endpoints directly from the browser
- See request/response schemas
- View detailed API documentation

## Development Features

### Hot Reload

The `--reload` flag enables auto-restart when code changes are detected.

### Debug Mode

Set `LOG_LEVEL=DEBUG` in `.env` for verbose logging:

```bash
LOG_LEVEL=DEBUG
```

### CORS

CORS is enabled for all origins in development. Customize in `app/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Customize for your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Project Structure

```
telegram-bot/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── bot/                 # Bot handlers
│   ├── services/            # Business logic
│   ├── database/            # Models and DB
│   └── utils/               # Utilities
├── api/
│   └── index.py             # Vercel entry point
├── requirements.txt         # Dependencies
└── vercel.json             # Vercel config
```

## Testing with Telegram

To test with actual Telegram:

1. Set your webhook to local ngrok URL:

```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000

# Set webhook
python scripts/setup_webhook.py set --url https://your-ngrok-url.ngrok.io/webhook
```

2. Send messages to your bot on Telegram

3. Watch logs in terminal

## Common Commands

```bash
# Start development server
uvicorn app.main:app --reload

# Start with custom port
uvicorn app.main:app --reload --port 3000

# Check installed packages
pip list

# Generate requirements
pip freeze > requirements.txt

# Run linter
ruff check app/

# Format code
black app/
```

## Troubleshooting

### Bot Not Initializing

- Check `TELEGRAM_BOT_TOKEN` in `.env`
- Verify token with: `curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe`

### Supabase Connection Failed

- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY`
- Check network connectivity

### Import Errors

- Ensure you're in the project root directory
- Reinstall dependencies: `pip install -r requirements.txt`

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```
