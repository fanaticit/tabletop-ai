# AI-Powered Tabletop Game Rules Query Service - Complete Project Documentation

## 🎯 Project Overview

Building a modern AI-powered service where tabletop game players can ask natural language questions about game rules and get accurate, context-aware responses. Think "ChatGPT for board game rules" with semantic search, conversational context, and game-specific knowledge.

**Current Status**: Foundation complete with working auth, game management, and rule upload. **Next Priority**: Implement chat interface using existing backend text search, then enhance with AI capabilities.

## 🏗️ Architecture & Technology Stack

### Backend: FastAPI + MongoDB Atlas + AI Integration
- **Framework**: FastAPI with async support and automatic OpenAPI docs
- **Database**: MongoDB Atlas with unified vector search capabilities  
- **AI Integration**: OpenAI GPT-4o-mini (free tier), Anthropic Claude 4 (premium)
- **Authentication**: JWT-based with admin system
- **File Processing**: Markdown parsing with frontmatter metadata

### Frontend: React + TypeScript + Modern State Management
- **Framework**: React 18 with TypeScript and strict typing
- **State Management**: Zustand (client state) + React Query v5 (server state)
- **Routing**: React Router v6 with protected routes
- **Testing**: Jest + React Testing Library with TDD workflow
- **UI**: Currently minimal HTML/CSS, ready for UI framework integration

### Infrastructure & Deployment
- **Development**: Railway (backend) + Netlify (frontend) + MongoDB Atlas
- **Production**: Scalable to AWS/GCP with containerized deployment
- **Monitoring**: FastAPI built-in metrics + MongoDB Atlas monitoring
- **Cost**: $0-15/month development, $85-105/month early production

## ✅ Current Working Features

### Backend (FastAPI) - OPERATIONAL
- **✅ Authentication System**: JWT login with admin/secret default credentials
- **✅ Dynamic Games Registry**: Automatic game registration from markdown frontmatter
- **✅ Rule Upload System**: Markdown file processing with metadata extraction
- **✅ Basic Search**: Text/regex-based rule queries (works without AI)
- **✅ Database Integration**: MongoDB Atlas with proper error handling
- **✅ API Documentation**: Interactive docs at `/docs` endpoint

**Working API Endpoints**:
```bash
POST /token                                    # Authentication
GET  /api/games/                              # List all games
GET  /api/games/{game_id}                     # Game details  
POST /api/admin/upload/markdown-simple       # Upload rules
POST /api/chat/query                          # Query rules (text search)
```

### Frontend (React) - FULLY OPERATIONAL  
- **✅ Authentication Flow**: Login/registration forms with validation
- **✅ Game Selection**: Complete game picker with filtering and persistence
- **✅ Chat Interface**: Full conversational UI with message history and rule search
- **✅ State Management**: Zustand + React Query integration working perfectly
- **✅ Test Infrastructure**: 57 passing tests with comprehensive coverage
- **✅ API Integration**: React Query configured for backend communication
- **✅ Complete User Flow**: Login → Game Selection → Working Chat Interface

**Test Status**:
```bash
npm test
# ✅ 57 tests passing across 6 suites:
# - ConversationStore: 8 tests (state management, message handling)
# - MessageInput: 16 tests (form handling, user interactions)
# - MessageList: 15 tests (message display, sources, scrolling)
# - ChatInterface: 4 tests (integration, game selection)
# - Auth: 7 tests (LoginForm, RegistrationForm)
# - Games: 7 tests (GameSelector, loading, error states)
```

## ⚠️ Known Issues & Current Priorities

### ✅ COMPLETED: Chat Interface Implementation
**Status**: ✅ Fully implemented and working
**Achievement**: Complete conversational UI with:
- ✅ ConversationStore - Message state management with persistence
- ✅ MessageInput - Form handling with API integration (Enter key, validation)
- ✅ MessageList - Conversation history with sources and timestamps
- ✅ ChatInterface - Full integration with backend `/api/chat/query`
- ✅ 43 comprehensive tests covering all chat functionality

### 🔥 HIGH PRIORITY: Fix OpenAI Integration  
**Problem**: Version conflict between openai==1.35.0 and httpx
```
Error: AsyncClient.__init__() got an unexpected keyword argument 'proxies'
```
**Impact**: No AI embeddings, semantic search, or advanced query understanding
**Current Workaround**: Basic text/regex search functional
**Solution**: Update to compatible versions (openai==1.40.0 + httpx==0.27.0)

### 🟡 MEDIUM PRIORITY: Enhanced Features
- User registration backend endpoint (frontend ready)
- Conversation context persistence in MongoDB
- Real-time chat updates with WebSocket
- Enhanced UI styling with modern framework
- Performance optimization and caching

## 📊 Database Schema (MongoDB Atlas)

### Current Collections

**games Collection** - Game metadata and statistics:
```javascript
{
  "game_id": "chess",                    // Unique identifier
  "name": "Chess",                       // Display name  
  "publisher": "FIDE",                   // Publisher
  "version": "Official Rules",           // Edition/version
  "complexity": "medium",                // easy|medium|hard
  "min_players": 2,                      // Player count
  "max_players": 2,
  "rule_count": 3,                       // Uploaded rules
  "categories": ["movement", "capture"], // Auto-populated
  "ai_tags": ["strategy", "board-game"], // AI classification
  "created_at": ISODate("..."),          // Timestamps
  "updated_at": ISODate("...")
}
```

**content_chunks Collection** - Individual game rules:
```javascript
{
  "game_id": "chess",                    // Game reference
  "category_id": "chess_movement",       // Hierarchical category
  "content_type": "rule_text",           // Content classification
  "title": "Pawn Movement",              // Rule title
  "content": "## Rule: Pawn Movement...",// Full markdown content
  "ancestors": ["chess", "chess_rules"], // Tree structure
  "chunk_metadata": {
    "source_file": "chess_rules.md",    // Origin file
    "section_index": 0,                 // Position in file
    "tokens": 150,                      // Token count
    "complexity_score": 0.7,            // AI difficulty rating
    "uploaded_without_ai": true         // Processing method
  },
  "rule_embedding": [0.1, -0.2, ...],   // ⚠️ Vector (missing due to AI issues)
  "created_at": ISODate("...")
}
```

### Future Collections (To Implement)
```javascript
// users - User management
{
  "_id": ObjectId,
  "username": String,
  "email": String, 
  "hashed_password": String,
  "preferences": {
    "selected_game_id": String,
    "theme": String
  },
  "created_at": Date
}

// conversations - Chat sessions
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "game_id": String,
  "created_at": Date,
  "last_message_at": Date,
  "message_count": Number
}

// messages - Chat history
{
  "_id": ObjectId,
  "conversation_id": ObjectId,
  "role": String, // 'user' | 'assistant'
  "content": String,
  "timestamp": Date,
  "sources": [String] // Rule references
}
```

## 🔗 API Contracts

### Working Endpoints (Ready for Frontend)

**Authentication**:
```typescript
POST /token
Content-Type: application/x-www-form-urlencoded  
Body: username=admin&password=secret
Response: { access_token: string, token_type: "bearer" }
```

**Games Management**:
```typescript
GET /api/games/
Response: { games: Game[] }

GET /api/games/{game_id}
Response: Game & { rule_count: number, categories: string[] }

GET /api/games/{game_id}/stats  
Response: { rule_count: number, categories: string[], last_updated: Date }
```

**Rule Queries** (USE THIS FOR CHAT IMPLEMENTATION):
```typescript
POST /api/chat/query
Content-Type: application/json
Body: { 
  query: string,           // "How do pawns move?"
  game_system: string      // "chess" (from gameStore)
}
Response: { 
  results: RuleChunk[],    // Matching rule content
  query: string,           // Echo query
  total_results?: number   // Result count
}

// Example working call:
fetch('/api/chat/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "How do pawns move in chess?", 
    game_system: "chess"
  })
})
```

### Missing Endpoints (To Add Later)
```typescript
POST /api/auth/register  // User registration
POST /api/chat/conversations  // Start conversation  
GET /api/chat/conversations/{id}/messages // Message history
```

## 🧪 Development Workflow

### Environment Setup
```bash
# Backend
cd tabletop-rules-api/
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn main:app --reload  # Starts on http://localhost:8000

# Frontend
cd tabletop-rules-frontend/  
npm install
npm start                  # Starts on http://localhost:3000

# Testing
npm test                   # Frontend tests (17 passing)
npm test -- --watch       # TDD watch mode
```

### Configuration Files
**Backend (.env)**:
```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=tabletop_rules
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your-jwt-secret-key
ENVIRONMENT=development
```

**Frontend (.env.local)**:
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000  
REACT_APP_ENV=development
```

### Working Dependencies
**Backend (requirements.txt)**:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
motor==3.3.2                    # MongoDB async driver
pymongo==4.6.0
python-jose[cryptography]==3.3.0  # JWT auth
python-frontmatter==1.0.0       # Markdown parsing
openai==1.35.0                   # ⚠️ Version conflict with httpx
httpx==0.25.2                    # ⚠️ Needs compatible version
```

**Frontend (package.json)**:
```json
{
  "@tanstack/react-query": "^5.8.4",  // Server state management
  "zustand": "^4.4.7",                // Client state management
  "react-router-dom": "^6.20.1",      // Routing
  "jwt-decode": "^4.0.0",             // Token parsing  
  "typescript": "^4.9.5",             // TypeScript
  "react": "^18.2.0"                  // React
}
```

## 📁 Project Structure

```
project-root/
├── tabletop-rules-api/              # FastAPI Backend
│   ├── main.py                      # ✅ App entry with all routes
│   ├── requirements.txt             # ✅ Working dependencies
│   ├── .env                         # MongoDB, OpenAI, JWT config
│   ├── app/
│   │   ├── config.py               # ✅ Settings management
│   │   ├── database.py             # ✅ MongoDB connection
│   │   ├── models.py               # ✅ Pydantic models
│   │   ├── routes/
│   │   │   ├── chat.py             # ✅ Query endpoints
│   │   │   ├── games.py            # ✅ Game management
│   │   │   └── admin.py            # ✅ Upload/admin routes
│   │   └── services/
│   │       ├── ai_service.py       # ⚠️ OpenAI (version conflict)
│   │       ├── upload_service.py   # ⚠️ Depends on AI service
│   │       └── auth_service.py     # ✅ JWT authentication
│   └── rules_data/
│       └── chess_rules.md          # ✅ Sample game data
│
├── tabletop-rules-frontend/         # React Frontend  
│   ├── package.json                # ✅ Dependencies configured
│   ├── .env.local                  # API URL configuration
│   ├── src/
│   │   ├── App.tsx                 # ✅ Main app with routing
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   │   ├── LoginForm.tsx   # ✅ Working login
│   │   │   │   └── RegistrationForm.tsx # ✅ Working registration
│   │   │   ├── games/
│   │   │   │   └── GameSelector.tsx # ✅ Working game selection
│   │   │   └── chat/
│   │   │       ├── ChatInterface.tsx    # ⚠️ Placeholder
│   │   │       ├── MessageInput.tsx     # ⚠️ Placeholder  
│   │   │       └── MessageList.tsx      # ⚠️ Placeholder
│   │   ├── stores/
│   │   │   ├── authStore.ts        # ✅ JWT state management
│   │   │   ├── gameStore.ts        # ✅ Game selection
│   │   │   └── conversationStore.ts # ⚠️ Not implemented
│   │   ├── __tests__/
│   │   │   ├── auth.test.tsx       # ✅ 7 tests passing
│   │   │   ├── games.test.tsx      # ✅ 7 tests passing
│   │   │   └── chat.test.tsx       # ✅ 3 placeholder tests
│   │   └── test-utils.tsx          # ✅ Test providers setup
│   └── README.md
│
└── PROJECT-DOCS.md                  # This comprehensive guide
```

## 🚀 IMMEDIATE NEXT STEPS

### Phase 1: Complete Chat Interface (THIS WEEK)

**Goal**: Users can have conversations about game rules using existing backend

#### Step 1: ConversationStore Implementation
Create `src/stores/conversationStore.ts`:
- Message interface with user/assistant roles
- Zustand store with persistence  
- Actions: addMessage, clearMessages, setLoading
- Integration with gameStore for context

#### Step 2: MessageInput Component  
Create `src/components/chat/MessageInput.tsx`:
- Form handling with controlled input
- API integration calling `POST /api/chat/query`
- Loading states and error display
- Submit on Enter key + button click
- Clear input after sending

#### Step 3: MessageList Component
Create `src/components/chat/MessageList.tsx`:
- Display user and assistant messages
- Different styling for message types
- Auto-scroll to bottom on new messages
- Timestamp display and loading indicators

#### Step 4: ChatInterface Integration
Create `src/components/chat/ChatInterface.tsx`:
- Combine MessageList + MessageInput
- Handle API calls and state updates
- Game context display and switching
- Empty states and error boundaries

#### Step 5: Replace Chat Placeholder  
Update App.tsx routing:
- Use real ChatInterface component
- Authentication guard (redirect to login)
- Game selection guard (redirect to game picker)

#### Step 6: Write Tests (TDD Approach)
Following existing test patterns:
- ConversationStore state management tests
- MessageInput form and API integration tests  
- MessageList rendering and interaction tests
- ChatInterface full workflow tests

**Expected Outcome**: Complete user flow working:
**Login → Game Selection → Functional Chat Interface**

### Phase 2: Fix AI Integration (NEXT WEEK)

#### Backend AI Enhancement
1. **Resolve OpenAI Version Conflicts**:
   ```bash
   pip uninstall openai httpx
   pip install openai==1.40.0 httpx==0.27.0
   ```

2. **Enable Vector Embeddings**:
   - Generate embeddings for existing rules
   - Add vector search to MongoDB Atlas
   - Enhance query endpoint with semantic search

3. **Improve Response Quality**:
   - Add context-aware prompts
   - Include rule sources in responses
   - Handle follow-up questions

### Phase 3: Production Features (MONTH 2)

#### User Management System
- User registration backend endpoint
- User authentication frontend
- Personal conversation history
- User preferences and settings

#### Enhanced Chat Features  
- Conversation persistence in MongoDB
- Real-time updates with WebSocket
- Multiple conversation threads
- Rule bookmarking and favorites

#### UI/UX Improvements
- Modern UI framework (Tailwind CSS/Chakra UI)
- Responsive design for mobile
- Dark/light mode toggle
- Better loading states and animations

## 🧪 Testing & Quality Assurance

### Current Test Status
```bash
npm test
# ✅ Test Suites: 6 passed
# ✅ Tests:       57 passed  
# ✅ Snapshots:   0 total
# ✅ Time:        ~4s
```

**Comprehensive Test Coverage:**
- **ConversationStore** (8 tests): State management, message handling, game filtering
- **MessageInput** (16 tests): Form handling, user interactions, validation, loading states
- **MessageList** (15 tests): Message display, styling, sources, timestamps, scrolling
- **ChatInterface** (4 tests): Integration tests, game selection, UI rendering
- **Auth** (7 tests): Login/registration forms with validation (existing)
- **Games** (7 tests): Game selection, filtering, error states (existing)

### Test Implementation Pattern
```typescript
// Example test structure following existing pattern
describe('MessageInput', () => {
  it('should send message on Enter key', async () => {
    render(<MessageInput onSendMessage={mockSendMessage} isLoading={false} />);
    
    const input = screen.getByPlaceholderText('Ask a question about the rules...');
    await user.type(input, 'How do pawns move?{Enter}');
    
    expect(mockSendMessage).toHaveBeenCalledWith('How do pawns move?');
    expect(input).toHaveValue(''); // Should clear after sending
  });
});

describe('ConversationStore', () => {
  it('should add messages with generated ID and timestamp', () => {
    const { result } = renderHook(() => useConversationStore());
    
    act(() => {
      result.current.addMessage({
        role: 'user',
        content: 'Test message',
        gameId: 'chess',
      });
    });

    expect(result.current.messages).toHaveLength(1);
    expect(result.current.messages[0]).toEqual({
      id: 'test-uuid-123',
      role: 'user',
      content: 'Test message',
      gameId: 'chess',
      timestamp: expect.any(Date),
    });
  });
});
```

## 💰 Business Model & Scaling

### Revenue Tiers
- **Free Tier**: 100 queries/month, OpenAI API, basic games (Chess, Catan)
- **Premium**: $9.99/month, 1000 queries, Claude API, all games including complex ones
- **Pro**: Unlimited usage-based billing at $0.02/query

### Cost Structure (Current)
- **Development**: $0-15/month (MongoDB Atlas M0 + Netlify free + Railway free)
- **Early Production**: $85-105/month (MongoDB M10 + Railway Pro + Cloudflare)
- **AI Costs**: Pass-through with small markup

### Scaling Architecture
- **Horizontal**: MongoDB sharding for 1TB+ datasets
- **Performance**: Redis caching + CDN for static content
- **Reliability**: Multi-region deployment with load balancing

## 🔐 Security & Compliance

### Current Security Measures
- JWT authentication with secure secret keys
- MongoDB Atlas network security and encryption
- Environment variable configuration
- Input validation with Pydantic models

### Production Requirements
- HTTPS enforcement with SSL certificates
- Rate limiting and DDoS protection
- User data encryption at rest and in transit  
- GDPR compliance with user data controls
- Regular security audits and updates

## 📈 Success Metrics & KPIs

### Technical Metrics
- **Response Time**: Target <200ms cached, <2s AI-generated
- **Accuracy**: 85%+ rule query accuracy with AI
- **Availability**: 99.9% uptime target
- **Test Coverage**: Maintain >80% code coverage

### Business Metrics  
- **User Retention**: 60%+ after first session
- **Conversion**: 10%+ free to paid conversion
- **Query Success**: 90%+ user satisfaction with responses
- **Growth**: 20%+ monthly active user growth

## 🔧 Common Development Commands

```bash
# Health checks
curl http://localhost:8000/health                    # Backend health
curl http://localhost:3000                           # Frontend health

# Authentication testing
curl -X POST "http://localhost:8000/token" \
  -d "username=admin&password=secret"                # Get JWT token

# Rule upload testing  
TOKEN="your-jwt-token"
curl -X POST "http://localhost:8000/api/admin/upload/markdown-simple" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@rules_data/chess_rules.md"              # Upload rules

# Chat testing
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "pawn movement", "game_system": "chess"}'

# Development workflow
npm test -- --watch                                 # TDD mode
npm test -- --coverage                              # Coverage report
npm start                                           # Dev server
```

## 🎯 Project Status Summary

### ✅ SOLID FOUNDATION COMPLETE
- Authentication system working
- Game management operational  
- Rule upload and basic search functional
- Test infrastructure established
- Database schema implemented
- API documentation available

### 🔥 IMMEDIATE PRIORITIES  
1. **Chat Interface Implementation** - Core user functionality
2. **OpenAI Integration Fix** - Enable AI-powered search
3. **User Registration** - Complete authentication system

### 🚀 READY FOR RAPID DEVELOPMENT
- All infrastructure in place
- Clear implementation plan
- Working development environment
- Comprehensive documentation
- Test-driven workflow established

**This project is positioned for successful completion with working core features and a clear path to AI enhancement and production deployment.**
