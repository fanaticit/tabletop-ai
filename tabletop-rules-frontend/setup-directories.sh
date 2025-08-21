#!/bin/bash

# Create the React project structure
echo "Setting up React frontend project structure..."

# Create directories
mkdir -p src/components/auth
mkdir -p src/components/chat
mkdir -p src/components/games
mkdir -p src/components/layout
mkdir -p src/stores
mkdir -p src/lib
mkdir -p src/hooks
mkdir -p src/__tests__
mkdir -p src/mocks

# Create placeholder component files (these will fail tests initially)
touch src/components/auth/LoginForm.tsx
touch src/components/auth/RegistrationForm.tsx
touch src/components/games/GameSelector.tsx
touch src/components/chat/ChatInterface.tsx
touch src/components/chat/MessageInput.tsx
touch src/components/chat/MessageList.tsx

# Create placeholder store files
touch src/stores/authStore.ts
touch src/stores/gameStore.ts
touch src/stores/conversationStore.ts

# Create placeholder lib files
touch src/lib/api.ts

echo "Directory structure created!"
echo ""
echo "Next steps:"
echo "1. Copy the package.json, .env.local, and setupTests.ts files"
echo "2. Run 'npm install' to install dependencies"
echo "3. Copy the test files to src/__tests__/"
echo "4. Run 'npm test' to see failing tests"
echo "5. Then we'll implement each component to make tests pass!"