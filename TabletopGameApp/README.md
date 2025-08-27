# TabletopPro iOS App

A native iOS app for the AI-powered tabletop game rules query service. Built with SwiftUI and designed for iOS 16+.

## 🚀 Features

### Complete Feature Parity with React Frontend
- **JWT Authentication** with secure Keychain storage
- **Game Selection** with search and filtering
- **AI-Powered Chat** with GPT-4o-mini integration
- **Structured Responses** with collapsible sections
- **Conversation History** with local persistence
- **Professional Gaming UI** with dark theme

### iOS-Specific Enhancements
- **Native SwiftUI Interface** optimized for iOS
- **Responsive Design** for iPhone and iPad
- **Dark Mode** gaming-focused color scheme
- **Secure Storage** using iOS Keychain Services
- **Performance Optimized** with lazy loading

## 🏗️ Architecture

### MVVM Pattern
```
Views/              # SwiftUI Views
├── LoginView.swift        # Authentication interface
├── DashboardView.swift    # Main dashboard
├── GameSelectionView.swift # Game picker
├── ChatView.swift         # AI chat interface
└── MessageBubble.swift    # Chat message components

ViewModels/         # Business Logic
├── AuthenticationManager.swift  # JWT auth & user state
├── GameManager.swift           # Game data & selection
└── ConversationManager.swift   # Chat state & AI integration

Models/             # Data Models
└── User.swift             # All Codable models

Services/           # Core Services  
├── APIClient.swift        # FastAPI integration
└── KeychainManager.swift  # Secure token storage
```

## 🔧 Setup Instructions

### 1. Prerequisites
- **Xcode 16+** (required for iOS 18 SDK)
- **iOS 16.0+** minimum deployment target
- **FastAPI Backend** running on `localhost:8000`

### 2. Configure Network Security

The app is pre-configured for localhost development. For production, update the `baseURL` in `APIClient.swift`:

```swift
#if DEBUG
private let baseURL = "http://localhost:8000"  // Development
#else 
private let baseURL = "https://your-api.com"   // Production
#endif
```

### 3. Build and Run

1. Open `TabletopGameApp.xcodeproj` in Xcode
2. Select iPhone simulator (iPhone 16 recommended)  
3. Build and run (⌘+R)

### 4. Demo Credentials

Use these credentials to test the app:
- **Username**: `admin`
- **Password**: `secret`

## 📱 App Flow

### 1. Authentication
- Secure login with JWT tokens
- Keychain storage for persistent sessions
- Professional gaming UI design

### 2. Dashboard
- Welcome screen with quick stats
- Featured games carousel
- Recent conversation history
- Quick action buttons

### 3. Game Selection  
- Browse all available games
- Search by name or category
- Filter by complexity (easy/medium/hard)
- Rich game cards with metadata

### 4. AI Chat Interface
- Real-time chat with AI assistant
- Structured response format
- Collapsible sections for detailed rules
- Source references with metadata
- Message history persistence

## 🔗 API Integration

### FastAPI Endpoints Used
```
POST /token                    # JWT authentication
GET  /api/games/              # Fetch game library
POST /api/chat/query          # AI rule queries
```

### Response Formats
- **Structured Responses**: New format with expandable sections
- **Legacy Support**: Backwards compatibility with simple responses
- **Error Handling**: Comprehensive error recovery

## 🎨 Design System

### Gaming Color Palette
```swift
.gamingBackground  // #0D1117 - Deep dark background
.gamingPrimary     // #21262D - Card backgrounds  
.gamingAccent      // #58A6FF - Interactive elements
.gamingText        // #F0F6FC - Primary text
.gamingSecondary   // #8B949E - Secondary text
```

### Typography
- **Headers**: System font, bold, rounded design
- **Body Text**: System font, optimized for readability
- **Code/Rules**: Monospace font for technical content

## 🔒 Security Features

### Token Management
- **Keychain Storage**: Encrypted JWT token storage
- **Automatic Expiry**: Token refresh handling
- **Secure Communication**: HTTPS enforcement in production

### Data Protection
- **No Sensitive Logging**: Secure handling of user data
- **Local Storage**: UserDefaults for non-sensitive preferences
- **Memory Management**: Proper cleanup of sensitive data

## 🚀 Performance Optimizations

### Efficient UI
- **Lazy Loading**: ScrollView with LazyVStack
- **Image Caching**: Optimized asset loading
- **State Management**: Minimal re-renders with @Published

### Network Efficiency
- **Async/Await**: Modern concurrency patterns
- **Request Batching**: Efficient API usage
- **Error Recovery**: Graceful degradation

## 🧪 Development Notes

### Building
- Uses SwiftUI NavigationView (iOS 16+ compatible)
- Automatic dependency resolution
- No external dependencies required

### Testing
- Ready for unit tests with ViewModels
- UI tests with accessibility identifiers
- Network mocking capabilities

### Deployment
- Configure code signing for distribution  
- Update bundle identifier for App Store
- Set production API endpoints

## 🔄 Sync with React Frontend

This iOS app maintains complete feature parity with the React frontend:

| Feature | React | iOS | Status |
|---------|-------|-----|--------|
| JWT Auth | ✅ | ✅ | ✅ Complete |
| Game Selection | ✅ | ✅ | ✅ Complete |
| AI Chat | ✅ | ✅ | ✅ Complete |
| Dashboard | ✅ | ✅ | ✅ Complete |
| Structured Responses | ✅ | ✅ | ✅ Complete |
| Message History | ✅ | ✅ | ✅ Complete |

## 📞 Support

For issues or questions:
1. Check the FastAPI backend is running on `localhost:8000`
2. Verify network security settings allow localhost access
3. Ensure demo credentials are correct (admin/secret)
4. Check Xcode console for detailed error messages

## 🎯 Next Steps

1. **Custom Game Icons**: Add specific icons for each game
2. **Push Notifications**: Real-time updates
3. **Offline Support**: Cache rules for offline access
4. **Widget Support**: iOS home screen widgets
5. **Apple Watch App**: Companion watchOS app