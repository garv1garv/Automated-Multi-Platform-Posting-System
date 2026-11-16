# Multi-Platform Posting Service

FastAPI service that publishes a short message with a CTA link to multiple platforms:

- Telegram
- Discord
- Reddit
- GitHub
- Mastodon

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

## Installation

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and set your credentials:

```bash
cp .env.example .env
```

If credentials for any platform are omitted, the service will record that platform as failed and continue posting to the others.

## Running the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Interactive API documentation will be available at:
- Swagger UI: http://localhost:4000/docs
- ReDoc: http://localhost:4000/redoc

## API Usage

### Endpoint

`POST http://localhost:4000/posting`

### Request

```json
{
  "message": "Check out our latest business platform and grow your online visibility. https://example.com"
}
```

Validation rules:
- Max 200 characters.
- Exactly one valid CTA link (http/https).

### Example Success Response

```json
{
  "success": true,
  "results": [
    {
      "platform": "Telegram",
      "status": "success",
      "posted_url": "https://t.me/example/123",
      "public_access": true,
      "date": "2026-11-16",
      "time": "16:40:12",
      "error": null
    },
    {
      "platform": "Discord",
      "status": "success",
      "posted_url": "https://discord.com/channels/123/456/789",
      "public_access": true,
      "date": "2026-11-16",
      "time": "16:40:13",
      "error": null
    },
    {
      "platform": "Reddit",
      "status": "success",
      "posted_url": "https://reddit.com/r/test/comments/xyz123",
      "public_access": true,
      "date": "2026-11-16",
      "time": "16:40:14",
      "error": null
    },
    {
      "platform": "GitHub",
      "status": "success",
      "posted_url": "https://gist.github.com/user/71f28b",
      "public_access": true,
      "date": "2026-11-16",
      "time": "16:40:14",
      "error": null
    },
    {
      "platform": "Mastodon",
      "status": "success",
      "posted_url": "https://mastodon.social/@user/1123456789",
      "public_access": true,
      "date": "2026-11-16",
      "time": "16:40:15",
      "error": null
    }
  ]
}
```

### Example Validation Error Response

When sending invalid input (e.g., missing link, >200 chars, or multiple links), the API returns HTTP 422:

```json
{
  "success": false,
  "error": "Validation Error",
  "details": [
    "message: Value error, Message must contain exactly one CTA link. Found 0 links."
  ]
}
```

## Running Tests

```bash
pytest -v
```
