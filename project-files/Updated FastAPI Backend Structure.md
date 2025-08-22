# FastAPI Backend Structure - Updated Implementation Status

## Current Working Project Structure

```
tabletop-rules-api/
├── requirements.txt                    # Updated with auth & markdown dependencies
├── .env                               # MongoDB URI, OpenAI API key, SECRET_KEY
├── main.py                            # FastAPI app with auth, games, chat, admin routes
├── test_openai.py                     # OpenAI connection test script
├── rules_data/
│   └── chess_rules.md                 # Sample chess rules with proper frontmatter
├── app/
│   ├── __init__.py
│   ├── config.py                      # Settings with extra='ignore' for compatibility
│   ├── database.py                    # MongoDB connection with error handling
│   ├── models.py                      # Pydantic models (fixed for v2 compatibility)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py                    # ✅ Query routes with regex search (working)
│   │   ├── games.py                   # ✅ Dynamic games registry (working)
│   │   └── admin.py                   # ✅ Upload & admin routes (working)
│   └── services/
│       ├── __init__.py
│       ├── ai_service.py              # ⚠️ OpenAI integration (version conflicts)
│       ├── upload_service.py          # ⚠️ Full markdown service (depends on AI)
│       └── auth_service.py            # ✅ JWT authentication (working)
└── tests/ (not implemented yet)
```

## ✅ WORKING FEATURES

### 1. Authentication System
- **JWT token-based auth**: Default admin/secret login
- **Admin-protected endpoints**: Upload, game management  
- **Token endpoint**: `POST /token`
- **Bearer token authentication**: All admin routes protected

### 2. Dynamic Games Registry
- **Automatic game registration**: From markdown frontmatter
- **Games API**: `GET /api/games/` - Lists all uploaded games
- **Game details**: `GET /api/games/{game_id}` - Individual game info
- **Game stats**: `GET /api/games/{game_id}/stats` - Rule counts, categories

### 3. Markdown Upload System (Without AI)
- **Simple upload**: `POST /api/admin/upload/markdown-simple`
- **Frontmatter parsing**: Extracts game_id, metadata
- **Rule chunking**: Splits by ## headers automatically
- **Database storage**: Stores in content_chunks collection
- **Debug endpoint**: `POST /api/admin/debug/parse-markdown`

### 4. Rule Query System
- **Text search**: `POST /api/chat/query` - Natural language queries
- **Keyword search**: `GET /api/chat/search/{game_id}?q=keyword`
- **Get all rules**: `GET /api/chat/games/{game_id}/rules`
- **Regex-based matching**: No database indexes required

### 5. Database Integration
- **MongoDB Atlas**: Cloud database with proper connection handling
- **Collections**: games, content_chunks
- **Error handling**: Graceful failures, service degradation

## ⚠️ KNOWN ISSUES & LIMITATIONS

### 1. OpenAI Integration (Needs Fixing)
- **Version conflict**: OpenAI 1.35.0 vs httpx 0.28.1 incompatibility
- **Error**: `AsyncClient.__init__() got an unexpected keyword argument 'proxies'`
- **Workaround**: Using upload without AI embeddings
- **Impact**: No semantic search, only text/regex search

### 2. Limited Search Capabilities
- **Basic text search**: Regex-based, case-insensitive
- **No semantic search**: Missing AI embeddings
- **No text index**: Could add MongoDB text index for better performance

## 📊 DATABASE SCHEMA (IMPLEMENTED)

### games Collection
```javascript
{
  "game_id": "chess",                    // Unique identifier
  "name": "Chess",                       // Display name
  "publisher": "FIDE",                   // Publisher info
  "version": "Official Rules",           // Version/edition
  "description": "Classic strategy game", // Description
  "complexity": "medium",                // easy|medium|hard
  "min_players": 2,                      // Minimum players
  "max_players": 2,                      // Maximum players
  "rule_count": 3,                       // Number of uploaded rules
  "categories": [],                      // Rule categories (auto-populated)
  "ai_tags": ["strategy", "board-game"], // AI classification tags
  "created_at": ISODate("..."),          // Creation timestamp
  "updated_at": ISODate("..."),          // Last update timestamp
  "auto_registered": false               // Manual vs auto registration
}
```

### content_chunks Collection
```javascript
{
  "game_id": "chess",                    // References games.game_id
  "category_id": "chess_general",        // Category classification
  "content_type": "rule_text",           // Type of content
  "title": "Pawn Movement",              // Rule title
  "content": "## Rule: Pawn Movement...", // Full markdown content
  "ancestors": ["chess", "chess_rules"], // Hierarchical path
  "chunk_metadata": {
    "source_file": "chess_rules.md",    // Original filename
    "section_index": 0,                 // Position in file
    "uploaded_without_ai": true         // Processing method
  },
  "created_at": ISODate("...")           // Upload timestamp
  // "rule_embedding": [...]             // Vector embedding (missing due to AI issues)
}
```

## 🔗 API ENDPOINTS (CURRENT)

### Public Endpoints
```
GET  /                          # API status and info
GET  /health                    # Health check
GET  /docs                      # Interactive API documentation
POST /token                     # Authentication (username/password → JWT)
```

### Games Endpoints
```
GET  /api/games/                # List all available games
GET  /api/games/{game_id}       # Get specific game details
GET  /api/games/{game_id}/stats # Get game statistics
```

### Chat/Query Endpoints  
```
POST /api/chat/query                    # Natural language rule queries
GET  /api/chat/search/{game_id}?q=term  # Simple keyword search
GET  /api/chat/games/{game_id}/rules    # Get all rules for a game
```

### Admin Endpoints (Require Authentication)
```
POST /api/admin/upload/markdown-simple     # Upload markdown without AI
POST /api/admin/debug/parse-markdown       # Debug markdown parsing
GET  /api/admin/test                       # Test admin authentication
GET  /api/admin/games/registered           # Admin view of games
POST /api/admin/games/register             # Manually register game
DELETE /api/admin/games/{game_id}          # Delete game and rules
GET  /api/admin/test/openai               # Test OpenAI connection (currently broken)
```

## 🔧 CURRENT CONFIGURATION

### requirements.txt (Working Versions)
```
# Core FastAPI
fastapi==0.104.1
uvicorn[standard]==0.24.0
motor==3.3.2
pymongo==4.6.0
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.0.3
python-multipart==0.0.6
httpx==0.25.2

# Authentication (Working)
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1

# Markdown Processing (Working)
python-frontmatter==1.0.0
markdown==3.5.1

# AI Integration (Issues)
openai==1.35.0  # Version conflict with httpx
```

### .env Configuration
```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=tabletop_rules
OPENAI_API_KEY=sk-your-key-here
ENVIRONMENT=development
SECRET_KEY=your-secret-key
```

## 🧪 TESTING WORKFLOW (VERIFIED WORKING)

### 1. Authentication Test
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=secret"
# Response: {"access_token": "...", "token_type": "bearer"}
```

### 2. Upload Chess Rules
```bash
TOKEN="your-token-here"
curl -X POST "http://localhost:8000/api/admin/upload/markdown-simple" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@rules_data/chess_rules.md"
# Response: {"success": true, "game_id": "chess", "rules_stored": 3}
```

### 3. Query Chess Rules
```bash
curl -X POST "http://localhost:8000/api/chat/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "pawn movement", "game_system": "chess"}'
# Response: Rule explanations with content snippets
```

### 4. List Available Games
```bash
curl http://localhost:8000/api/games/
# Response: {"games": [{"game_id": "chess", "rule_count": 3, ...}]}
```

## 🚀 NEXT STEPS / TODO

### High Priority (Foundation)
1. **Fix OpenAI Integration**
   - Resolve httpx/openai version conflict
   - Enable AI embeddings for semantic search
   - Add vector similarity search

2. **Enhance Search Capabilities**
   - Add MongoDB text index for better performance
   - Implement hybrid search (text + semantic when AI fixed)
   - Add search result ranking

3. **Add Frontend Integration**
   - CORS configured for localhost:3000
   - API ready for React frontend
   - Interactive docs available at /docs

### Medium Priority (Features)
4. **Batch Upload System**
   - Multiple file upload
   - Progress tracking
   - Background processing

5. **Enhanced Rule Management**
   - Edit/update existing rules
   - Rule versioning
   - Category management

6. **User Management**
   - Multiple admin users
   - User registration
   - Role-based permissions

### Low Priority (Polish)
7. **Performance Optimization**
   - Query caching
   - Database indexes
   - Response compression

8. **Monitoring & Logging**
   - Error tracking
   - Usage analytics
   - Performance metrics

## 💡 ARCHITECTURE DECISIONS MADE

### ✅ Successful Choices
- **MongoDB Atlas**: Unified storage for games + rules
- **FastAPI**: Excellent docs, async support, validation
- **JWT Authentication**: Simple, stateless admin access
- **Markdown + Frontmatter**: Clean content format
- **Dynamic Games Registry**: No hardcoded game lists

### ⚠️ Need Revisiting  
- **OpenAI Version Management**: Pin compatible versions
- **Search Strategy**: Consider alternatives to OpenAI
- **Error Handling**: Improve user-facing error messages

## 🎯 CURRENT SYSTEM CAPABILITIES

**✅ What Works Right Now:**
- Upload chess rules via Markdown
- Query chess rules with natural language
- Authenticate admin users
- Manage games dynamically
- Interactive API documentation
- MongoDB cloud storage

**⚠️ What Needs OpenAI Fix:**
- Semantic similarity search
- AI embeddings generation
- Advanced query understanding
- Cost-optimized AI responses

**🔮 Ready for Frontend:**
- All CRUD operations available
- RESTful API design
- CORS configured
- Comprehensive error handling
- Interactive testing at /docs

## 📈 PERFORMANCE STATUS

- **Response Times**: <200ms for most queries
- **Database**: MongoDB Atlas M0 (free tier)
- **Concurrent Users**: Tested with single user
- **File Upload**: Up to markdown files (tested with chess rules)
- **Query Accuracy**: Basic text matching (no AI ranking yet)

This implementation provides a solid foundation for a tabletop rules API with room for AI enhancement once the OpenAI version conflicts are resolved.