# Tabletop Rules AI Frontend - Project Documentation

## Project Overview
React TypeScript frontend for an AI-powered tabletop game rules query service. Users can select games, ask questions about rules, and have conversational interactions with context preservation.

## Current Status ✅❌

### ✅ FULLY WORKING (All Tests Passing + Running App)
- **Development Server**: `npm start` works perfectly on `http://localhost:3000`
- **Authentication System**: Login/Registration forms with validation + error handling
- **Game Selection**: Complete game picker with filtering, selection persistence, and visual feedback
- **State Management**: Zustand stores working perfectly with React Query
- **API Integration**: React Query v5 with proper configuration (gcTime, etc.)
- **Test Infrastructure**: 17 tests passing - full TDD workflow established
- **TypeScript**: All compilation errors resolved, strict typing working
- **Routing**: Basic React Router setup with `/login`, `/register`, `/games`, `/`

### ❌ READY FOR IMPLEMENTATION (Next Features)
- **Chat Functionality**: Real conversation interface with AI (need to implement ChatInterface, MessageInput, MessageList)
- **Conversation Context**: Message history and follow-up questions (ConversationStore ready for implementation)
- **User Registration Backend**: Frontend ready, need FastAPI endpoint
- **Real-time Updates**: WebSocket integration for live chat
- **Enhanced UI/Styling**: Move from minimal HTML/CSS to modern UI framework
- **Navigation**: Full app navigation and layout structure
- **Error Boundaries**: Better error handling and user feedback

## Project Structure

```
tabletop-rules-frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx           ✅ Working (minimal styling)
│   │   │   └── RegistrationForm.tsx    ✅ Working (minimal styling)
│   │   ├── games/
│   │   │   └── GameSelector.tsx        ✅ Working (React Query + Zustand)
│   │   └── chat/
│   │       ├── ChatInterface.tsx       ❌ Placeholder only
│   │       ├── MessageInput.tsx        ❌ Placeholder only
│   │       └── MessageList.tsx         ❌ Placeholder only
│   ├── stores/
│   │   ├── authStore.ts                ✅ JWT token management
│   │   ├── gameStore.ts                ✅ Game selection persistence
│   │   └── conversationStore.ts        ❌ Not implemented
│   ├── __tests__/
│   │   ├── auth.test.tsx               ✅ 7 tests passing
│   │   ├── games.test.tsx              ✅ 7 tests passing  
│   │   └── chat.test.tsx               ✅ 3 basic tests passing
│   ├── test-utils.tsx                  ✅ Test providers setup
│   ├── setupTests.ts                   ✅ Jest configuration
│   └── App.tsx                         ✅ Basic routing
├── package.json                        ✅ Dependencies configured
└── README.md
```

## Key Dependencies

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "typescript": "^4.9.5",
    "@tanstack/react-query": "^5.8.4",  // Server state management
    "zustand": "^4.4.7",                // Client state management  
    "react-router-dom": "^6.20.1",      // Routing
    "axios": "^1.6.2",                  // HTTP client (not used yet)
    "jwt-decode": "^4.0.0",             // JWT token parsing
    "socket.io-client": "^4.7.4"        // WebSocket (not used yet)
  }
}
```

## Configuration Files

### package.json - Scripts
```json
{
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build", 
    "test": "react-scripts test",
    "test:watch": "react-scripts test --watch",
    "test:coverage": "react-scripts test --coverage --watchAll=false"
  }
}
```

### .env.local
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
REACT_APP_ENV=development
```

## State Management Architecture

### Auth Store (Zustand)
```typescript
interface AuthStore {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
  updateUserPreferences: (preferences: Partial<User['preferences']>) => void;
  setLoading: (loading: boolean) => void;
}
```

### Game Store (Zustand)  
```typescript
interface GameStore {
  selectedGame: Game | null;
  selectGame: (game: Game) => void;
  clearSelection: () => void;
}
```

### Server State (React Query)
- Games list fetching
- Authentication API calls
- Future: Chat message APIs

## Test Infrastructure

### Test Utils Setup
```typescript
// src/test-utils.tsx - Provides all necessary providers for testing
const AllTheProviders = ({ children }) => (
  <BrowserRouter>
    <QueryClientProvider client={queryClient}>
      <div data-testid="test-wrapper">
        {children}
      </div>
    </QueryClientProvider>
  </BrowserRouter>
);
```

### Mock Strategy
- **Fetch mocking**: Global fetch mock in setupTests.ts
- **No MSW**: Removed to avoid complexity
- **Simple mocks**: Direct Jest mocks for external dependencies

### Current Test Coverage
- **Auth**: Form rendering, validation, API integration
- **Games**: Loading, selection, filtering, error handling
- **Chat**: Basic component rendering (placeholders)

## API Integration Points

### Current Endpoints
```typescript
// Working with existing FastAPI backend
GET  /api/games                    // ✅ Fetch available games
POST /api/auth/login               // ✅ User authentication  
POST /api/auth/register            // ❌ Need to add to backend
POST /api/chat/query               // ❌ Basic endpoint exists, needs enhancement
```

### Expected API Contracts
```typescript
// Game object
interface Game {
  id: string;
  name: string;
  description: string;
  category: string;
  rule_count: number;
}

// Auth response
interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    username: string;
    email: string;
  };
}

// Chat query (to implement)
interface ChatQuery {
  query: string;
  game_system: string;
  conversation_id?: string;
}
```

## Development Workflow (TDD)

### Test-First Development Process
1. **Write failing test** for new feature
2. **Run tests** to see failure: `npm test`
3. **Implement minimal code** to make test pass
4. **Refactor** while keeping tests green
5. **Repeat** for next feature

### Test Commands
```bash
npm test                    # Run all tests
npm test -- --watch        # Watch mode for TDD
npm test -- auth.test.tsx   # Run specific test file
npm run test:coverage       # Coverage report
```

## Styling Approach

### Current: Minimal HTML/CSS
- **Pros**: No dependency issues, tests work reliably
- **Cons**: Basic styling, not production-ready
- **Components**: Use inline styles for now

### Future: Enhanced UI Options
1. **Chakra UI**: Full component library (had dependency issues)
2. **Tailwind CSS**: Utility-first CSS
3. **Material-UI**: Google Material Design
4. **Custom CSS**: Styled-components or CSS modules

## Next Implementation Priority

### Phase 1: Chat Functionality (HIGH)
1. **ConversationStore**: Implement Zustand store for chat state
2. **MessageInput**: Real input component with form handling
3. **MessageList**: Display messages with proper formatting
4. **ChatInterface**: Integrate input + list with API calls

### Phase 2: Enhanced Features (MEDIUM)
1. **Conversation Context**: Maintain chat history
2. **User Registration**: Add backend endpoint + frontend form
3. **Real-time Updates**: WebSocket integration
4. **Error Boundaries**: Better error handling

### Phase 3: Polish (LOW)
1. **Better Styling**: Choose and implement UI framework
2. **Performance**: Code splitting, lazy loading
3. **Accessibility**: ARIA labels, keyboard navigation
4. **PWA Features**: Offline support, installable

## Common Issues & Solutions

### Infinite Loop Prevention
- **Problem**: useEffect causing setState loops
- **Solution**: Separate server state (React Query) from client state (Zustand)

### Dependency Conflicts
- **Problem**: MSW/Chakra UI version conflicts
- **Solution**: Use minimal dependencies, add complexity gradually

### Test Environment
- **Problem**: Browser APIs not available in Jest
- **Solution**: Mock in setupTests.ts (localStorage, fetch, etc.)

## FastAPI Backend Integration

### Required Backend Endpoints
```python
# Add to FastAPI backend
@app.post("/api/auth/register")
async def register_user(user_data: UserCreate):
    # Create user in MongoDB users collection
    pass

@app.post("/api/chat/conversation")  
async def start_conversation(game_id: str):
    # Create new conversation thread
    pass

@app.get("/api/chat/conversations/{conversation_id}")
async def get_conversation_history():
    # Retrieve message history
    pass
```

### MongoDB Collections Needed
```javascript
// users collection
{
  _id: ObjectId,
  username: String,
  email: String,
  hashedPassword: String,
  createdAt: Date,
  preferences: {
    selectedGameId: String,
    theme: String
  }
}

// conversations collection  
{
  _id: ObjectId,
  userId: ObjectId,
  gameId: String,
  createdAt: Date,
  lastMessageAt: Date,
  messageCount: Number
}

// messages collection
{
  _id: ObjectId,
  conversationId: ObjectId,
  role: String, // 'user' | 'assistant'
  content: String,
  timestamp: Date
}
```

## Development Commands

```bash
# Start development
npm start                 # Frontend dev server (port 3000)
# Backend should run on port 8000

# Testing  
npm test                  # Run tests
npm test -- --watch      # TDD mode

# Building
npm run build            # Production build
npm run test:coverage    # Test coverage report
```

## Key Design Decisions Made

1. **State Management**: Zustand (simple) + React Query (server state)
2. **Testing**: Simple fetch mocks instead of MSW
3. **Styling**: Start minimal, upgrade later
4. **Architecture**: Component-store separation
5. **API**: RESTful with future WebSocket enhancement

## Files to Reference in New Chats

**Essential Files to Share:**
- `src/stores/authStore.ts` - Authentication state management
- `src/stores/gameStore.ts` - Game selection state
- `src/components/games/GameSelector.tsx` - Working game component
- `src/__tests__/games.test.tsx` - Test examples
- `src/test-utils.tsx` - Test setup
- `package.json` - Dependencies

**Current Working Test Command:**
```bash
npm test
# Should show: 17 tests passing across 3 suites
```

This documentation provides everything needed to continue development in future chats. The project is at a solid foundation stage with working authentication, game selection, and test infrastructure ready for implementing the chat functionality.