//
//  APIClient.swift
//  TabletopGameApp
//
//  Created by Claude on 27/08/2025.
//

import Foundation

class APIClient: ObservableObject {
    static let shared = APIClient()
    
    #if DEBUG
    private let baseURL = "http://127.0.0.1:8000"  // Use 127.0.0.1 instead of localhost for iOS simulator
    #else
    private let baseURL = "https://your-production-api.com"
    #endif
    
    private let session = URLSession.shared
    private let decoder: JSONDecoder = {
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }()
    
    private let encoder: JSONEncoder = {
        let encoder = JSONEncoder()
        encoder.keyEncodingStrategy = .convertToSnakeCase
        return encoder
    }()
    
    enum NetworkError: Error {
        case invalidURL
        case invalidResponse
        case authenticationFailed
        case serverError(statusCode: Int, message: String?)
        case decodingError(Error)
        case encodingError(Error)
        case networkError(Error)
        case noToken
        
        var localizedDescription: String {
            switch self {
            case .invalidURL:
                return "Invalid URL"
            case .invalidResponse:
                return "Invalid response from server"
            case .authenticationFailed:
                return "Authentication failed. Please check your credentials (try admin/secret for demo)."
            case .serverError(let statusCode, let message):
                return message ?? "Server error (\(statusCode))"
            case .decodingError(let error):
                return "Failed to decode response: \(error.localizedDescription)"
            case .encodingError(let error):
                return "Failed to encode request: \(error.localizedDescription)"
            case .networkError(let error):
                return "Network error: \(error.localizedDescription)"
            case .noToken:
                return "No authentication token available"
            }
        }
    }
    
    // MARK: - Authentication
    
    func authenticateUser(username: String, password: String) async throws -> TokenResponse {
        let urlString = "\(baseURL)/token"
        print("🌐 Attempting to connect to: \(urlString)")
        
        guard let url = URL(string: urlString) else {
            print("❌ Invalid URL: \(urlString)")
            throw NetworkError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 10.0  // Add timeout
        
        // Properly encode form data - encode values individually, not the entire string
        guard let encodedUsername = username.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed),
              let encodedPassword = password.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) else {
            print("❌ Failed to encode form data")
            throw NetworkError.encodingError(NSError(domain: "encoding", code: 0, userInfo: [NSLocalizedDescriptionKey: "Failed to encode form data"]))
        }
        
        let formData = "username=\(encodedUsername)&password=\(encodedPassword)"
        request.httpBody = formData.data(using: .utf8)
        
        print("📝 Form data: \(formData)")  // Debug log
        
        print("📤 Sending authentication request...")
        
        do {
            let (data, response) = try await session.data(for: request)
            print("📥 Received response")
            
            guard let httpResponse = response as? HTTPURLResponse else {
                print("❌ Invalid response type")
                throw NetworkError.invalidResponse
            }
            
            print("📊 Status code: \(httpResponse.statusCode)")
            
            if httpResponse.statusCode == 401 {
                let message = String(data: data, encoding: .utf8)
                print("❌ Authentication failed - 401 Unauthorized: \(message ?? "No message")")
                throw NetworkError.authenticationFailed
            }
            
            if httpResponse.statusCode == 422 {
                let message = String(data: data, encoding: .utf8)
                print("❌ Authentication failed - 422 Validation Error: \(message ?? "No message")")
                throw NetworkError.authenticationFailed
            }
            
            guard httpResponse.statusCode == 200 else {
                let message = String(data: data, encoding: .utf8)
                print("❌ Server error \(httpResponse.statusCode): \(message ?? "No message")")
                throw NetworkError.serverError(statusCode: httpResponse.statusCode, message: message)
            }
            
            do {
                // Log the raw JSON response for debugging
                if let jsonString = String(data: data, encoding: .utf8) {
                    print("📄 Raw JSON response: \(jsonString)")
                } else {
                    print("❌ Could not convert response data to string")
                }
                
                // Use a separate decoder for TokenResponse since it has explicit CodingKeys
                let tokenDecoder = JSONDecoder()
                // Don't use convertFromSnakeCase for TokenResponse as it has explicit CodingKeys
                tokenDecoder.dateDecodingStrategy = .iso8601
                let response = try tokenDecoder.decode(TokenResponse.self, from: data)
                print("✅ Authentication successful")
                print("✅ Decoded token: \(response.access_token.prefix(20))...")
                print("✅ User info: \(response.user?.username ?? "No user")")
                return response
            } catch {
                print("❌ Failed to decode response: \(error)")
                print("❌ Decoding error details: \(error.localizedDescription)")
                if let decodingError = error as? DecodingError {
                    print("❌ DecodingError specific info: \(decodingError)")
                }
                throw NetworkError.decodingError(error)
            }
        } catch let error as NetworkError {
            print("❌ NetworkError: \(error.localizedDescription)")
            throw error
        } catch {
            print("❌ Underlying network error: \(error.localizedDescription)")
            print("❌ Error details: \(error)")
            throw NetworkError.networkError(error)
        }
    }
    
    // MARK: - Games
    
    func fetchGames() async throws -> [Game] {
        let urlString = "\(baseURL)/api/games/"
        print("🎮 Fetching games from: \(urlString)")
        
        guard let url = URL(string: urlString) else {
            throw NetworkError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.timeoutInterval = 10.0
        
        if let token = try? KeychainManager.shared.retrieveToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        print("🎮 Sending games request...")
        
        do {
            let (data, response) = try await session.data(for: request)
            print("🎮 Received games response")
            
            guard let httpResponse = response as? HTTPURLResponse else {
                print("❌ Invalid HTTP response")
                throw NetworkError.invalidResponse
            }
            
            print("🎮 Games API status code: \(httpResponse.statusCode)")
            
            guard httpResponse.statusCode == 200 else {
                let message = String(data: data, encoding: .utf8)
                print("❌ Games API error \(httpResponse.statusCode): \(message ?? "No message")")
                throw NetworkError.serverError(statusCode: httpResponse.statusCode, message: message)
            }
            
            // Log the raw JSON response for debugging
            if let jsonString = String(data: data, encoding: .utf8) {
                print("🎮 Raw games JSON response: \(jsonString)")
            }
            
            // The API returns { "games": [Game] } format
            struct GamesResponse: Codable {
                let games: [Game]
            }
            
            do {
                // Use a dedicated decoder for games to avoid snake_case issues
                let gamesDecoder = JSONDecoder()
                gamesDecoder.dateDecodingStrategy = .iso8601
                let response = try gamesDecoder.decode(GamesResponse.self, from: data)
                print("✅ Successfully decoded \(response.games.count) games")
                return response.games
            } catch {
                print("❌ Failed to decode games response: \(error)")
                if let decodingError = error as? DecodingError {
                    print("❌ Games decoding error details: \(decodingError)")
                }
                throw NetworkError.decodingError(error)
            }
        } catch let error as NetworkError {
            throw error
        } catch {
            throw NetworkError.networkError(error)
        }
    }
    
    func fetchGame(gameId: String) async throws -> Game {
        guard let url = URL(string: "\(baseURL)/api/games/\(gameId)") else {
            throw NetworkError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        if let token = try? KeychainManager.shared.retrieveToken() {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.invalidResponse
            }
            
            guard httpResponse.statusCode == 200 else {
                let message = String(data: data, encoding: .utf8)
                throw NetworkError.serverError(statusCode: httpResponse.statusCode, message: message)
            }
            
            do {
                return try decoder.decode(Game.self, from: data)
            } catch {
                throw NetworkError.decodingError(error)
            }
        } catch let error as NetworkError {
            throw error
        } catch {
            throw NetworkError.networkError(error)
        }
    }
    
    // MARK: - Chat
    
    func queryChatBot(query: String, gameSystem: String) async throws -> StructuredChatResponse {
        let urlString = "\(baseURL)/api/chat/query"
        print("💬 Chat query to: \(urlString)")
        print("💬 Query: \(query)")
        print("💬 Game system: \(gameSystem)")
        
        guard let url = URL(string: urlString) else {
            print("❌ Invalid chat URL: \(urlString)")
            throw NetworkError.invalidURL
        }
        
        guard let token = try? KeychainManager.shared.retrieveToken() else {
            print("❌ No auth token for chat")
            throw NetworkError.noToken
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        request.timeoutInterval = 30.0  // Longer timeout for AI responses
        
        struct ChatRequest: Codable {
            let query: String
            let gameSystem: String
            
            enum CodingKeys: String, CodingKey {
                case query
                case gameSystem = "game_system"
            }
        }
        
        let chatRequest = ChatRequest(query: query, gameSystem: gameSystem)
        
        do {
            request.httpBody = try encoder.encode(chatRequest)
            if let bodyString = String(data: request.httpBody!, encoding: .utf8) {
                print("💬 Request body: \(bodyString)")
            }
        } catch {
            print("❌ Failed to encode chat request: \(error)")
            throw NetworkError.encodingError(error)
        }
        
        print("💬 Sending chat request...")
        
        do {
            let (data, response) = try await session.data(for: request)
            print("💬 Received chat response")
            
            guard let httpResponse = response as? HTTPURLResponse else {
                print("❌ Invalid HTTP response type")
                throw NetworkError.invalidResponse
            }
            
            print("💬 Chat API status code: \(httpResponse.statusCode)")
            
            if let jsonString = String(data: data, encoding: .utf8) {
                print("💬 Raw chat response: \(jsonString)")
            }
            
            guard httpResponse.statusCode == 200 else {
                let message = String(data: data, encoding: .utf8)
                print("❌ Chat API error \(httpResponse.statusCode): \(message ?? "No message")")
                throw NetworkError.serverError(statusCode: httpResponse.statusCode, message: message)
            }
            
            do {
                print("💬 Attempting to decode as StructuredChatResponse...")
                // Use a dedicated decoder for chat responses to avoid snake_case conversion conflicts
                let chatDecoder = JSONDecoder()
                chatDecoder.dateDecodingStrategy = .iso8601
                return try chatDecoder.decode(StructuredChatResponse.self, from: data)
            } catch {
                print("❌ Failed to decode as StructuredChatResponse: \(error)")
                // Try to decode as legacy QueryResponse for backward compatibility
                do {
                    print("💬 Attempting to decode as QueryResponse...")
                    // Use a dedicated decoder for legacy responses too
                    let legacyDecoder = JSONDecoder()
                    legacyDecoder.dateDecodingStrategy = .iso8601
                    let legacyResponse = try legacyDecoder.decode(QueryResponse.self, from: data)
                    print("✅ Successfully decoded as QueryResponse")
                    // Convert legacy response to structured format
                    return convertLegacyResponse(legacyResponse, query: query, gameSystem: gameSystem)
                } catch {
                    print("❌ Failed to decode as QueryResponse: \(error)")
                    if let decodingError = error as? DecodingError {
                        print("❌ QueryResponse decoding error details: \(decodingError)")
                    }
                    throw NetworkError.decodingError(error)
                }
            }
        } catch let error as NetworkError {
            print("❌ Chat NetworkError: \(error.localizedDescription)")
            throw error
        } catch {
            print("❌ Chat underlying error: \(error.localizedDescription)")
            print("❌ Chat error details: \(error)")
            throw NetworkError.networkError(error)
        }
    }
    
    private func convertLegacyResponse(_ legacy: QueryResponse, query: String, gameSystem: String) -> StructuredChatResponse {
        let content = legacy.results.isEmpty
            ? "No specific rules found for your query."
            : legacy.results.map { rule in
                "**\(rule.title)**\n\(rule.content)"
            }.joined(separator: "\n\n")
        
        let structuredResponse = StructuredResponse(
            id: UUID().uuidString,
            content: StructuredResponse.ResponseContent(
                summary: StructuredResponse.ResponseContent.Summary(
                    text: content,
                    confidence: 0.8
                ),
                sections: legacy.results.enumerated().map { index, rule in
                    StructuredResponse.ResponseContent.ResponseSection(
                        id: "section_\(index)",
                        title: rule.title,
                        content: rule.content,
                        type: "explanation",
                        level: 1,
                        collapsible: true,
                        expanded: false
                    )
                },
                sources: legacy.results.map { rule in
                    StructuredResponse.ResponseContent.Source(
                        type: "rulebook",
                        reference: rule.chunkMetadata?.sourceFile ?? "Unknown",
                        url: nil,
                        page: nil
                    )
                }
            )
        )
        
        return StructuredChatResponse(
            query: query,
            gameSystem: gameSystem,
            structuredResponse: structuredResponse,
            searchMethod: "legacy",
            timestamp: ISO8601DateFormatter().string(from: Date())
        )
    }
}