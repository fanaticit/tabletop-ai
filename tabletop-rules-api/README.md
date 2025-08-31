# 🎲 Tabletop Rules API - FastAPI Backend

A modern AI-powered FastAPI backend for tabletop game rules management with intelligent query capabilities.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MongoDB Atlas account
- OpenAI API key (optional, for AI features)

### Installation
```bash
# Clone and navigate
cd tabletop-rules-api/

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your MongoDB URI and OpenAI API key
```

### Environment Configuration
Create a `.env` file with:
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=tabletop_rules
OPENAI_API_KEY=sk-your-openai-key-here
SECRET_KEY=your-jwt-secret-key-here
ENVIRONMENT=development
```

### Run the Server
```bash
# Development server with auto-reload
uvicorn main:app --reload

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`
Interactive API docs: `http://localhost:8000/docs`

## 🎯 Core Features

### ✅ AI-Powered Rule Queries
- GPT-4o-mini integration for intelligent responses
- Context-aware rule scoring and retrieval
- Fallback system for AI unavailability
- Cost monitoring and token tracking

### ✅ Content Management
- Markdown file processing with frontmatter
- Automatic game registration
- Rule chunking and categorization
- Batch upload capabilities

### ✅ Authentication & Security
- JWT-based authentication
- Admin user management
- Secure API endpoints
- Input validation with Pydantic

## 🛠️ CLI Content Management

### Setup CLI Tool
```bash
# Install CLI dependencies
python setup_cli.py

# Or install manually
pip install -r cli_requirements.txt
```

### CLI Commands
```bash
# Check backend status
python tabletop_cli.py status

# Upload game rules
python tabletop_cli.py upload rules_data/chess_rules.md

# List all games
python tabletop_cli.py list-games --verbose

# Show rules for a specific game
python tabletop_cli.py show-rules chess

# Validate game integrity
python tabletop_cli.py validate chess

# Batch upload multiple files
python tabletop_cli.py batch-upload rules_data/ --pattern "*.md"

# Delete a game
python tabletop_cli.py delete chess --force

# Show CLI configuration
python tabletop_cli.py config
```

For detailed CLI usage, see `CLI_README.md`.

## 🔗 API Endpoints

### Authentication
```bash
POST /token                    # Get JWT token
```

### Public Endpoints
```bash
GET  /health                   # Health check
GET  /api/games/               # List games
GET  /api/games/{game_id}      # Game details
POST /api/chat/query           # AI rule queries
```

### Admin Endpoints (Requires Authentication)
```bash
# Game Management
GET    /api/admin/games/                     # List games (detailed)
GET    /api/admin/games/{game_id}/rules      # Get game rules
POST   /api/admin/games/{game_id}/validate   # Validate integrity
DELETE /api/admin/games/{game_id}            # Delete game

# Rule Management  
PUT    /api/admin/rules/{rule_id}            # Update rule
DELETE /api/admin/rules/{rule_id}            # Delete rule

# File Upload
POST   /api/admin/upload/markdown-simple     # Upload single file
POST   /api/admin/batch/upload               # Batch upload

# Debug
POST   /api/admin/debug/parse-markdown       # Parse without storing
```

## 📄 Markdown File Format

Rules files should follow this structure:
```markdown
---
game_id: "chess"
name: "Chess"
publisher: "FIDE"
version: "Official Rules"
description: "Classic strategy board game"
complexity: "medium"
min_players: 2
max_players: 2
ai_tags: ["strategy", "board-game"]
---

# Chess Rules

## Pawn Movement
Pawns move forward one square at a time...

## Piece Capture
Pieces capture diagonally...
```

## 🧪 Testing

### Run Backend Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ai_chat_service.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Manual API Testing
```bash
# Get authentication token
TOKEN=$(curl -X POST "http://localhost:8000/token" \
  -d "username=admin&password=secret" | jq -r '.access_token')

# Upload a file
curl -X POST "http://localhost:8000/api/admin/upload/markdown-simple" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@rules_data/chess_rules.md"

# Query rules
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do pawns move?", "game_system": "chess"}'
```

## 🗃️ Database Schema

### Games Collection
```javascript
{
  "game_id": "chess",
  "name": "Chess",
  "publisher": "FIDE",
  "version": "Official Rules",
  "complexity": "medium",
  "min_players": 2,
  "max_players": 2,
  "rule_count": 15,
  "categories": ["movement", "capture"],
  "ai_tags": ["strategy", "board-game"],
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Content Chunks Collection
```javascript
{
  "game_id": "chess",
  "category_id": "chess_movement",
  "content_type": "rule_text",
  "title": "Pawn Movement",
  "content": "## Pawn Movement\nPawns move...",
  "ancestors": ["chess", "chess_rules"],
  "chunk_metadata": {
    "source_file": "chess_rules.md",
    "section_index": 0,
    "tokens": 150,
    "uploaded_without_ai": true
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 🔧 Development

### Project Structure
```
tabletop-rules-api/
├── main.py                    # FastAPI application entry
├── requirements.txt           # Python dependencies
├── cli_requirements.txt       # CLI-specific dependencies
├── tabletop_cli.py           # CLI tool
├── setup_cli.py              # CLI setup script
├── CLI_README.md             # CLI documentation
├── app/
│   ├── config.py             # Settings management
│   ├── database.py           # MongoDB connection
│   ├── models.py             # Pydantic models
│   ├── routes/
│   │   ├── admin.py          # Admin endpoints
│   │   ├── chat.py           # AI chat endpoints
│   │   └── games.py          # Game endpoints
│   └── services/
│       ├── ai_chat_service.py # GPT integration
│       ├── auth_service.py    # JWT authentication
│       └── upload_service.py  # File processing
├── rules_data/               # Sample game files
├── tests/                    # Test files
└── .env                      # Environment variables
```

### Adding New Endpoints
1. Define Pydantic models in `app/models.py`
2. Add route handlers in appropriate `app/routes/` file
3. Update authentication if needed in `app/services/auth_service.py`
4. Add tests in `tests/`

### Environment Variables
- `MONGODB_URI`: MongoDB connection string
- `DATABASE_NAME`: Database name (default: `tabletop_rules`)
- `OPENAI_API_KEY`: OpenAI API key for AI features
- `SECRET_KEY`: JWT signing secret
- `ENVIRONMENT`: `development` or `production`

## 🚀 Deployment

### Local Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
```bash
# Using Gunicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Docker (if Dockerfile exists)
docker build -t tabletop-api .
docker run -p 8000:8000 tabletop-api
```

### Environment Setup for Deployment
- Set `ENVIRONMENT=production`
- Use strong `SECRET_KEY`
- Configure production MongoDB URI
- Set up proper logging
- Enable HTTPS in production

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### API Documentation
- Interactive docs: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Logs
- Application logs via Python logging
- MongoDB Atlas monitoring
- Custom metrics for AI usage and costs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/`
5. Submit a pull request

## 📜 License

This project is part of the Tabletop Rules Query Service.