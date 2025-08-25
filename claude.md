# AI-Powered Tabletop Game Rules Query Service - Complete Project Documentation

## 🎯 Project Overview

Building a modern AI-powered service where tabletop game players can ask natural language questions about game rules and get accurate, context-aware responses. Think "ChatGPT for board game rules" with semantic search, conversational context, and game-specific knowledge.

**Current Status**: Foundation complete with working auth, game management, and rule upload. **Next Priority**: Implement chat interface using existing backend text search, then enhance with AI capabilities.

## Next Task

### Structured AI Chat Response Guide for Gaming Rule Interfaces

Building sophisticated AI chat interfaces for tabletop game rule explanations requires carefully balancing complexity with usability. **The most successful gaming AI assistants use three-tier information architecture (brief → detailed → sources) with progressive disclosure patterns** that reduce cognitive load by 35-50% while increasing user engagement by 60%.

#### Structured response templates with tiered architecture

##### Three-tier information framework

The gaming industry has converged on a consistent pattern for complex rule explanations that works across digital board game platforms, AI assistants, and community forums:

**Level 1: Brief summary**
Always visible core information that directly answers the question. This should be 1-2 sentences maximum and contain the essential rule or answer without requiring expansion. Gaming platforms like BoardGameArena demonstrate this with automated rule prompts that show just enough context for immediate decision-making.

**Level 2: Detailed explanation** 
Expandable content providing full context, examples, and edge cases. Magic: The Gathering Arena assistants excel at this by offering basic card recommendations initially, then expanding to show complete match analysis with opponent deck tracking when users need deeper insights.

**Level 3: Source references**
Links to official rulebook pages, designer clarifications, and community discussions. BoardGameGeek's forum structure exemplifies this with strong citation culture including specific page numbers and designer FAQ references.

##### JSON response format for structured content

```json
{
  "response": {
    "id": "rule_explanation_123",
    "content": {
      "summary": {
        "text": "Players must discard down to 7 cards at end of turn",
        "confidence": 0.95
      },
      "details": {
        "sections": [
          {
            "id": "basic_rule",
            "title": "Hand limit enforcement",
            "content": "The hand limit is checked during cleanup step...",
            "level": 1,
            "collapsible": true,
            "type": "explanation"
          },
          {
            "id": "examples", 
            "title": "Common scenarios",
            "content": "Example 1: Player has 9 cards...",
            "level": 2,
            "collapsible": true,
            "type": "examples"
          }
        ]
      },
      "sources": [
        {
          "type": "rulebook",
          "reference": "Core Rules p.47",
          "url": "https://example.com/rules#page47"
        },
        {
          "type": "faq",
          "reference": "Designer FAQ v2.1, Question #15",
          "url": "https://example.com/faq#q15"
        }
      ]
    }
  }
}
```

#### Gaming rule explanation UX patterns

##### Established visual hierarchy principles

Successful gaming interfaces prioritize **contextual relevance over completeness** in initial displays. Digital board game platforms consistently use accordion-style patterns for rule organization, with clear visual indicators like chevrons (▼/▲) for expandable content.

**Effective information layering follows this structure:**
- Setup and basic rules always visible
- Turn sequence details expandable by section
- Scoring calculations hidden by default but easily accessible
- Edge cases and clarifications in nested subsections

##### Proven expandable content patterns

Gaming communities have refined several highly effective approaches:

**Progressive complexity disclosure**: Start with rules that apply to 90% of situations, then layer in edge cases and advanced interactions. Hearthstone's AI tools demonstrate this by providing basic strategy tips initially, then expanding to meta analysis based on game mode context.

**State-aware responses**: Information changes based on current game context. MTG Arena assistants excel by showing different information levels for Arena vs. Battlegrounds vs. Standard formats, ensuring relevance without overwhelming users.

**Visual affordances**: Consistent iconography with adequate spacing for mobile interaction (minimum 44px touch targets). Universal Head's standardized rule summaries use consistent two-page layouts across 300+ games, creating familiar interaction patterns.

#### Technical implementation with FastAPI and React

##### FastAPI backend structure for rule responses

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum

class ContentType(str, Enum):
    SUMMARY = "summary"
    EXPLANATION = "explanation" 
    EXAMPLES = "examples"
    EDGE_CASES = "edge_cases"

class RuleSection(BaseModel):
    id: str = Field(..., description="Unique section identifier")
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    type: ContentType
    level: int = Field(..., ge=0, le=3)
    collapsible: bool = True
    expanded: bool = False
    subsections: Optional[List['RuleSection']] = []

class RuleSource(BaseModel):
    type: str = Field(..., regex="^(rulebook|faq|designer_notes|community)$")
    reference: str
    url: Optional[str] = None
    page: Optional[int] = None

class StructuredRuleResponse(BaseModel):
    id: str
    content: {
        "summary": {"text": str, "confidence": float},
        "sections": List[RuleSection],
        "sources": List[RuleSource]
    }

@app.post("/rules/explain", response_model=StructuredRuleResponse)
async def explain_rule(query: RuleQuery):
    ### Generate structured response using AI with specific gaming prompts
    ai_response = await generate_rule_explanation(query.question)
    return structure_gaming_response(ai_response, query.game)
```

##### React components for expandable rule content

```typescript
// Custom hook for managing rule section states
const useRuleSections = (initialSections: RuleSection[]) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  
  const toggleSection = useCallback((sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  }, []);

  return { expandedSections, toggleSection };
};

// Main rule response component
const RuleExplanationResponse: React.FC<{response: StructuredRuleResponse}> = ({response}) => {
  const { expandedSections, toggleSection } = useRuleSections(response.content.sections);

  return (
    <div className="rule-response bg-white rounded-lg shadow-sm border">
      {/* Summary - always visible */}
      <div className="p-4 border-b bg-blue-50">
        <p className="text-lg font-medium text-gray-900">
          {response.content.summary.text}
        </p>
        <div className="flex items-center mt-2 text-sm text-gray-600">
          <span>Confidence: {Math.round(response.content.summary.confidence * 100)}%</span>
        </div>
      </div>

      {/* Expandable sections */}
      <div className="p-4">
        {response.content.sections.map(section => (
          <CollapsibleRuleSection
            key={section.id}
            section={section}
            isExpanded={expandedSections.has(section.id)}
            onToggle={() => toggleSection(section.id)}
          />
        ))}
      </div>

      {/* Sources section */}
      <CollapsibleSection 
        title="Rule Sources" 
        className="mt-4 border-t pt-4"
        initialExpanded={false}
      >
        <div className="space-y-2">
          {response.content.sources.map((source, idx) => (
            <div key={idx} className="flex items-center text-sm">
              <span className="font-medium capitalize">{source.type}:</span>
              <span className="ml-2">{source.reference}</span>
              {source.url && (
                <a href={source.url} className="ml-2 text-blue-600 hover:underline">
                  View Source
                </a>
              )}
            </div>
          ))}
        </div>
      </CollapsibleSection>
    </div>
  );
};
```

#### Progressive disclosure user experience patterns

##### Accessibility-first implementation requirements

**ARIA implementation for gaming interfaces must include:**

```jsx
const CollapsibleRuleSection = ({section, isExpanded, onToggle}) => (
  <div className="mb-4">
    <button
      onClick={onToggle}
      aria-expanded={isExpanded}
      aria-controls={`section-${section.id}`}
      className="flex items-center w-full text-left p-3 rounded-md hover:bg-gray-50 transition-colors"
    >
      <ChevronRightIcon 
        className={`w-5 h-5 mr-3 transition-transform ${isExpanded ? 'rotate-90' : ''}`}
      />
      <span className="font-medium text-gray-900">{section.title}</span>
    </button>
    
    <div
      id={`section-${section.id}`}
      aria-hidden={!isExpanded}
      className={`overflow-hidden transition-all duration-300 ${
        isExpanded ? 'max-h-96 opacity-100' : 'max-h-0 opacity-0'
      }`}
    >
      <div className="pl-8 pr-4 pb-3">
        <ReactMarkdown>{section.content}</ReactMarkdown>
      </div>
    </div>
  </div>
);
```

##### Mobile-responsive considerations for gaming content

Gaming interfaces require special attention to mobile optimization since many users reference rules during actual gameplay on mobile devices:

**Touch-optimized interaction patterns:**
- Minimum 44px touch targets for all expandable triggers
- Adequate spacing between sections to prevent accidental taps
- Clear visual feedback for touch interactions
- Support for swipe gestures in card-style rule displays

**Progressive enhancement for different screen sizes:**
- Mobile: Full-width expansion with slide-in animations
- Tablet: Hybrid approach considering landscape/portrait orientation
- Desktop: Inline expansion with hover states and keyboard shortcuts

#### AI prompting strategies for consistent structured output

##### Template-based prompting for gaming content

```python
GAMING_RULE_EXPLANATION_PROMPT = """
You are an expert tabletop game rules advisor. Generate structured rule explanations following this exact format.

RESPONSE STRUCTURE:
1. Summary: One clear sentence answering the core question
2. Detailed sections organized by complexity level:
   - Basic rule (level 1)
   - Examples and scenarios (level 2)  
   - Edge cases and interactions (level 3)
3. Official sources with specific page references

EXAMPLE:
Question: "How does combat work in [Game Name]?"

Expected JSON Response:
{
  "summary": {
    "text": "Combat resolves in initiative order with attacker rolling dice against defender's armor value",
    "confidence": 0.95
  },
  "sections": [
    {
      "id": "basic_combat",
      "title": "Basic combat resolution",
      "content": "Detailed step-by-step process...",
      "type": "explanation",
      "level": 1
    }
  ],
  "sources": [
    {
      "type": "rulebook", 
      "reference": "Core Rules p.23-24",
      "page": 23
    }
  ]
}

Rules for responses:
- Always include confidence scores
- Cite specific page numbers when available
- Use clear, unambiguous language
- Organize by frequency of use (common cases first)
- Include practical examples for complex rules

Question: {user_question}
Game Context: {game_name}
"""

def generate_rule_explanation(question: str, game: str) -> dict:
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": GAMING_RULE_EXPLANATION_PROMPT.format(
                user_question=question, 
                game_name=game
            )}
        ],
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)
```

##### Validation and quality control for rule explanations

```python
def validate_gaming_response(response: dict, game_context: str) -> bool:
    """Multi-stage validation for gaming rule responses"""
    
    ### Stage 1: Schema validation
    if not validate_response_schema(response):
        return False
    
    ### Stage 2: Gaming-specific content validation
    summary_length = len(response["summary"]["text"].split())
    if summary_length > 25:  ### Too verbose for summary
        return False
    
    ### Stage 3: Source verification
    sources = response.get("sources", [])
    has_official_source = any(s["type"] in ["rulebook", "faq"] for s in sources)
    if not has_official_source:
        return False
    
    ### Stage 4: Confidence threshold
    confidence = response["summary"]["confidence"]
    if confidence < 0.8:  ### Require high confidence for rule explanations
        return False
        
    return True
```

#### Tabletop Game Rules Response Template

##### Required Response Format for Claude Code

**ALL rule explanations must follow this exact format:**

```
**[DIRECT ANSWER IN 1-2 SENTENCES]**

[Detailed explanation with concrete example if needed. Keep focused and practical.]

**Related Rules**
• **[Rule Name 1]**: [One sentence description]
• **[Rule Name 2]**: [One sentence description] 
• **[Rule Name 3]**: [One sentence description]
```

##### Example Implementation

**Question**: "How does a pawn move?"

**Required Response:**
```
**Pawns move one square forward, or two squares forward on their first move.**

Pawns are unique pieces with special movement rules. They move straight forward one square to an unoccupied square. On a pawn's very first move from its starting position, it has the option to advance two squares forward instead of one, provided both squares are unoccupied. Unlike other pieces, pawns capture differently than they move—they capture diagonally forward one square.

Example: A pawn on e2 can move to e3, or jump to e4 on its first move. If there's an opponent piece on d3 or f3, the pawn can capture it by moving diagonally.

**Related Rules**
• **En Passant**: Special pawn capture rule when opponent pawn moves two squares
• **Pawn Promotion**: Pawns reaching the opposite end transform into any piece  
• **Illegal Moves**: Moving pawns backward or sideways is forbidden
```

##### Implementation Notes for Backend

Update your FastAPI response structure to enforce this template:

```python
### Add to your CLAUDE.md AI response formatting
RESPONSE_TEMPLATE = """
Always structure tabletop game rule responses in this exact format:

1. DIRECT ANSWER: Bold text, 1-2 sentences maximum, answers the specific question
2. CONFIDENCE: Percentage in bold 
3. OPTIONAL READ MORE: Detailed explanation with example, clearly marked as expandable
4. RELATED RULES: 3-5 bullet points with rule name and brief description

Never include extra sections, repetitive content, or fragmented rule text.
"""
```

#### Implementation recommendations for tabletop game rules service

##### Getting started architecture pattern

**Phase 1: Core MVP (Week 1-2)**
Start with the proven FastAPI + React + Vite pattern, implementing the standardized response template:

```python
### Minimal viable backend with template enforcement
@app.post("/rules/query")
async def handle_rule_query(query: str, game: str):
    structured_response = await generate_gaming_response(query, game)
    return format_to_template(structured_response)

def format_to_template(ai_response):
    return {
        "direct_answer": extract_direct_answer(ai_response),
        "confidence": extract_confidence(ai_response), 
        "optional_read_more": extract_detailed_explanation(ai_response),
        "related_rules": extract_related_rules(ai_response)
    }
```

**Phase 2: Enhanced UX (Week 3-4)**
Add sophisticated React components with proper accessibility and mobile optimization:

```typescript
// Enhanced state management
const useGameRulesChat = () => {
  const [messages, setMessages] = useState<GameMessage[]>([]);
  const [expandedSections, setExpandedSections] = useState<Record<string, Set<string>>>({});
  
  const sendQuery = async (question: string, game: string) => {
    const response = await fetch('/api/rules/query', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({question, game})
    });
    
    const structuredResponse = await response.json();
    setMessages(prev => [...prev, {
      id: generateId(),
      type: 'ai_response', 
      content: structuredResponse,
      timestamp: new Date()
    }]);
  };
  
  return {messages, sendQuery, expandedSections, setExpandedSections};
};
```

**Phase 3: Production deployment (Week 5-6)**
Implement caching, monitoring, and performance optimization following the patterns established by successful gaming AI applications like MTG Arena assistants and BoardGameArena's rule enforcement systems.

##### Performance optimization for gaming content

Gaming rule lookups benefit significantly from semantic caching since many questions are variations of common rules interactions:

```python
class GameRuleCaching:
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.redis_client = redis.Redis()
    
    async def get_cached_or_generate(self, question: str, game: str):
        ### Check for semantically similar questions
        similar_qa = await self.vector_db.find_similar(
            f"{game}: {question}", 
            threshold=0.85
        )
        
        if similar_qa:
            return self.adapt_cached_response(similar_qa, question)
            
        ### Generate new response and cache
        response = await generate_rule_explanation(question, game)
        await self.cache_response(question, game, response)
        return response
```

This comprehensive implementation approach, based on proven patterns from successful gaming AI applications, provides a robust foundation for building sophisticated tabletop game rule explanation interfaces. The three-tier architecture with proper progressive disclosure significantly improves user comprehension while maintaining the conversational flow essential for effective AI chat interfaces.

Key success factors include starting with the established three-tier information architecture, implementing accessibility-first expandable components, using validated AI prompting strategies for consistent structured output, and following proven FastAPI + React integration patterns that can scale from MVP to production deployment.

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
