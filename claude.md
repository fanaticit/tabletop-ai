# Claude Code Project Documentation: AI-Powered Tabletop Game Rules Query Service

## 🎯 Project Vision
Building a modern AI-powered service where tabletop game players can ask natural language questions about game rules and get accurate, context-aware responses. Think "ChatGPT for board game rules" with semantic search and conversational context.

## 🏗️ Current Architecture

### Backend: FastAPI + MongoDB Atlas
- **API Framework**: FastAPI with async support
- **Database**: MongoDB Atlas with vector search capabilities
- **AI Integration**: OpenAI GPT-4 (with version conflicts to fix)
- **Authentication**: JWT-based admin system
- **Status**: Core functionality working, AI integration needs fixing

### Frontend: React + TypeScript
- **Framework**: React 18 with TypeScript
- **State Management**: Zustand (client) + React Query (server state)
- **Routing**: React Router v6
- **Testing**: Jest + React Testing Library (17 tests passing)
- **Status**: Auth + game selection working, chat interface needs implementation

## 🔧 Technology Stack

### Dependencies (Working Versions)
```json
// Backend (requirements.txt)
"fastapi==0.104.1"
"motor==3.3.2"           // MongoDB async driver
"python-jose==3.3.0"     // JWT authentication
"openai==1.35.0"          // ⚠️ Version conflict with httpx
"python-frontmatter==1.0.0" // Markdown parsing

// Frontend (package.json)  
"@tanstack/react-query": "^5.8.4"  // Server state
"zustand": "^4.4.7"                 // Client state
"react-router-dom": "^6.20.1"       // Routing
"jwt-decode": "^4.0.0"              // Token parsing
```

### Development Environment
```bash
# Backend
cd tabletop-rules-api/
source venv/bin/activate
uvicorn main:app --reload  # Port 8000

# Frontend  
cd tabletop-rules-frontend/
npm start                  # Port 3000

# Database
MongoDB Atlas cloud instance (connection in .env)
```

## ✅ Current Working Features

### Backend (FastAPI)
- **Authentication**: JWT login with admin/secret default
- **Game Management**: Dynamic game registration from markdown uploads
- **Rule Upload**: Markdown file processing with frontmatter parsing
- **Basic Search**: Text/regex-based rule queries (no AI embeddings yet)
- **API Endpoints**: 
  - `POST /token` - Authentication
  - `GET /api/games/` - List games
  - `POST /api/admin/upload/markdown-simple` - Upload rules
  - `POST /api/chat/query` - Basic rule queries

### Frontend (React)
- **Authentication Forms**: Login/registration UI with validation
- **Game Selection**: Complete game picker with filtering
- **State Management**: Zustand stores + React Query integration
- **Test Suite**: 17 passing tests with TDD workflow
- **API Integration**: React Query configured for backend calls

## ⚠️ Known Issues & Next Steps

### HIGH PRIORITY - Fix OpenAI Integration
**Problem**: Version conflict between openai==1.35.0 and httpx
```
AsyncClient.__init__() got an unexpected keyword argument 'proxies'
```
**Impact**: No semantic search, only basic text matching
**Solution**: Fix dependency versions, enable AI embeddings

### HIGH PRIORITY - Implement Chat Interface
**Current State**: Placeholder components only
**Needed**: 
- `ChatInterface.tsx` - Main chat container
- `MessageInput.tsx` - User input with form handling  
- `MessageList.tsx` - Message history display
- `conversationStore.ts` - Chat state management

### MEDIUM PRIORITY - Enhanced Features
- User registration backend endpoint
- Conversation context persistence
- Real-time chat with WebSocket
- Better UI/styling framework

## 📊 Database Schema (MongoDB)

### Collections Structure
```javascript
// games - Game metadata
{
  "game_id": "chess",
  "name": "Chess", 
  "publisher": "FIDE",
  "rule_count": 3,
  "categories": ["movement", "capture"],
  "created_at": ISODate("...")
}

// content_chunks - Individual rules
{
  "game_id": "chess",
  "category_id": "chess_movement", 
  "content_type": "rule_text",
  "title": "Pawn Movement",
  "content": "## Rule: Pawn Movement\nPawns move...",
  "rule_embedding": [0.1, -0.2, ...], // ⚠️ Missing due to AI issues
  "chunk_metadata": {
    "source_file": "chess_rules.md",
    "uploaded_without_ai": true
  }
}

// Future: users, conversations, messages collections
```

## 🧪 Development Workflow

### Test-Driven Development (TDD)
```bash
# Frontend testing
npm test                    # Run all tests (17 passing)
npm test -- --watch        # TDD watch mode
npm test -- auth.test.tsx   # Specific test file

# Backend testing  
pytest                      # (Not implemented yet)
```

### File Upload Testing
```bash
# Test markdown upload
curl -X POST "http://localhost:8000/api/admin/upload/markdown-simple" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@rules_data/chess_rules.md"
```

## 📁 Project Structure

```
project-root/
├── tabletop-rules-api/          # FastAPI Backend
│   ├── main.py                  # ✅ FastAPI app with routes
│   ├── app/
│   │   ├── models.py           # ✅ Pydantic models  
│   │   ├── database.py         # ✅ MongoDB connection
│   │   ├── routes/
│   │   │   ├── chat.py         # ✅ Query endpoints
│   │   │   ├── games.py        # ✅ Game management
│   │   │   └── admin.py        # ✅ Upload endpoints
│   │   └── services/
│   │       ├── ai_service.py   # ⚠️ OpenAI integration (broken)
│   │       └── upload_service.py # ⚠️ Depends on AI service
│   └── rules_data/
│       └── chess_rules.md      # ✅ Sample game data
│
├── tabletop-rules-frontend/     # React Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── auth/           # ✅ Login/Register forms
│   │   │   ├── games/          # ✅ Game selection
│   │   │   └── chat/           # ⚠️ Placeholder components
│   │   ├── stores/
│   │   │   ├── authStore.ts    # ✅ JWT management
│   │   │   ├── gameStore.ts    # ✅ Game selection
│   │   │   └── conversationStore.ts # ⚠️ Not implemented
│   │   └── __tests__/          # ✅ 17 tests passing
│   └── package.json
│
└── claude.md                   # This file
```

## 🔗 API Contract (Current)

### Working Endpoints
```typescript
// Authentication
POST /token
Body: { username: "admin", password: "secret" }
Response: { access_token: string, token_type: "bearer" }

// Games
GET /api/games/
Response: { games: Game[] }

// Chat (Basic)
POST /api/chat/query  
Body: { query: string, game_system: string }
Response: { results: RuleChunk[], query: string }

// Admin (Protected)
POST /api/admin/upload/markdown-simple
Header: Authorization: Bearer <token>
Body: FormData with file
Response: { success: true, game_id: string, rules_stored: number }
```

### Missing Endpoints (To Implement)
```typescript
// User registration
POST /api/auth/register
Body: { username: string, email: string, password: string }

// Enhanced chat with context
POST /api/chat/conversation
Body: { message: string, conversation_id?: string, game_id: string }
Response: { response: string, conversation_id: string, sources: RuleChunk[] }
```

## 🎯 Immediate Development Priorities

### 1. Fix OpenAI Integration (Backend)
- Resolve httpx/openai version conflict
- Enable semantic search with vector embeddings
- Add AI response streaming

### 2. Implement Chat Interface (Frontend)
- Build conversation UI components
- Add message state management
- Integrate with backend chat endpoints

### 3. Add User Registration (Full Stack)
- Backend endpoint for user creation
- Frontend registration flow
- MongoDB users collection

## 🔍 Common Debugging Commands

```bash
# Backend health check
curl http://localhost:8000/health

# Test authentication
curl -X POST "http://localhost:8000/token" \
  -d "username=admin&password=secret"

# Frontend test specific component
npm test -- GameSelector.test.tsx

# Check MongoDB connection
# (View in FastAPI logs when starting server)
```

## 🚀 Success Metrics

### Current Achievements
- ✅ 17 frontend tests passing
- ✅ Basic rule upload and query working  
- ✅ JWT authentication implemented
- ✅ MongoDB Atlas integration working
- ✅ Game management system operational

### Target Goals
- 🎯 AI-powered semantic search operational
- 🎯 Conversational chat interface completed
- 🎯 User registration and management
- 🎯 Sub-200ms query response times
- 🎯 85%+ rule query accuracy with AI

## 💡 Key Architecture Decisions

1. **Unified Database**: MongoDB Atlas for both operational data and vector search
2. **State Separation**: Zustand for client state, React Query for server state
3. **Authentication**: JWT-based with admin tier first, user registration later
4. **AI Strategy**: OpenAI for free tier, Anthropic Claude for premium (future)
5. **Testing**: TDD workflow with Jest, simple mocks over MSW complexity

## 🔐 Environment Configuration

### Required .env Files
```bash
# Backend (.env)
MONGODB_URI=mongodb+srv://...
DATABASE_NAME=tabletop_rules
OPENAI_API_KEY=sk-...
SECRET_KEY=your-jwt-secret
ENVIRONMENT=development

# Frontend (.env.local)  
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_ENV=development
```

This project is at a solid foundation stage with working core features. The main blockers are the OpenAI integration fix and chat interface implementation. All testing infrastructure and basic functionality is operational.