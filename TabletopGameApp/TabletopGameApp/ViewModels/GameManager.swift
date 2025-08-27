//
//  GameManager.swift
//  TabletopGameApp
//
//  Created by Claude on 27/08/2025.
//

import Foundation

@MainActor
class GameManager: ObservableObject {
    @Published var games: [Game] = []
    @Published var selectedGame: Game?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiClient: APIClient
    
    init(apiClient: APIClient = APIClient.shared) {
        self.apiClient = apiClient
    }
    
    func loadGames() async {
        isLoading = true
        errorMessage = nil
        
        defer {
            isLoading = false
        }
        
        do {
            games = try await apiClient.fetchGames()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
    
    func selectGame(_ game: Game) {
        selectedGame = game
    }
    
    func clearSelection() {
        selectedGame = nil
    }
    
    func clearError() {
        errorMessage = nil
    }
    
    // MARK: - Computed Properties
    
    var gamesByComplexity: [String: [Game]] {
        Dictionary(grouping: games) { $0.complexity }
    }
    
    var featuredGames: [Game] {
        // Return first 3 games as featured, or all if less than 3
        Array(games.prefix(3))
    }
    
    func filteredGames(searchText: String) -> [Game] {
        if searchText.isEmpty {
            return games
        }
        
        return games.filter { game in
            game.name.localizedCaseInsensitiveContains(searchText) ||
            game.description.localizedCaseInsensitiveContains(searchText) ||
            game.categories.contains { $0.localizedCaseInsensitiveContains(searchText) } ||
            game.aiTags.contains { $0.localizedCaseInsensitiveContains(searchText) }
        }
    }
}