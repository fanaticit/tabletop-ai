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
    private let baseURL = "http://localhost:8000"
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
                return "Authentication failed. Please check your credentials."
            case .serverError(let statusCode, let message):
                return message ?? "Server error (\(statusCode))"
            case .decodingError:
                return "Failed to decode response"
            case .encodingError:
                return "Failed to encode request"
            case .networkError(let error):
                return "Network error: \(error.localizedDescription)"
            case .noToken:
                return "No authentication token available"
            }
        }
    }
    
    // MARK: - Authentication
    
    func authenticateUser(username: String, password: String) async throws -> TokenResponse {
        guard let url = URL(string: "\(baseURL)/token") else {
            throw NetworkError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/x-www-form-urlencoded", forHTTPHeaderField: "Content-Type")
        
        let formData = "username=\(username)&password=\(password)"
            .addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? ""
        request.httpBody = formData.data(using: .utf8)
        
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                throw NetworkError.invalidResponse
            }
            
            if httpResponse.statusCode == 422 {
                throw NetworkError.authenticationFailed
            }
            
            guard httpResponse.statusCode == 200 else {
                let message = String(data: data, encoding: .utf8)
                throw NetworkError.serverError(statusCode: httpResponse.statusCode, message: message)
            }
            
            do {
                return try decoder.decode(TokenResponse.self, from: data)
            } catch {
                throw NetworkError.decodingError(error)
            }
        } catch let error as NetworkError {
            throw error
        } catch {
            throw NetworkError.networkError(error)
        }
    }
    
    // MARK: - Games
    
    func fetchGames() async throws -> [Game] {
        guard let url = URL(string: "\(baseURL)/api/games/") else {
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
            
            // The API returns { "games": [Game] } format
            struct GamesResponse: Codable {
                let games: [Game]
            }
            
            do {
                let response = try decoder.decode(GamesResponse.self, from: data)
                return response.games
            } catch {
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
        guard let url = URL(string: "\(baseURL)/api/chat/query") else {
            throw NetworkError.invalidURL
        }
        
        guard let token = try? KeychainManager.shared.retrieveToken() else {
            throw NetworkError.noToken
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
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
        } catch {
            throw NetworkError.encodingError(error)
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
                return try decoder.decode(StructuredChatResponse.self, from: data)
            } catch {
                // Try to decode as legacy QueryResponse for backward compatibility
                do {
                    let legacyResponse = try decoder.decode(QueryResponse.self, from: data)
                    // Convert legacy response to structured format
                    return convertLegacyResponse(legacyResponse, query: query, gameSystem: gameSystem)
                } catch {
                    throw NetworkError.decodingError(error)
                }
            }
        } catch let error as NetworkError {
            throw error
        } catch {
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