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
            print("🔑 AuthManager: Calling API client...")
            let tokenResponse = try await apiClient.authenticateUser(username: username, password: password)
            
            print("🔑 AuthManager: Got token response, storing in keychain...")
            do {
                try keychainManager.storeToken(tokenResponse.access_token)
                print("🔑 AuthManager: Token stored successfully in keychain")
            } catch {
                print("❌ AuthManager: Failed to store token in keychain: \(error)")
                throw error
            }
            
            // Create user from token response
            print("🔑 AuthManager: Creating user object...")
            if let tokenUser = tokenResponse.user {
                print("🔑 AuthManager: Using user data from token: \(tokenUser.username)")
                currentUser = User(
                    id: tokenUser.id,
                    email: tokenUser.email,
                    username: tokenUser.username,
                    preferences: User.UserPreferences(
                        selectedGameId: nil,
                        theme: .system
                    )
                )
            } else {
                print("🔑 AuthManager: No user data in token, using fallback")
                // Fallback if user field is missing
                currentUser = User(
                    id: "1",
                    email: username,
                    username: username,
                    preferences: User.UserPreferences(
                        selectedGameId: nil,
                        theme: .system
                    )
                )
            }
            
            print("🔑 AuthManager: Setting isAuthenticated = true")
            isAuthenticated = true
            print("✅ User authenticated successfully: \(currentUser?.username ?? "Unknown")")
            print("🔑 AuthManager: Authentication complete, isAuthenticated = \(isAuthenticated)")
        } catch {
            errorMessage = error.localizedDescription
            print("❌ Authentication error in manager: \(error)")
            print("❌ Error type: \(type(of: error))")
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