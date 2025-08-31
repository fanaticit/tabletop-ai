# 🎲 Tabletop Rules API - FastAPI Backend

A modern **dual AI-powered** FastAPI backend for tabletop game rules management with intelligent query capabilities. Supports both **OpenAI GPT-4o-mini** and **Anthropic Claude 3.5 Sonnet** with seamless provider switching.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- MongoDB Atlas account
- **AI Provider API Keys** (configure one or both):
  - OpenAI API key (for GPT-4o-mini)
  - Anthropic API key (for Claude 3.5 Sonnet)

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
Create a `.env` file with dual AI provider support:
```bash
# Database Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=tabletop_rules

# JWT Authentication
SECRET_KEY=your-very-secure-secret-key-change-this-in-production

# AI Provider Configuration - Configure one or both
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4o-mini

# Anthropic Configuration  
ANTHROPIC_API_KEY=sk-ant-your-anthropic-api-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Default AI provider ("openai" or "anthropic")
DEFAULT_AI_PROVIDER=openai

# Environment
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

### ⭐ **Dual AI-Powered Rule Queries**
- **OpenAI GPT-4o-mini** integration ($0.15/$0.60 per 1M tokens)
- **Anthropic Claude 3.5 Sonnet** integration ($3.00/$15.00 per 1M tokens)
- **Provider switching** - Choose your preferred AI or compare both
- **Side-by-side comparison** - Test both providers simultaneously
- Context-aware rule scoring and retrieval
- Intelligent fallback system for AI unavailability
- Comprehensive cost monitoring and token tracking

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
POST /api/chat/query           # AI rule queries (uses default provider)
POST /api/chat/query/enhanced  # Enhanced queries with provider selection
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

## 🤖 Dual AI Provider System

### AI Provider Configuration

The backend supports both OpenAI and Anthropic simultaneously:

**OpenAI GPT-4o-mini:**
- **Cost**: $0.15 input / $0.60 output per 1M tokens
- **Speed**: ~1-2 seconds response time
- **Best for**: Cost-effective queries, quick responses

**Anthropic Claude 3.5 Sonnet:**
- **Cost**: $3.00 input / $15.00 output per 1M tokens
- **Speed**: ~2-3 seconds response time  
- **Best for**: Complex reasoning, detailed explanations

### AI Endpoint Usage

#### Standard Query (Uses Default Provider)
```bash
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do pawns move?",
    "game_system": "chess"
  }'
```

#### Enhanced Query with Provider Selection
```bash
curl -X POST "http://localhost:8000/api/chat/query/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do pawns move?",
    "game_system": "chess",
    "ai_provider": "anthropic"
  }'
```

#### Side-by-Side Provider Comparison
```bash
curl -X POST "http://localhost:8000/api/chat/query/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is checkmate?",
    "game_system": "chess",
    "compare_providers": true
  }'
```

### AI Monitoring Endpoints
```bash
GET  /api/chat/ai-usage           # Combined usage statistics
GET  /api/chat/ai-test            # Test legacy OpenAI service
GET  /api/chat/ai-test/multi      # Test both AI providers
GET  /api/chat/ai-test/multi?provider=anthropic  # Test specific provider
```

### Testing AI Integration

Run the included test script to verify both providers:
```bash
# Test both AI providers with sample queries
python test_dual_ai.py
```

This script will:
- Test connections to both providers
- Compare response quality side-by-side
- Show performance metrics and costs
- Demonstrate all API usage patterns

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

# Query rules (standard endpoint)
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do pawns move?", "game_system": "chess"}'

# Query with specific AI provider
curl -X POST "http://localhost:8000/api/chat/query/enhanced" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do pawns move?", "game_system": "chess", "ai_provider": "anthropic"}'
```

### Dual AI Testing Script
```bash
# Run comprehensive dual AI provider testing
python test_dual_ai.py

# This will:
# - Test connections to both AI providers
# - Compare response quality side-by-side  
# - Show performance metrics and costs
# - Demonstrate all API usage patterns
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
│   ├── config.py             # Settings management (dual AI support)
│   ├── database.py           # MongoDB connection
│   ├── models.py             # Pydantic models
│   ├── routes/
│   │   ├── admin.py          # Admin endpoints
│   │   ├── chat.py           # AI chat endpoints (dual AI support)
│   │   └── games.py          # Game endpoints
│   └── services/
│       ├── ai_chat_service.py # Legacy OpenAI GPT integration
│       ├── multi_ai_service.py # Dual AI provider service
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
- `SECRET_KEY`: JWT signing secret
- **AI Provider Settings:**
  - `OPENAI_API_KEY`: OpenAI API key for GPT-4o-mini
  - `ANTHROPIC_API_KEY`: Anthropic API key for Claude 3.5 Sonnet
  - `DEFAULT_AI_PROVIDER`: Default provider (`openai` or `anthropic`)
  - `OPENAI_MODEL`: OpenAI model name (default: `gpt-4o-mini`)
  - `ANTHROPIC_MODEL`: Anthropic model name (default: `claude-3-5-sonnet-20241022`)
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
- Custom metrics for AI usage and costs (both providers)

### AI Usage Monitoring
```bash
# Get combined usage statistics
curl http://localhost:8000/api/chat/ai-usage

# Test both AI providers
curl http://localhost:8000/api/chat/ai-test/multi
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass: `pytest tests/`
5. Submit a pull request

## 📜 License

This project is part of the Tabletop Rules Query Service.