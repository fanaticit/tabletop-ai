# iOS App Network Debugging Guide

## 🔍 **Current Issue**: Login Network Error

The error `"The operation couldn't be completed. (TabletopGame.APIClient.NetworkError error 0.)"` indicates a network connection problem.

## ✅ **Fixes Applied**

1. **Changed localhost to 127.0.0.1**: iOS simulator sometimes has issues with `localhost`
2. **Added detailed logging**: Console will now show exactly what's happening
3. **Improved error messages**: Better error descriptions for debugging
4. **Added timeout**: 10-second timeout to prevent hanging requests

## 🔧 **Debugging Steps**

### 1. Check Console Logs
When you run the app and try to login, look at the Xcode console output for these messages:
```
🌐 Attempting to connect to: http://127.0.0.1:8000/token
📤 Sending authentication request...
📥 Received response
📊 Status code: 200
✅ Authentication successful
```

### 2. Common Issues & Solutions

#### **Issue**: Can't connect to 127.0.0.1:8000
**Solution**: iOS simulator networking issue
```bash
# Test from command line first:
curl -X POST "http://127.0.0.1:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=secret"
```

#### **Issue**: App Transport Security blocking HTTP
**Solution**: Configure in Xcode project settings:
1. Open `TabletopGameApp.xcodeproj`
2. Select the project → TabletopGameApp target
3. Go to Info tab
4. Add custom iOS target property:
   - Key: `NSAppTransportSecurity`
   - Type: Dictionary
   - Add child: `NSAllowsArbitraryLoads` = YES (for development only)

#### **Issue**: Simulator network not working
**Solution**: Try these steps:
1. **Reset simulator**: Device → Erase All Content and Settings
2. **Use physical device**: Test on actual iPhone/iPad
3. **Use different simulator**: Try iPad simulator instead

### 3. Alternative Backend URLs to Try

Update the `baseURL` in `APIClient.swift`:

```swift
// Try these URLs in order:
private let baseURL = "http://127.0.0.1:8000"     // Current
private let baseURL = "http://localhost:8000"     // Alternative 1  
private let baseURL = "http://0.0.0.0:8000"      // Alternative 2
```

### 4. FastAPI CORS Configuration

Ensure your FastAPI backend allows iOS requests:

```python
# In your FastAPI main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 5. Manual Testing

Test the exact request the app makes:

```bash
# This should match what the iOS app sends:
curl -X POST "http://127.0.0.1:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "User-Agent: TabletopGameApp" \
  -d "username=admin&password=secret" \
  -v
```

## 🚀 **Next Steps**

1. **Run the app** and check Xcode console for the new log messages
2. **Try login** with `admin`/`secret` credentials  
3. **Look for specific error** in the console logs
4. **If still failing**, try the alternative solutions above

## 🔧 **Emergency Workaround**

If networking continues to fail, you can temporarily mock the authentication:

```swift
// In AuthenticationManager.swift, temporarily modify login method:
func login(username: String, password: String) async throws {
    // TEMPORARY: Skip network call for testing
    if username == "admin" && password == "secret" {
        currentUser = User(
            id: "1",
            email: "admin@example.com", 
            username: "admin",
            preferences: User.UserPreferences(selectedGameId: nil, theme: .system)
        )
        isAuthenticated = true
        return
    }
    
    // Original network code here...
}
```

This allows you to test the rest of the app while debugging network issues.

## 📱 **Testing on Physical Device**

If simulator networking fails:
1. Connect iPhone/iPad via USB
2. Select physical device in Xcode
3. Update `baseURL` to your Mac's IP address:
   ```bash
   # Find your Mac's IP:
   ifconfig | grep "inet " | grep -v 127.0.0.1
   ```
   ```swift
   private let baseURL = "http://YOUR_MAC_IP:8000"  // e.g., "http://192.168.1.100:8000"
   ```

## 🎯 **Expected Console Output**

When login works correctly, you should see:
```
🌐 Attempting to connect to: http://127.0.0.1:8000/token
📤 Sending authentication request...
📥 Received response
📊 Status code: 200
✅ Authentication successful
```

When it fails, you'll see the specific error that helps identify the problem.