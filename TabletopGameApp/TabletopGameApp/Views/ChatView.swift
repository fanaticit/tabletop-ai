//
//  ChatView.swift
//  TabletopGameApp
//
//  Created by Claude on 27/08/2025.
//

import SwiftUI

struct ChatView: View {
    let game: Game
    @StateObject private var conversationManager = ConversationManager()
    @EnvironmentObject private var authManager: AuthenticationManager
    @EnvironmentObject private var navigationManager: NavigationManager
    @State private var messageText = ""
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.gamingBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Header
                    headerView
                    
                    // Game Status Bar
                    gameStatusBar
                    
                    // Messages
                    messageList
                    
                    // Input Area
                    inputArea
                }
            }
        }
        .navigationViewStyle(StackNavigationViewStyle())
        .preferredColorScheme(.dark)
        .onAppear {
            conversationManager.setCurrentGame(game.game_id)
        }
    }
    
    // MARK: - Header
    
    private var headerView: some View {
        HStack {
            // Left side - Navigation and Game Info
            HStack(spacing: 12) {
                Button("Dashboard") {
                    navigationManager.navigateToDashboard()
                }
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.gamingAccent)
                
                Rectangle()
                    .fill(Color.gamingSecondary.opacity(0.3))
                    .frame(width: 1, height: 24)
                
                HStack(spacing: 8) {
                    Text(game.game_id == "chess" ? "♟️" : "🎲")
                        .font(.system(size: 20))
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text("\(game.name) Chat")
                            .font(.system(size: 16, weight: .semibold))
                            .foregroundColor(.gamingText)
                        
                        Text("AI-Powered Rules Assistant")
                            .font(.system(size: 12))
                            .foregroundColor(.gamingSecondary)
                    }
                }
            }
            
            Spacer()
            
            // Right side - Actions and User
            HStack(spacing: 12) {
                Button("Switch Game") {
                    navigationManager.navigateToGameSelection()
                }
                .font(.system(size: 12, weight: .medium))
                .padding(.horizontal, 12)
                .padding(.vertical, 6)
                .background(
                    RoundedRectangle(cornerRadius: 6)
                        .stroke(Color.gamingSecondary.opacity(0.3), lineWidth: 1)
                )
                .foregroundColor(.gamingText)
                
                Rectangle()
                    .fill(Color.gamingSecondary.opacity(0.3))
                    .frame(width: 1, height: 24)
                
                HStack(spacing: 8) {
                    Text(authManager.currentUser?.username ?? "User")
                        .font(.system(size: 14))
                        .foregroundColor(.gamingText)
                    
                    Button("Logout") {
                        authManager.logout()
                    }
                    .font(.system(size: 14))
                    .foregroundColor(.gamingSecondary)
                }
            }
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 16)
        .background(Color.gamingPrimary)
    }
    
    // MARK: - Game Status Bar
    
    private var gameStatusBar: some View {
        HStack {
            HStack(spacing: 8) {
                Circle()
                    .fill(Color.gamingSuccess)
                    .frame(width: 8, height: 8)
                
                Text("Ready to help with \(game.name) rules!")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.blue)
                
                Text("Ask any question about gameplay, rules, or strategies.")
                    .font(.system(size: 14))
                    .foregroundColor(.blue.opacity(0.7))
            }
            
            Spacer()
            
            Text("AI Powered")
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.blue.opacity(0.8))
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 12)
        .background(Color.blue.opacity(0.1))
    }
    
    // MARK: - Message List
    
    private var messageList: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(spacing: 16) {
                    if conversationManager.currentGameMessages.isEmpty {
                        welcomeMessage
                    } else {
                        ForEach(conversationManager.currentGameMessages) { message in
                            MessageBubble(message: message, game: game)
                                .id(message.id)
                        }
                        
                        if conversationManager.isLoading {
                            typingIndicator
                        }
                    }
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 16)
            }
            .onChange(of: conversationManager.currentGameMessages.count) {
                if let lastMessage = conversationManager.currentGameMessages.last {
                    withAnimation(.easeInOut(duration: 0.5)) {
                        proxy.scrollTo(lastMessage.id, anchor: .bottom)
                    }
                }
            }
        }
    }
    
    private var welcomeMessage: some View {
        VStack(spacing: 16) {
            Text(game.game_id == "chess" ? "♟️" : "🎲")
                .font(.system(size: 48))
            
            Text("Welcome to \(game.name) Assistant!")
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(.gamingText)
                .multilineTextAlignment(.center)
            
            Text("I'm here to help answer questions about \(game.name) rules, gameplay, and strategies. What would you like to know?")
                .font(.system(size: 16))
                .foregroundColor(.gamingSecondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 20)
            
            VStack(spacing: 8) {
                Text("Try asking:")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.gamingText)
                
                ForEach(sampleQuestions, id: \.self) { question in
                    Button(action: {
                        messageText = question
                        sendMessage()
                    }) {
                        Text("\"\(question)\"")
                            .font(.system(size: 14))
                            .foregroundColor(.gamingAccent)
                            .padding(.horizontal, 16)
                            .padding(.vertical, 8)
                            .background(
                                RoundedRectangle(cornerRadius: 20)
                                    .stroke(Color.gamingAccent.opacity(0.3), lineWidth: 1)
                            )
                    }
                }
            }
            .padding(.top, 20)
        }
        .padding(.vertical, 40)
    }
    
    private var sampleQuestions: [String] {
        switch game.game_id {
        case "chess":
            return [
                "How do pawns move?",
                "What is castling?",
                "How does en passant work?"
            ]
        default:
            return [
                "How do I start the game?",
                "What are the basic rules?",
                "How do I win?"
            ]
        }
    }
    
    private var typingIndicator: some View {
        HStack {
            HStack(spacing: 4) {
                ForEach(0..<3) { index in
                    Circle()
                        .fill(Color.gamingAccent)
                        .frame(width: 6, height: 6)
                        .scaleEffect(1.0)
                        .animation(
                            Animation.easeInOut(duration: 0.6)
                                .repeatForever()
                                .delay(Double(index) * 0.2),
                            value: conversationManager.isLoading
                        )
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 18)
                    .fill(Color.gamingPrimary)
            )
            
            Spacer()
        }
    }
    
    // MARK: - Input Area
    
    private var inputArea: some View {
        VStack(spacing: 12) {
            Rectangle()
                .fill(Color.gamingSecondary.opacity(0.2))
                .frame(height: 1)
            
            HStack(spacing: 12) {
                TextField("Ask a question about the rules...", text: $messageText, axis: .vertical)
                    .textFieldStyle(PlainTextFieldStyle())
                    .font(.system(size: 16))
                    .foregroundColor(.gamingText)
                    .padding(.horizontal, 16)
                    .padding(.vertical, 12)
                    .background(
                        RoundedRectangle(cornerRadius: 24)
                            .fill(Color.gamingPrimary)
                            .overlay(
                                RoundedRectangle(cornerRadius: 24)
                                    .stroke(Color.gamingSecondary.opacity(0.3), lineWidth: 1)
                            )
                    )
                    .lineLimit(1...4)
                
                Button(action: sendMessage) {
                    Image(systemName: conversationManager.isLoading ? "stop.circle.fill" : "arrow.up.circle.fill")
                        .font(.system(size: 32))
                        .foregroundColor(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty ? .gamingSecondary : .gamingAccent)
                }
                .disabled(messageText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty && !conversationManager.isLoading)
            }
            .padding(.horizontal, 20)
        }
        .padding(.vertical, 16)
        .background(Color.gamingBackground)
        .onSubmit {
            sendMessage()
        }
    }
    
    private func sendMessage() {
        let trimmedMessage = messageText.trimmingCharacters(in: .whitespacesAndNewlines)
        
        guard !trimmedMessage.isEmpty else { return }
        
        let message = trimmedMessage
        messageText = ""
        
        Task {
            await conversationManager.sendMessage(content: message, gameId: game.game_id)
        }
    }
}

#Preview {
    let sampleGame = Game(
        game_id: "chess",
        name: "Chess",
        description: "The classic strategy board game",
        complexity: "medium",
        min_players: 2,
        max_players: 2,
        rule_count: 15,
        publisher: "FIDE",
        categories: ["strategy", "board"],
        ai_tags: ["classic", "strategy"],
        created_at: Date()
    )
    
    ChatView(game: sampleGame)
        .environmentObject(AuthenticationManager())
}