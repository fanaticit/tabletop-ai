//
//  AuthenticationManager.swift
//  TabletopGameApp
//
//  Created by Claude on 27/08/2025.
//

import Foundation

@MainActor
class AuthenticationManager: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    private let apiClient: APIClient
    private let keychainManager: KeychainManager
    
    init(apiClient: APIClient = APIClient.shared, keychainManager: KeychainManager = KeychainManager.shared) {
        self.apiClient = apiClient
        self.keychainManager = keychainManager
        
        checkAuthenticationStatus()
    }
    
    private func checkAuthenticationStatus() {
        isAuthenticated = keychainManager.hasToken()
        
        if isAuthenticated {
            // Create a mock user for now - in a real app, you'd decode the JWT or fetch user profile
            currentUser = User(
                id: "1",
                email: "admin@example.com",
                username: "admin",
                preferences: User.UserPreferences(
                    selectedGameId: nil,
                    theme: .system
                )
            )
        }
    }
    
    func login(username: String, password: String) async throws {
        isLoading = true
        errorMessage = nil
        
        defer {
            isLoading = false
        }
        
        do {
            let tokenResponse = try await apiClient.authenticateUser(username: username, password: password)
            
            try keychainManager.storeToken(tokenResponse.accessToken)
            
            // Create user from login response - in a real app, decode JWT or fetch profile
            currentUser = User(
                id: "1",
                email: username,
                username: username,
                preferences: User.UserPreferences(
                    selectedGameId: nil,
                    theme: .system
                )
            )
            
            isAuthenticated = true
        } catch {
            errorMessage = error.localizedDescription
            throw error
        }
    }
    
    func logout() {
        keychainManager.deleteToken()
        isAuthenticated = false
        currentUser = nil
        errorMessage = nil
    }
    
    func updateUserPreferences(_ preferences: User.UserPreferences) {
        guard let user = currentUser else { return }
        
        currentUser = User(
            id: user.id,
            email: user.email,
            username: user.username,
            preferences: preferences
        )
    }
    
    func clearError() {
        errorMessage = nil
    }
}