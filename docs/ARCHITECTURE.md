# Infinite Story Web - Architecture

## Overview

Infinite Story Web is a collaborative, procedurally-generated storytelling platform. The application generates an infinite, evolving narrative that responds to user interactions and allows multiple users to merge their storylines together.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────┐  │
│  │   index.html  │  │   style.css   │  │      main.js      │  │
│  │  (Structure)  │  │   (Styling)   │  │  (Interactions)   │  │
│  └───────────────┘  └───────────────┘  └───────────────────┘  │
│                              │                                  │
│              HTTP/REST API   │   WebSocket                      │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│                         Backend                                 │
│  ┌───────────────────────────┴───────────────────────────────┐ │
│  │                    Flask Server (server.py)                │ │
│  │  ┌─────────────────┐  ┌─────────────────────────────────┐ │ │
│  │  │   REST API      │  │      WebSocket (Socket.IO)      │ │ │
│  │  │   Endpoints     │  │      Real-time Events           │ │ │
│  │  └─────────────────┘  └─────────────────────────────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│  ┌───────────────────────────┴───────────────────────────────┐ │
│  │              Story Generator (story_generator.py)          │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐   │ │
│  │  │   Moods     │  │   Genres    │  │ Context Manager │   │ │
│  │  └─────────────┘  └─────────────┘  └─────────────────┘   │ │
│  └───────────────────────────────────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│                        Database Layer                           │
│  ┌───────────────────────────┴───────────────────────────────┐ │
│  │              DatabaseManager (models.py)                   │ │
│  │  ┌─────────┐ ┌──────────────┐ ┌───────────┐ ┌──────────┐ │ │
│  │  │  Users  │ │StorySegments │ │Interactions│ │  Merges  │ │ │
│  │  └─────────┘ └──────────────┘ └───────────┘ └──────────┘ │ │
│  └───────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                    ┌─────────┴─────────┐                       │
│                    │   SQLite / SQL    │                       │
│                    │     Database      │                       │
│                    └───────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer

#### index.html
- Main application structure
- Story display container with infinite scroll support
- Control panel for genre/mood selection
- Merge panel for collaborative features
- Interaction hint display

#### style.css
- Dark theme with CSS variables for theming
- Responsive design with mobile support
- Animations (fade-in, typewriter effect)
- Story segment highlighting for merged content

#### main.js
- Session management and API communication
- Event handling (scroll, click, keypress)
- WebSocket connection for real-time updates
- Debounced interaction processing
- Story segment rendering with animations

### Backend Layer

#### server.py (Flask Application)

**REST API Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/session` | POST | Create new session |
| `/api/session/<id>` | GET | Get session info |
| `/api/story/start` | POST | Start new story |
| `/api/story/continue` | POST | Generate next segment |
| `/api/story/<session_id>` | GET | Get full story |
| `/api/story/mood` | POST | Set story mood |
| `/api/story/genre` | POST | Set story genre |
| `/api/users/active` | GET | List active users |
| `/api/merge/request` | POST | Request merge |
| `/api/merge/pending/<id>` | GET | Get pending merges |
| `/api/merge/accept` | POST | Accept merge |
| `/api/interactions/<id>` | GET | Get interaction history |

**WebSocket Events:**

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | Client→Server | Establish connection |
| `join_story` | Client→Server | Join story room |
| `leave_story` | Client→Server | Leave story room |
| `interaction` | Client→Server | Send interaction |
| `story_update` | Server→Client | Broadcast story update |
| `merge_request` | Server→Client | Notify of merge request |

#### story_generator.py

**Classes:**

- `Mood` (Enum): Story mood types
  - MYSTERIOUS, ADVENTUROUS, DARK, WHIMSICAL, ROMANTIC, SUSPENSEFUL, PHILOSOPHICAL

- `Genre` (Enum): Story genre types
  - FANTASY, SCIFI, HORROR, ROMANCE, ADVENTURE, MYSTERY

- `StoryContext` (Dataclass): Current story state
  - current_mood, genre, characters, locations, themes
  - tension_level, story_length, recent_events

- `StoryGenerator`: Main generation engine
  - `generate_opening()`: Create story opening
  - `generate_segment()`: Generate next segment
  - `merge_storylines()`: Combine story segments
  - `set_mood()`, `set_genre()`: Control narrative

**Generation Algorithm:**

1. Apply interaction influence (scroll, click, keypress)
2. Select transition phrase
3. Apply tension modifier based on level
4. Choose character and action for current mood
5. Optionally add location context
6. Potentially introduce new elements
7. Evolve context naturally

### Database Layer

#### models.py

**Tables:**

1. **Users**
   - `id` (UUID): Primary key
   - `session_id`: Unique session identifier
   - `created_at`, `last_active`: Timestamps

2. **StorySegments**
   - `id` (UUID): Primary key
   - `user_id`: Foreign key to Users
   - `content`: Segment text
   - `sequence_number`: Order in story
   - `parent_id`: For story branching
   - `is_merged`, `merged_from`: Merge tracking

3. **Interactions**
   - `id` (UUID): Primary key
   - `user_id`: Foreign key to Users
   - `interaction_type`: scroll, click, keypress
   - `data`: JSON interaction details
   - `timestamp`: When interaction occurred

4. **MergeRequests**
   - `id` (UUID): Primary key
   - `source_user_id`, `target_user_id`: Participants
   - `source_segment_id`: Segment to merge
   - `status`: pending, accepted, rejected
   - `created_at`, `resolved_at`: Timestamps

**DatabaseManager Methods:**

- User operations: create, get, update activity, get active, delete
- Story operations: create segment, get segments, get latest, get full story
- Interaction operations: record, get recent, get counts
- Merge operations: create request, get pending, resolve

## Data Flow

### Story Generation Flow

```
User Interaction (scroll/click/keypress)
         │
         ▼
    main.js captures event
         │
         ▼
    Debounce (500ms)
         │
         ▼
    POST /api/story/continue
         │
         ▼
    server.py receives request
         │
         ▼
    Record interaction in DB
         │
         ▼
    StoryGenerator.generate_segment()
         │
         ├── Apply interaction influence
         ├── Build segment from templates
         └── Evolve context
         │
         ▼
    Save segment to DB
         │
         ▼
    Return segment + context
         │
         ▼
    main.js appends with animation
```

### Merge Flow

```
User A                              User B
   │                                   │
   ├── POST /merge/request ──────────►│
   │                                   │
   │                     WebSocket: merge_request
   │                                   │
   │                         User sees notification
   │                                   │
   │◄────────── POST /merge/accept ────┤
   │                                   │
   ├── Merged segment created ─────────┤
   │                                   │
   ▼                                   ▼
Both stories now contain merged content
```

## Security Considerations

1. **Session Management**: UUID-based sessions, no authentication required
2. **Input Validation**: All API inputs validated before processing
3. **CORS**: Configured for cross-origin requests
4. **SQL Injection**: Using SQLAlchemy ORM with parameterized queries
5. **XSS Prevention**: Content rendered as text, not HTML

## Scalability

### Current Design (Single Server)
- SQLite database
- In-memory story generators per session
- Single Flask process with WebSocket

### Future Scaling Options
1. **Database**: Migrate to PostgreSQL for multi-server
2. **Session State**: Use Redis for generator state
3. **WebSocket**: Use Redis pub/sub for multi-server events
4. **Load Balancing**: Sticky sessions for WebSocket connections

## Performance Optimizations

1. **Debouncing**: Client-side debounce prevents excessive API calls
2. **Pagination**: Story segments fetched in pages
3. **Lazy Loading**: New segments generated on scroll
4. **Connection Pooling**: SQLAlchemy connection management
5. **Caching**: Story generators cached per session

## Testing Strategy

### Unit Tests
- `test_story_generator.py`: Generator logic, moods, genres
- `test_database.py`: CRUD operations, model methods
- `test_server.py`: API endpoints, error handling

### Coverage Target
- Minimum 75% code coverage
- Focus on critical paths: generation, persistence, API

### CI/CD Pipeline
- Linting (flake8, black)
- Multi-Python version testing (3.9-3.12)
- Coverage reporting
- Security scanning (bandit, safety)
