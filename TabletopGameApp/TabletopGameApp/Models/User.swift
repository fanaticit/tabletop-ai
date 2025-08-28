//
//  User.swift
//  TabletopGameApp
//
//  Created by Claude on 27/08/2025.
//

import Foundation

struct User: Codable, Identifiable {
    let id: String
    let email: String
    let username: String
    var preferences: UserPreferences
    
    struct UserPreferences: Codable {
        var selectedGameId: String?
        var theme: Theme
        
        enum Theme: String, Codable, CaseIterable {
            case light = "light"
            case dark = "dark"
            case system = "system"
        }
    }
}

struct TokenResponse: Codable {
    let access_token: String  // Use exact JSON key names to avoid any CodingKeys issues
    let token_type: String
    let expires_in: Int?
    let user: TokenUser?
    
    struct TokenUser: Codable {
        let id: String
        let username: String
        let email: String
    }
}

struct Game: Codable, Identifiable, Hashable {
    let game_id: String
    let name: String
    let description: String
    let complexity: String
    let min_players: Int
    let max_players: Int
    let rule_count: Int
    let publisher: String?
    let categories: [String]?
    let ai_tags: [String]?
    let created_at: Date?
    
    var id: String { game_id }
    
    // Provide defaults for optional fields that may not be in API response
    var safeCategories: [String] {
        return categories ?? []
    }
    
    var safeAiTags: [String] {
        return ai_tags ?? []
    }
}

struct ChatMessage: Codable, Identifiable {
    let id: String
    let role: MessageRole
    let content: String
    let gameId: String?
    let timestamp: Date
    var structuredResponse: StructuredResponse?
    var sources: [RuleChunk]?
    
    enum MessageRole: String, Codable {
        case user = "user"
        case assistant = "assistant"
    }
    
    init(id: String = UUID().uuidString, role: MessageRole, content: String, gameId: String? = nil, timestamp: Date = Date(), structuredResponse: StructuredResponse? = nil, sources: [RuleChunk]? = nil) {
        self.id = id
        self.role = role
        self.content = content
        self.gameId = gameId
        self.timestamp = timestamp
        self.structuredResponse = structuredResponse
        self.sources = sources
    }
}

struct StructuredResponse: Codable {
    let id: String
    let content: ResponseContent
    
    struct ResponseContent: Codable {
        let summary: Summary
        let sections: [ResponseSection]
        let sources: [Source]
        
        struct Summary: Codable {
            let text: String
            let confidence: Double
        }
        
        struct ResponseSection: Codable {
            let id: String
            let title: String
            let content: String
            let type: String
            let level: Int
            let collapsible: Bool
            let expanded: Bool
        }
        
        struct Source: Codable {
            let type: String
            let reference: String
            let url: String?
            let page: Int?
        }
    }
}

struct RuleChunk: Codable, Identifiable {
    let gameId: String
    let categoryId: String
    let title: String
    let content: String
    let chunkMetadata: ChunkMetadata?
    
    var id: String { "\(gameId)-\(categoryId)-\(title)" }
    
    enum CodingKeys: String, CodingKey {
        case gameId = "game_id"
        case categoryId = "category_id"
        case title, content
        case chunkMetadata = "chunk_metadata"
    }
    
    struct ChunkMetadata: Codable {
        let sourceFile: String?
        let uploadedWithoutAi: Bool?
        
        enum CodingKeys: String, CodingKey {
            case sourceFile = "source_file"
            case uploadedWithoutAi = "uploaded_without_ai"
        }
    }
}

struct StructuredChatResponse: Codable {
    let query: String
    let gameSystem: String
    let structuredResponse: StructuredResponse
    let searchMethod: String
    let timestamp: String
    
    enum CodingKeys: String, CodingKey {
        case query
        case gameSystem = "game_system"
        case structuredResponse = "structured_response"
        case searchMethod = "search_method"
        case timestamp
    }
}

struct QueryResponse: Codable {
    let results: [RuleChunk]
    let query: String
}