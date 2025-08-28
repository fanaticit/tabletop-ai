//
//  MessageBubble.swift
//  TabletopGameApp
//
//  Created by Claude on 27/08/2025.
//

import SwiftUI

struct MessageBubble: View {
    let message: ChatMessage
    let game: Game
    
    var body: some View {
        HStack {
            if message.role == .user {
                Spacer(minLength: 60)
                userMessage
            } else {
                assistantMessage
                Spacer(minLength: 60)
            }
        }
    }
    
    // MARK: - User Message
    
    private var userMessage: some View {
        VStack(alignment: .trailing, spacing: 4) {
            Text(message.content)
                .font(.system(size: 16))
                .foregroundColor(.white)
                .padding(.horizontal, 16)
                .padding(.vertical, 12)
                .background(
                    RoundedRectangle(cornerRadius: 20)
                        .fill(Color.gamingAccent)
                )
            
            Text(formatTime(message.timestamp))
                .font(.system(size: 12))
                .foregroundColor(.gamingSecondary)
        }
    }
    
    // MARK: - Assistant Message
    
    private var assistantMessage: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack(spacing: 8) {
                Text("🤖")
                    .font(.system(size: 16))
                
                Text("AI Assistant")
                    .font(.system(size: 14, weight: .medium))
                    .foregroundColor(.gamingText)
            }
            
            VStack(alignment: .leading, spacing: 12) {
                if let structuredResponse = message.structuredResponse {
                    StructuredResponseView(response: structuredResponse)
                } else {
                    // Fallback to plain text
                    Text(message.content)
                        .font(.system(size: 16))
                        .foregroundColor(.gamingText)
                        .fixedSize(horizontal: false, vertical: true)
                }
                
                // Sources section
                if let sources = message.sources, !sources.isEmpty {
                    SourcesView(sources: sources)
                }
                
                // Timestamp
                HStack {
                    Text(formatTime(message.timestamp))
                        .font(.system(size: 12))
                        .foregroundColor(.gamingSecondary)
                    
                    Spacer()
                    
                    if let structuredResponse = message.structuredResponse {
                        Text("Confidence: \(Int(structuredResponse.content.summary.confidence * 100))%")
                            .font(.system(size: 12))
                            .foregroundColor(.gamingAccent)
                    }
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 12)
            .background(
                RoundedRectangle(cornerRadius: 16)
                    .fill(Color.gamingPrimary)
                    .overlay(
                        RoundedRectangle(cornerRadius: 16)
                            .stroke(Color.gamingSecondary.opacity(0.2), lineWidth: 1)
                    )
            )
        }
    }
    
    private func formatTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

// MARK: - Structured Response View

struct StructuredResponseView: View {
    let response: StructuredResponse
    @State private var expandedSections: Set<String> = []
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            // Summary
            Text(response.content.summary.text)
                .font(.system(size: 16, weight: .medium))
                .foregroundColor(.gamingText)
                .fixedSize(horizontal: false, vertical: true)
            
            // Sections
            if !response.content.sections.isEmpty {
                VStack(alignment: .leading, spacing: 8) {
                    ForEach(response.content.sections, id: \.id) { section in
                        SectionView(
                            section: section,
                            isExpanded: expandedSections.contains(section.id)
                        ) {
                            if expandedSections.contains(section.id) {
                                expandedSections.remove(section.id)
                            } else {
                                expandedSections.insert(section.id)
                            }
                        }
                    }
                }
            }
        }
    }
}

// MARK: - Section View

struct SectionView: View {
    let section: StructuredResponse.ResponseContent.ResponseSection
    let isExpanded: Bool
    let onToggle: () -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            if section.collapsible {
                Button(action: onToggle) {
                    HStack {
                        Text(section.title)
                            .font(.system(size: 14, weight: .semibold))
                            .foregroundColor(.gamingAccent)
                        
                        Spacer()
                        
                        Image(systemName: isExpanded ? "chevron.down" : "chevron.right")
                            .font(.system(size: 12, weight: .medium))
                            .foregroundColor(.gamingAccent)
                    }
                }
                .buttonStyle(PlainButtonStyle())
                
                if isExpanded || section.expanded {
                    Text(section.content)
                        .font(.system(size: 14))
                        .foregroundColor(.gamingSecondary)
                        .fixedSize(horizontal: false, vertical: true)
                        .padding(.leading, 8)
                }
            } else {
                Text(section.title)
                    .font(.system(size: 14, weight: .semibold))
                    .foregroundColor(.gamingAccent)
                
                Text(section.content)
                    .font(.system(size: 14))
                    .foregroundColor(.gamingSecondary)
                    .fixedSize(horizontal: false, vertical: true)
                    .padding(.leading, 8)
            }
        }
        .padding(.vertical, 4)
    }
}

// MARK: - Sources View

struct SourcesView: View {
    let sources: [RuleChunk]
    @State private var isExpanded = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Button(action: { isExpanded.toggle() }) {
                HStack {
                    Image(systemName: "book.fill")
                        .font(.system(size: 12))
                        .foregroundColor(.gamingAccent)
                    
                    Text("Sources (\(sources.count))")
                        .font(.system(size: 12, weight: .medium))
                        .foregroundColor(.gamingAccent)
                    
                    Spacer()
                    
                    Image(systemName: isExpanded ? "chevron.down" : "chevron.right")
                        .font(.system(size: 10, weight: .medium))
                        .foregroundColor(.gamingAccent)
                }
            }
            .buttonStyle(PlainButtonStyle())
            
            if isExpanded {
                VStack(alignment: .leading, spacing: 6) {
                    ForEach(sources.prefix(3), id: \.id) { source in
                        HStack(spacing: 8) {
                            Circle()
                                .fill(Color.gamingAccent)
                                .frame(width: 4, height: 4)
                            
                            VStack(alignment: .leading, spacing: 2) {
                                Text(source.title)
                                    .font(.system(size: 12, weight: .medium))
                                    .foregroundColor(.gamingText)
                                
                                if let sourceFile = source.chunkMetadata?.sourceFile {
                                    Text("From: \(sourceFile)")
                                        .font(.system(size: 10))
                                        .foregroundColor(.gamingSecondary)
                                }
                            }
                            
                            Spacer()
                        }
                    }
                    
                    if sources.count > 3 {
                        Text("and \(sources.count - 3) more...")
                            .font(.system(size: 12))
                            .foregroundColor(.gamingSecondary)
                            .padding(.leading, 12)
                    }
                }
                .padding(.leading, 8)
            }
        }
        .padding(.vertical, 8)
        .padding(.horizontal, 12)
        .background(
            RoundedRectangle(cornerRadius: 8)
                .fill(Color.gamingBackground)
                .overlay(
                    RoundedRectangle(cornerRadius: 8)
                        .stroke(Color.gamingAccent.opacity(0.2), lineWidth: 1)
                )
        )
    }
}

#Preview {
    let sampleGame = Game(
        game_id: "chess",
        name: "Chess",
        description: "Classic strategy game",
        complexity: "medium",
        min_players: 2,
        max_players: 2,
        rule_count: 15,
        publisher: nil,
        categories: ["strategy"],
        ai_tags: ["classic"],
        created_at: Date()
    )
    
    let sampleMessage = ChatMessage(
        role: .assistant,
        content: "Pawns move forward one square, but capture diagonally.",
        gameId: "chess"
    )
    
    VStack {
        MessageBubble(message: sampleMessage, game: sampleGame)
        
        MessageBubble(
            message: ChatMessage(role: .user, content: "How do pawns move?", gameId: "chess"),
            game: sampleGame
        )
    }
    .padding()
    .background(Color.gamingBackground)
    .preferredColorScheme(.dark)
}