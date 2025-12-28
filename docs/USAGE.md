# Infinite Story Web - Usage Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Running the Application](#running-the-application)
4. [Using the Application](#using-the-application)
5. [API Reference](#api-reference)
6. [Configuration](#configuration)
7. [Development](#development)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

Infinite Story Web is an interactive storytelling platform that generates procedural narratives based on your interactions. Every scroll, click, and keypress influences the evolving story.

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- A modern web browser

---

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd infinite-plot-twist
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment (Optional)

Copy the example environment file and customize:

```bash
cp .env.example .env
```

Edit `.env` to configure:
- `FLASK_ENV`: Set to `development` or `production`
- `SECRET_KEY`: Change to a secure random string
- `PORT`: Server port (default: 5000)

---

## Running the Application

### Development Mode

```bash
python run.py
```

The server will start on `http://localhost:5000`

### Production Mode

```bash
export FLASK_ENV=production
export FLASK_DEBUG=0
python run.py
```

For production deployment, consider using:
- Gunicorn with eventlet workers
- Nginx as a reverse proxy
- Environment variables for sensitive configuration

---

## Using the Application

### Starting Your Story

1. Open your browser to `http://localhost:5000`
2. Click **"New Story"** to begin your narrative
3. The story will generate an opening based on a random genre and mood

### Interacting with the Story

Your interactions shape the narrative:

| Interaction | Effect |
|-------------|--------|
| **Scroll** | Triggers new story segments; faster scrolling increases tension |
| **Click** | Introduces new elements (characters, locations) |
| **Keypress** | Changes the story mood (see keyboard shortcuts) |

### Keyboard Shortcuts

Press these keys to instantly change the story mood:

| Key | Mood |
|-----|------|
| `M` | Mysterious |
| `A` | Adventurous |
| `D` | Dark |
| `W` | Whimsical |
| `R` | Romantic |
| `S` | Suspenseful |
| `P` | Philosophical |

### Changing Genre and Mood

Use the dropdown menus in the control panel:

- **Genre**: Fantasy, Sci-Fi, Horror, Romance, Adventure, Mystery
- **Mood**: Affects the tone and action types in generated segments

### Story Context Display

The context bar shows:
- **Genre**: Current story genre
- **Mood**: Current narrative mood
- **Tension**: Story tension level (0-100%)
- **Words**: Total word count

### Collaborative Features

#### Finding Other Storylines

1. Click **"Find Storylines"**
2. Browse active users' stories
3. Click **"Merge"** to request a storyline merger

#### Accepting Merge Requests

When someone wants to merge with your story:
1. A notification appears in the bottom-right
2. Click **"Accept"** to merge their content into your story
3. Click **"Reject"** to decline

Merged content appears highlighted in green with a dotted underline.

---

## API Reference

### Session Management

#### Create Session
```http
POST /api/session
```

Response:
```json
{
  "session_id": "uuid-string",
  "user_id": "uuid-string"
}
```

#### Get Session
```http
GET /api/session/{session_id}
```

### Story Operations

#### Start Story
```http
POST /api/story/start
Content-Type: application/json

{
  "session_id": "your-session-id"
}
```

#### Continue Story
```http
POST /api/story/continue
Content-Type: application/json

{
  "session_id": "your-session-id",
  "interaction": {
    "type": "scroll|click|keypress",
    "amount": 100,       // for scroll
    "x": 50, "y": 100,   // for click
    "key": "m"           // for keypress
  }
}
```

#### Get Full Story
```http
GET /api/story/{session_id}?limit=50&offset=0
```

#### Set Mood
```http
POST /api/story/mood
Content-Type: application/json

{
  "session_id": "your-session-id",
  "mood": "mysterious|adventurous|dark|whimsical|romantic|suspenseful|philosophical"
}
```

#### Set Genre
```http
POST /api/story/genre
Content-Type: application/json

{
  "session_id": "your-session-id",
  "genre": "fantasy|scifi|horror|romance|adventure|mystery"
}
```

### Collaboration

#### Get Active Users
```http
GET /api/users/active?minutes=5
```

#### Request Merge
```http
POST /api/merge/request
Content-Type: application/json

{
  "session_id": "your-session-id",
  "target_session_id": "other-session-id"
}
```

#### Get Pending Merges
```http
GET /api/merge/pending/{session_id}
```

#### Accept Merge
```http
POST /api/merge/accept
Content-Type: application/json

{
  "session_id": "your-session-id",
  "request_id": "merge-request-id"
}
```

### Utility

#### Health Check
```http
GET /api/health
```

#### Get Interactions
```http
GET /api/interactions/{session_id}?limit=10
```

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment mode | `development` |
| `FLASK_DEBUG` | Enable debug mode | `1` |
| `SECRET_KEY` | Flask secret key | `dev-secret-key` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `5000` |
| `DATABASE_URL` | Database connection URL | `sqlite:///stories.db` |
| `MAX_STORY_LENGTH` | Maximum story length | `10000` |
| `STORY_SEGMENT_LENGTH` | Target segment length | `150` |

### Database Configuration

Default: SQLite file database (`stories.db`)

For PostgreSQL:
```
DATABASE_URL=postgresql://user:password@localhost/infinite_story
```

---

## Development

### Project Structure

```
infinite-plot-twist/
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── pytest.ini               # Pytest configuration
├── conftest.py              # Test fixtures
├── .env.example             # Environment template
├── .gitignore               # Git ignore patterns
│
├── src/
│   ├── __init__.py
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── server.py        # Flask application
│   │   └── story_generator.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── models.py        # SQLAlchemy models
│   └── frontend/
│       ├── index.html
│       ├── style.css
│       └── main.js
│
├── tests/
│   ├── __init__.py
│   ├── test_story_generator.py
│   ├── test_database.py
│   └── test_server.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── USAGE.md
│   └── SUGGESTIONS.md
│
└── .github/
    └── workflows/
        └── ci.yml           # CI/CD pipeline
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_story_generator.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Linting
flake8 src/ tests/

# Formatting
black src/ tests/

# Check formatting without changes
black --check src/ tests/
```

### Adding New Features

1. **New Story Elements**: Add to `CHARACTERS`, `LOCATIONS`, or `ACTIONS` in `story_generator.py`
2. **New Moods/Genres**: Add to `Mood` or `Genre` enums and corresponding templates
3. **New API Endpoints**: Add to `register_routes()` in `server.py`
4. **New Database Models**: Add to `models.py` and run `db.create_tables()`

---

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'src'"

Ensure you're running from the project root:
```bash
cd infinite-plot-twist
python run.py
```

Or add the project to PYTHONPATH:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### "Address already in use"

Another process is using port 5000. Either:
- Kill the existing process
- Change the port: `PORT=5001 python run.py`

#### "WebSocket connection failed"

- Check that the server is running
- Ensure no firewall is blocking WebSocket connections
- Check browser console for detailed errors

#### Database errors

Reset the database:
```bash
rm stories.db
python run.py  # Tables will be recreated
```

### Getting Help

1. Check the [Architecture documentation](ARCHITECTURE.md) for system design
2. Review the [Suggestions documentation](SUGGESTIONS.md) for known limitations
3. Open an issue on GitHub with:
   - Python version
   - Operating system
   - Error message and stack trace
   - Steps to reproduce
