//
//  DashboardView.swift
//  TabletopGameApp
//
//  Created by Claude on 27/08/2025.
//

import SwiftUI

struct DashboardView: View {
    @StateObject private var gameManager = GameManager()
    @StateObject private var conversationManager = ConversationManager()
    @EnvironmentObject private var authManager: AuthenticationManager
    @State private var selectedGame: Game?
    @State private var showGameSelection = false
    @State private var showAllConversations = false
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.gamingBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: 24) {
                        // Header
                        headerView
                        
                        // Quick Stats
                        quickStatsView
                        
                        // Featured Games
                        if !gameManager.featuredGames.isEmpty {
                            featuredGamesSection
                        }
                        
                        // Recent Conversations
                        if conversationManager.hasMessages {
                            recentConversationsSection
                        }
                        
                        // Quick Actions
                        quickActionsSection
                        
                        Spacer(minLength: 100)
                    }
                    .padding(.horizontal, 20)
                    .padding(.vertical, 16)
                }
            }
        }
        .navigationViewStyle(StackNavigationViewStyle())
        .preferredColorScheme(.dark)
        .task {
            if gameManager.games.isEmpty {
                await gameManager.loadGames()
            }
        }
        .sheet(isPresented: $showGameSelection) {
            GameSelectionView()
                .environmentObject(authManager)
        }
        .fullScreenCover(item: $selectedGame) { game in
            ChatView(game: game)
                .environmentObject(authManager)
        }
    }
    
    // MARK: - Header
    
    private var headerView: some View {
        VStack(spacing: 16) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Welcome back!")
                        .font(.system(size: 14))
                        .foregroundColor(.gamingSecondary)
                    
                    Text("Ready to explore game rules?")
                        .font(.system(size: 24, weight: .bold))
                        .foregroundColor(.gamingText)
                }
                
                Spacer()
                
                Menu {
                    Button("Profile Settings") {
                        // TODO: Navigate to profile
                    }
                    
                    Button("Preferences") {
                        // TODO: Navigate to preferences
                    }
                    
                    Divider()
                    
                    Button("Logout", role: .destructive) {
                        authManager.logout()
                    }
                } label: {
                    HStack(spacing: 8) {
                        Text(authManager.currentUser?.username ?? "User")
                            .font(.system(size: 14, weight: .medium))
                            .foregroundColor(.gamingText)
                        
                        Image(systemName: "person.circle.fill")
                            .font(.system(size: 20))
                            .foregroundColor(.gamingAccent)
                    }
                }
                .buttonStyle(PlainButtonStyle())
            }
            
            // Search Bar
            Button(action: { showGameSelection = true }) {
                HStack {
                    Image(systemName: "magnifyingglass")
                        .foregroundColor(.gamingSecondary)
                    
                    Text("Search games or ask a question...")
                        .foregroundColor(.gamingSecondary)
                    
                    Spacer()
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(
                    RoundedRectangle(cornerRadius: 12)
                        .fill(Color.gamingPrimary)
                        .overlay(
                            RoundedRectangle(cornerRadius: 12)
                                .stroke(Color.gamingSecondary.opacity(0.3), lineWidth: 1)
                        )
                )
            }
            .buttonStyle(PlainButtonStyle())
        }
    }
    
    // MARK: - Quick Stats
    
    private var quickStatsView: some View {
        HStack(spacing: 16) {
            StatCard(
                icon: "gamecontroller.fill",
                title: "Games Available",
                value: "\(gameManager.games.count)",
                color: .gamingAccent
            )
            
            StatCard(
                icon: "message.fill",
                title: "Conversations",
                value: "\(conversationManager.messages.count)",
                color: .gamingSuccess
            )
            
            StatCard(
                icon: "brain.head.profile",
                title: "AI Queries",
                value: "\(conversationManager.messages.filter { $0.role == .user }.count)",
                color: .gamingWarning
            )
        }
    }
    
    // MARK: - Featured Games Section
    
    private var featuredGamesSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("Featured Games")
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(.gamingText)
                
                Spacer()
                
                Button("View All") {
                    showGameSelection = true
                }
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.gamingAccent)
            }
            
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 16) {
                    ForEach(gameManager.featuredGames) { game in
                        FeaturedGameCard(game: game) {
                            selectedGame = game
                        }
                    }
                }
                .padding(.horizontal, 1)
            }
        }
    }
    
    // MARK: - Recent Conversations Section
    
    private var recentConversationsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            HStack {
                Text("Recent Activity")
                    .font(.system(size: 20, weight: .bold))
                    .foregroundColor(.gamingText)
                
                Spacer()
                
                Button("View All") {
                    showAllConversations = true
                }
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.gamingAccent)
            }
            
            VStack(spacing: 12) {
                ForEach(Array(recentConversationsByGame.prefix(3)), id: \.key) { gameId, messages in
                    if let game = gameManager.games.first(where: { $0.gameId == gameId }) {
                        ConversationPreviewCard(
                            game: game,
                            messageCount: messages.count,
                            lastMessage: messages.last
                        ) {
                            selectedGame = game
                        }
                    }
                }
            }
        }
    }
    
    private var recentConversationsByGame: [(key: String, value: [ChatMessage])] {
        let grouped = Dictionary(grouping: conversationManager.messages) { $0.gameId ?? "" }
        return grouped.compactMap { key, value in
            guard !key.isEmpty else { return nil }
            return (key, value.sorted { $0.timestamp > $1.timestamp })
        }
        .sorted { $0.value.first?.timestamp ?? Date.distantPast > $1.value.first?.timestamp ?? Date.distantPast }
    }
    
    // MARK: - Quick Actions Section
    
    private var quickActionsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Quick Actions")
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(.gamingText)
            
            VStack(spacing: 12) {
                QuickActionButton(
                    icon: "plus.circle.fill",
                    title: "Start New Chat",
                    subtitle: "Choose a game and start asking questions",
                    color: .gamingAccent
                ) {
                    showGameSelection = true
                }
                
                QuickActionButton(
                    icon: "book.fill",
                    title: "Browse Games",
                    subtitle: "Explore all available tabletop games",
                    color: .gamingSuccess
                ) {
                    showGameSelection = true
                }
                
                QuickActionButton(
                    icon: "clock.fill",
                    title: "Recent Activity",
                    subtitle: "View your conversation history",
                    color: .gamingWarning
                ) {
                    showAllConversations = true
                }
            }
        }
    }
}

// MARK: - Supporting Views

struct StatCard: View {
    let icon: String
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon)
                .font(.system(size: 24))
                .foregroundColor(color)
            
            Text(value)
                .font(.system(size: 20, weight: .bold))
                .foregroundColor(.gamingText)
            
            Text(title)
                .font(.system(size: 12))
                .foregroundColor(.gamingSecondary)
                .multilineTextAlignment(.center)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 16)
        .background(
            RoundedRectangle(cornerRadius: 12)
                .fill(Color.gamingPrimary)
                .overlay(
                    RoundedRectangle(cornerRadius: 12)
                        .stroke(Color.gamingSecondary.opacity(0.2), lineWidth: 1)
                )
        )
    }
}

struct FeaturedGameCard: View {
    let game: Game
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            VStack(alignment: .leading, spacing: 12) {
                HStack {
                    Text(game.gameId == "chess" ? "♟️" : "🎲")
                        .font(.system(size: 32))
                    
                    Spacer()
                    
                    complexityBadge
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(game.name)
                        .font(.system(size: 16, weight: .bold))
                        .foregroundColor(.gamingText)
                        .multilineTextAlignment(.leading)
                    
                    Text(game.description)
                        .font(.system(size: 12))
                        .foregroundColor(.gamingSecondary)
                        .lineLimit(2)
                        .multilineTextAlignment(.leading)
                }
                
                HStack {
                    Image(systemName: "person.2.fill")
                        .font(.system(size: 10))
                        .foregroundColor(.gamingSecondary)
                    
                    Text("\(game.minPlayers)-\(game.maxPlayers)")
                        .font(.system(size: 10))
                        .foregroundColor(.gamingSecondary)
                    
                    Spacer()
                    
                    Image(systemName: "book.fill")
                        .font(.system(size: 10))
                        .foregroundColor(.gamingSecondary)
                    
                    Text("\(game.ruleCount)")
                        .font(.system(size: 10))
                        .foregroundColor(.gamingSecondary)
                }
            }
            .padding(16)
            .frame(width: 200)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.gamingPrimary)
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.gamingSecondary.opacity(0.2), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private var complexityBadge: some View {
        HStack(spacing: 4) {
            Circle()
                .fill(complexityColor)
                .frame(width: 6, height: 6)
            
            Text(game.complexity.capitalized)
                .font(.system(size: 10, weight: .medium))
                .foregroundColor(.gamingSecondary)
        }
    }
    
    private var complexityColor: Color {
        switch game.complexity {
        case "easy": return .gamingSuccess
        case "medium": return .gamingWarning
        case "hard": return .gamingError
        default: return .gamingSecondary
        }
    }
}

struct ConversationPreviewCard: View {
    let game: Game
    let messageCount: Int
    let lastMessage: ChatMessage?
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 12) {
                Text(game.gameId == "chess" ? "♟️" : "🎲")
                    .font(.system(size: 24))
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(game.name)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.gamingText)
                    
                    if let lastMessage = lastMessage {
                        Text(lastMessage.content)
                            .font(.system(size: 14))
                            .foregroundColor(.gamingSecondary)
                            .lineLimit(1)
                    }
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text("\(messageCount)")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.gamingAccent)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(
                            RoundedRectangle(cornerRadius: 10)
                                .fill(Color.gamingAccent.opacity(0.2))
                        )
                    
                    if let lastMessage = lastMessage {
                        Text(formatTime(lastMessage.timestamp))
                            .font(.system(size: 10))
                            .foregroundColor(.gamingSecondary)
                    }
                }
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.gamingPrimary)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.gamingSecondary.opacity(0.2), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    private func formatTime(_ date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .abbreviated
        return formatter.localizedString(for: date, relativeTo: Date())
    }
}

struct QuickActionButton: View {
    let icon: String
    let title: String
    let subtitle: String
    let color: Color
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 16) {
                Image(systemName: icon)
                    .font(.system(size: 24))
                    .foregroundColor(color)
                    .frame(width: 40)
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.system(size: 16, weight: .semibold))
                        .foregroundColor(.gamingText)
                    
                    Text(subtitle)
                        .font(.system(size: 14))
                        .foregroundColor(.gamingSecondary)
                }
                
                Spacer()
                
                Image(systemName: "chevron.right")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.gamingSecondary)
            }
            .padding(16)
            .background(
                RoundedRectangle(cornerRadius: 12)
                    .fill(Color.gamingPrimary)
                    .overlay(
                        RoundedRectangle(cornerRadius: 12)
                            .stroke(Color.gamingSecondary.opacity(0.2), lineWidth: 1)
                    )
            )
        }
        .buttonStyle(PlainButtonStyle())
    }
}

#Preview {
    DashboardView()
        .environmentObject(AuthenticationManager())
}