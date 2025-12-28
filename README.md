# Infinite Story Web

An interactive, procedurally-generated storytelling platform where every user interaction shapes an infinite, evolving narrative. Users can collaborate by merging their storylines together, creating unique collaborative fiction.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen.svg)

## Features

- **Infinite Procedural Story Generation**: Stories continue endlessly as you interact
- **Interaction-Driven Narrative**: Scrolls, clicks, and keypresses influence the story
- **Multiple Moods & Genres**: 7 moods and 6 genres for diverse narratives
- **Collaborative Storytelling**: Merge your storyline with other users
- **Real-time Updates**: WebSocket support for live story evolution
- **Typewriter Effects**: Beautiful text animations

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd infinite-plot-twist

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
python run.py
```

Open your browser to `http://localhost:5000`

## How It Works

### Interacting with the Story

| Interaction | Effect |
|-------------|--------|
| **Scroll** | Generates new story segments; speed affects tension |
| **Click** | Introduces new elements to the narrative |
| **Keypress** | Changes story mood instantly |

### Keyboard Shortcuts

| Key | Mood |
|-----|------|
| M | Mysterious |
| A | Adventurous |
| D | Dark |
| W | Whimsical |
| R | Romantic |
| S | Suspenseful |
| P | Philosophical |

### Genres

Fantasy • Sci-Fi • Horror • Romance • Adventure • Mystery

## Project Structure

```
infinite-plot-twist/
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
├── src/
│   ├── backend/
│   │   ├── server.py        # Flask application & API
│   │   └── story_generator.py
│   ├── database/
│   │   └── models.py        # SQLAlchemy models
│   └── frontend/
│       ├── index.html
│       ├── style.css
│       └── main.js
├── tests/                   # Test suite (92% coverage)
├── docs/                    # Documentation
└── .github/workflows/       # CI/CD pipeline
```

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/session` | POST | Create session |
| `/api/story/start` | POST | Start new story |
| `/api/story/continue` | POST | Generate next segment |
| `/api/story/<id>` | GET | Get full story |
| `/api/story/mood` | POST | Set mood |
| `/api/story/genre` | POST | Set genre |
| `/api/merge/request` | POST | Request merge |

See [USAGE.md](docs/USAGE.md) for complete API documentation.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Code Quality

```bash
# Linting
flake8 src/ tests/

# Formatting
black src/ tests/
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and component details
- [Usage Guide](docs/USAGE.md) - Installation, configuration, and API reference
- [Suggestions](docs/SUGGESTIONS.md) - Future improvements and roadmap

## Tech Stack

- **Backend**: Flask, Flask-SocketIO, SQLAlchemy
- **Frontend**: Vanilla JavaScript, CSS3
- **Database**: SQLite (configurable to PostgreSQL)
- **Testing**: pytest, pytest-cov
- **CI/CD**: GitHub Actions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Procedural generation inspired by interactive fiction traditions
- Built with modern web technologies for seamless storytelling
