//
//  ConversationManager.swift
//  TabletopGameApp
//
//  Created by Claude on 27/08/2025.
//

import Foundation

@MainActor
class ConversationManager: ObservableObject {
    @Published var messages: [ChatMessage] = []
    @Published var isLoading = false
    @Published var currentGameId: String?
    
    private let apiClient: APIClient
    
    init(apiClient: APIClient = APIClient.shared) {
        self.apiClient = apiClient
        loadMessagesFromStorage()
    }
    
    func setCurrentGame(_ gameId: String) {
        currentGameId = gameId
    }
    
    func addMessage(_ message: ChatMessage) {
        messages.append(message)
        saveMessagesToStorage()
    }
    
    func sendMessage(content: String, gameId: String) async {
        // Add user message
        let userMessage = ChatMessage(
            role: .user,
            content: content,
            gameId: gameId
        )
        addMessage(userMessage)
        
        isLoading = true
        
        defer {
            isLoading = false
        }
        
        do {
            let response = try await apiClient.queryChatBot(query: content, gameSystem: gameId)
            
            // Create assistant message with structured response
            let assistantMessage = ChatMessage(
                role: .assistant,
                content: response.structuredResponse.content.summary.text,
                gameId: gameId,
                structuredResponse: response.structuredResponse
            )
            
            addMessage(assistantMessage)
            
        } catch {
            // Add error message
            let errorMessage = ChatMessage(
                role: .assistant,
                content: "Sorry, I encountered an error while processing your question. Please try again. Error: \(error.localizedDescription)",
                gameId: gameId
            )
            addMessage(errorMessage)
        }
    }
    
    func clearMessages(for gameId: String? = nil) {
        if let gameId = gameId {
            messages.removeAll { $0.gameId == gameId }
        } else {
            messages.removeAll()
        }
        saveMessagesToStorage()
    }
    
    func messagesForGame(_ gameId: String) -> [ChatMessage] {
        return messages.filter { $0.gameId == gameId }
    }
    
    // MARK: - Persistence
    
    private func loadMessagesFromStorage() {
        if let data = UserDefaults.standard.data(forKey: "stored_messages"),
           let decodedMessages = try? JSONDecoder().decode([ChatMessage].self, from: data) {
            messages = decodedMessages
        }
    }
    
    private func saveMessagesToStorage() {
        if let encoded = try? JSONEncoder().encode(messages) {
            UserDefaults.standard.set(encoded, forKey: "stored_messages")
        }
    }
    
    // MARK: - Computed Properties
    
    var hasMessages: Bool {
        !messages.isEmpty
    }
    
    var currentGameMessages: [ChatMessage] {
        guard let gameId = currentGameId else { return [] }
        return messagesForGame(gameId)
    }
    
    func messageCount(for gameId: String) -> Int {
        return messagesForGame(gameId).count
    }
    
    func lastMessage(for gameId: String) -> ChatMessage? {
        return messagesForGame(gameId).last
    }
}