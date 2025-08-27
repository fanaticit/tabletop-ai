//
//  GameSelectionView.swift
//  TabletopGameApp
//
//  Created by Claude on 27/08/2025.
//

import SwiftUI

struct GameSelectionView: View {
    @StateObject private var gameManager = GameManager()
    @EnvironmentObject private var authManager: AuthenticationManager
    @State private var searchText = ""
    @State private var selectedComplexity: String? = nil
    
    private let complexityOrder = ["easy", "medium", "hard"]
    
    var body: some View {
        NavigationView {
            ZStack {
                Color.gamingBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Header
                    headerView
                    
                    // Search Bar
                    searchBarView
                    
                    // Content
                    if gameManager.isLoading {
                        loadingView
                    } else if let errorMessage = gameManager.errorMessage {
                        errorView(errorMessage)
                    } else {
                        gameListView
                    }
                }
            }
        }
        .preferredColorScheme(.dark)
        .navigationViewStyle(StackNavigationViewStyle())
        .task {
            if gameManager.games.isEmpty {
                await gameManager.loadGames()
            }
        }
    }
    
    // MARK: - Header
    
    private var headerView: some View {
        VStack(spacing: 16) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Choose Your Game")
                        .font(.system(size: 28, weight: .bold))
                        .foregroundColor(.gamingText)
                    
                    Text("Select a tabletop game to start asking questions about its rules")
                        .font(.system(size: 14))
                        .foregroundColor(.gamingSecondary)
                }
                
                Spacer()
                
                Button("Logout") {
                    authManager.logout()
                }
                .font(.system(size: 14, weight: .medium))
                .foregroundColor(.gamingAccent)
            }
            .padding(.horizontal, 20)
            .padding(.top, 10)
        }
        .background(Color.gamingPrimary)
    }
    
    // MARK: - Search Bar
    
    private var searchBarView: some View {
        VStack(spacing: 12) {
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.gamingSecondary)
                
                TextField("Search games...", text: $searchText)
                    .textFieldStyle(PlainTextFieldStyle())
                    .foregroundColor(.gamingText)
                
                if !searchText.isEmpty {
                    Button(action: { searchText = "" }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(.gamingSecondary)
                    }
                }
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
            
            // Complexity Filter
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 12) {
                    complexityFilterButton(for: nil, label: "All")
                    
                    ForEach(complexityOrder, id: \.self) { complexity in
                        complexityFilterButton(for: complexity, label: complexity.capitalized)
                    }
                }
                .padding(.horizontal, 20)
            }
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 16)
        .background(Color.gamingBackground)
    }
    
    private func complexityFilterButton(for complexity: String?, label: String) -> some View {
        Button(action: {
            selectedComplexity = complexity
        }) {
            Text(label)
                .font(.system(size: 14, weight: .medium))
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .background(
                    RoundedRectangle(cornerRadius: 20)
                        .fill(selectedComplexity == complexity ? Color.gamingAccent : Color.gamingPrimary)
                        .overlay(
                            RoundedRectangle(cornerRadius: 20)
                                .stroke(Color.gamingSecondary.opacity(0.3), lineWidth: 1)
                        )
                )
                .foregroundColor(selectedComplexity == complexity ? .white : .gamingText)
        }
    }
    
    // MARK: - Game List
    
    private var gameListView: some View {
        ScrollView {
            LazyVStack(spacing: 16) {
                ForEach(filteredGames) { game in
                    GameCard(
                        game: game,
                        onSelect: {
                            gameManager.selectGame(game)
                        }
                    )
                }
                
                if filteredGames.isEmpty && !searchText.isEmpty {
                    emptySearchView
                }
            }
            .padding(.horizontal, 20)
            .padding(.bottom, 20)
        }
    }
    
    private var filteredGames: [Game] {
        let searchFiltered = gameManager.filteredGames(searchText: searchText)
        
        guard let complexity = selectedComplexity else {
            return searchFiltered
        }
        
        return searchFiltered.filter { $0.complexity == complexity }
    }
    
    // MARK: - Loading View
    
    private var loadingView: some View {
        VStack(spacing: 16) {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: .gamingAccent))
                .scaleEffect(1.2)
            
            Text("Loading games...")
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(.gamingSecondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    // MARK: - Error View
    
    private func errorView(_ message: String) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 48))
                .foregroundColor(.gamingError)
            
            Text("Failed to load games")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.gamingText)
            
            Text(message)
                .font(.system(size: 14))
                .foregroundColor(.gamingSecondary)
                .multilineTextAlignment(.center)
            
            Button("Try Again") {
                Task {
                    await gameManager.loadGames()
                }
            }
            .font(.system(size: 16, weight: .medium))
            .foregroundColor(.white)
            .padding(.horizontal, 24)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 8)
                    .fill(Color.gamingAccent)
            )
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(.horizontal, 40)
    }
    
    // MARK: - Empty Search View
    
    private var emptySearchView: some View {
        VStack(spacing: 16) {
            Image(systemName: "magnifyingglass")
                .font(.system(size: 48))
                .foregroundColor(.gamingSecondary)
            
            Text("No games found")
                .font(.system(size: 18, weight: .semibold))
                .foregroundColor(.gamingText)
            
            Text("Try adjusting your search or filters")
                .font(.system(size: 14))
                .foregroundColor(.gamingSecondary)
        }
        .padding(.vertical, 60)
    }
}

// MARK: - Game Card

struct GameCard: View {
    let game: Game
    let onSelect: () -> Void
    
    var body: some View {
        Button(action: onSelect) {
            VStack(alignment: .leading, spacing: 12) {
                // Header
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(game.name)
                            .font(.system(size: 20, weight: .bold))
                            .foregroundColor(.gamingText)
                            .multilineTextAlignment(.leading)
                        
                        HStack(spacing: 16) {
                            complexityBadge
                            playerCountBadge
                            ruleCountBadge
                        }
                    }
                    
                    Spacer()
                    
                    gameIcon
                }
                
                // Description
                Text(game.description)
                    .font(.system(size: 14))
                    .foregroundColor(.gamingSecondary)
                    .multilineTextAlignment(.leading)
                    .lineLimit(3)
                
                // Categories
                if !game.categories.isEmpty {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 8) {
                            ForEach(Array(game.categories.prefix(5)), id: \.self) { category in
                                Text(category)
                                    .font(.system(size: 12, weight: .medium))
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
                                    .background(
                                        RoundedRectangle(cornerRadius: 12)
                                            .fill(Color.gamingAccent.opacity(0.2))
                                    )
                                    .foregroundColor(.gamingAccent)
                            }
                        }
                        .padding(.horizontal, 1)
                    }
                }
            }
            .padding(16)
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
                .frame(width: 8, height: 8)
            
            Text(game.complexity.capitalized)
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.gamingSecondary)
        }
    }
    
    private var playerCountBadge: some View {
        HStack(spacing: 4) {
            Image(systemName: "person.2.fill")
                .font(.system(size: 10))
                .foregroundColor(.gamingSecondary)
            
            Text("\(game.minPlayers)-\(game.maxPlayers)")
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.gamingSecondary)
        }
    }
    
    private var ruleCountBadge: some View {
        HStack(spacing: 4) {
            Image(systemName: "book.fill")
                .font(.system(size: 10))
                .foregroundColor(.gamingSecondary)
            
            Text("\(game.ruleCount) rules")
                .font(.system(size: 12, weight: .medium))
                .foregroundColor(.gamingSecondary)
        }
    }
    
    private var gameIcon: some View {
        Text(game.gameId == "chess" ? "♟️" : "🎲")
            .font(.system(size: 32))
    }
    
    private var complexityColor: Color {
        switch game.complexity {
        case "easy":
            return .gamingSuccess
        case "medium":
            return .gamingWarning
        case "hard":
            return .gamingError
        default:
            return .gamingSecondary
        }
    }
}

#Preview {
    GameSelectionView()
        .environmentObject(AuthenticationManager())
}