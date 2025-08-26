# tests/test_chat_endpoints.py - Comprehensive tests for chat API endpoints with AI integration
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestChatEndpoints:
    """Test suite for chat API endpoints"""
    
    @pytest.fixture
    def mock_game_data(self):
        """Mock game data for testing"""
        return {
            "game_id": "chess",
            "name": "Chess",
            "publisher": "FIDE",
            "version": "Official Rules",
            "complexity": "medium",
            "min_players": 2,
            "max_players": 2
        }
    
    @pytest.fixture
    def mock_rules_data(self):
        """Mock rules data for testing"""
        return [
            {
                "game_id": "chess",
                "category_id": "chess_movement", 
                "title": "Pawn Movement",
                "content": "Pawns move forward one square, or two squares on their first move.",
                "ancestors": ["chess", "chess_rules"],
                "chunk_metadata": {
                    "source_file": "chess_rules.md",
                    "section_index": 0,
                    "tokens": 50,
                    "complexity_score": 0.3
                }
            },
            {
                "game_id": "chess", 
                "category_id": "chess_movement",
                "title": "Bishop Movement",
                "content": "Bishops move diagonally any number of squares.",
                "ancestors": ["chess", "chess_rules"], 
                "chunk_metadata": {
                    "source_file": "chess_rules.md",
                    "section_index": 1,
                    "tokens": 30,
                    "complexity_score": 0.2
                }
            }
        ]
    
    @pytest.fixture
    def mock_ai_response(self):
        """Mock AI service response"""
        return {
            "response": """**Pawns move one square forward, or two squares forward on their first move.**

Pawns are unique pieces with special movement rules. They move straight forward one square to an unoccupied square. On a pawn's very first move from its starting position, it has the option to advance two squares forward instead of one, provided both squares are unoccupied.

Example: A pawn on e2 can move to e3, or jump to e4 on its first move.

**Related Rules**
• **En Passant**: Special pawn capture rule when opponent pawn moves two squares
• **Pawn Promotion**: Pawns reaching the opposite end transform into any piece""",
            "ai_powered": True,
            "model": "gpt-4o-mini",
            "response_time": 1.2,
            "usage": {
                "input_tokens": 150,
                "output_tokens": 100,
                "total_tokens": 250,
                "estimated_cost": 0.00045
            },
            "rules_used": 2,
            "confidence": "high"
        }
    
    @pytest.mark.asyncio
    @patch('app.routes.chat.games_collection')
    @patch('app.routes.chat.content_collection')
    async def test_chat_query_basic_success(self, mock_content, mock_games, mock_game_data, mock_rules_data):
        """Test basic chat query without AI"""
        # Mock database responses
        mock_games.find_one.return_value = mock_game_data
        mock_content_cursor = AsyncMock()
        mock_content_cursor.to_list.return_value = mock_rules_data
        mock_content.find.return_value = mock_content_cursor
        
        response = client.post(
            "/api/chat/query",
            json={"query": "How do pawns move?", "game_system": "chess"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["query"] == "How do pawns move?"
        assert data["game_system"] == "chess"
        assert "structured_response" in data
        assert data["search_method"] in ["intelligent_scoring", "ai_powered_gpt4o_mini"]
        
        # Verify structured response format
        structured = data["structured_response"]
        assert "summary" in structured
        assert "sections" in structured
        assert "sources" in structured
    
    @patch('app.routes.chat.games_collection')
    @patch('app.routes.chat.content_collection') 
    @patch('app.routes.chat.ai_chat_service')
    def test_chat_query_ai_powered_success(self, mock_ai_service, mock_content, mock_games, 
                                         mock_game_data, mock_rules_data, mock_ai_response):
        """Test AI-powered chat query success"""
        # Mock database responses
        mock_games.find_one.return_value = mock_game_data
        mock_content_cursor = AsyncMock()
        mock_content_cursor.to_list.return_value = mock_rules_data
        mock_content.find.return_value = mock_content_cursor
        
        # Mock AI service success
        mock_ai_service.generate_rule_response.return_value = mock_ai_response
        
        response = client.post(
            "/api/chat/query",
            json={"query": "How do pawns move?", "game_system": "chess"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["search_method"] == "ai_powered_gpt4o_mini"
        
        # Verify AI service was called
        mock_ai_service.generate_rule_response.assert_called_once_with(
            query="How do pawns move?",
            game_id="chess",
            rules_context=mock_rules_data
        )
        
        # Verify structured response includes AI data
        structured = data["structured_response"]
        assert structured["summary"]["text"] == "Pawns move one square forward, or two squares forward on their first move."
        assert structured["ai_metadata"]["model"] == "gpt-4o-mini"
        assert structured["ai_metadata"]["usage"]["total_tokens"] == 250
    
    @patch('app.routes.chat.games_collection')
    @patch('app.routes.chat.content_collection')
    @patch('app.routes.chat.ai_chat_service')
    def test_chat_query_ai_fallback_behavior(self, mock_ai_service, mock_content, mock_games,
                                           mock_game_data, mock_rules_data):
        """Test fallback to template response when AI fails"""
        # Mock database responses
        mock_games.find_one.return_value = mock_game_data
        mock_content_cursor = AsyncMock()
        mock_content_cursor.to_list.return_value = mock_rules_data
        mock_content.find.return_value = mock_content_cursor
        
        # Mock AI service failure
        mock_ai_service.generate_rule_response.return_value = {
            "error": "OpenAI API key not configured",
            "ai_powered": False,
            "fallback_required": True,
            "error_type": "ValueError"
        }
        
        response = client.post(
            "/api/chat/query",
            json={"query": "How do pawns move?", "game_system": "chess"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should fallback to intelligent scoring
        assert data["search_method"] == "intelligent_scoring"
        
        # Should still have structured response
        structured = data["structured_response"]
        assert "summary" in structured
        assert "sections" in structured
        assert structured["summary"]["confidence"] > 0
        
        # Should not have AI metadata
        assert "ai_metadata" not in structured
    
    @patch('app.routes.chat.games_collection')
    def test_chat_query_game_not_found(self, mock_games):
        """Test chat query with non-existent game"""
        mock_games.find_one.return_value = None
        
        response = client.post(
            "/api/chat/query",
            json={"query": "How to play?", "game_system": "nonexistent-game"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "Game 'nonexistent-game' not found" in data["detail"]
    
    @patch('app.routes.chat.games_collection')
    @patch('app.routes.chat.content_collection')
    def test_chat_query_no_rules_found(self, mock_content, mock_games, mock_game_data):
        """Test chat query when no rules match"""
        # Mock database responses
        mock_games.find_one.return_value = mock_game_data
        mock_content_cursor = AsyncMock()
        mock_content_cursor.to_list.return_value = []  # No rules found
        mock_content.find.return_value = mock_content_cursor
        
        response = client.post(
            "/api/chat/query",
            json={"query": "How do dragons move?", "game_system": "chess"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        structured = data["structured_response"]
        assert "no specific rules found" in structured["summary"]["text"].lower()
        assert structured["summary"]["confidence"] == 0.1  # Low confidence
        assert len(structured["sections"]) == 0
    
    def test_chat_query_invalid_request_body(self):
        """Test chat query with invalid request body"""
        response = client.post(
            "/api/chat/query",
            json={"query": ""}  # Missing game_system
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_chat_query_missing_query(self):
        """Test chat query with missing query"""
        response = client.post(
            "/api/chat/query",
            json={"game_system": "chess"}  # Missing query
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('app.routes.chat.games_collection')
    @patch('app.routes.chat.content_collection')
    def test_chat_query_database_error_handling(self, mock_content, mock_games, mock_game_data):
        """Test chat query handles database errors gracefully"""
        # Mock database responses
        mock_games.find_one.return_value = mock_game_data
        mock_content.find.side_effect = Exception("Database connection error")
        
        response = client.post(
            "/api/chat/query", 
            json={"query": "How do pawns move?", "game_system": "chess"}
        )
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data["detail"].lower()
    
    @patch('app.routes.chat.games_collection')
    @patch('app.routes.chat.content_collection')
    def test_chat_query_long_query_handling(self, mock_content, mock_games, mock_game_data, mock_rules_data):
        """Test chat query with very long input"""
        # Mock database responses
        mock_games.find_one.return_value = mock_game_data
        mock_content_cursor = AsyncMock()
        mock_content_cursor.to_list.return_value = mock_rules_data
        mock_content.find.return_value = mock_content_cursor
        
        long_query = "How do pawns move? " * 100  # Very long query
        
        response = client.post(
            "/api/chat/query",
            json={"query": long_query, "game_system": "chess"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == long_query
        assert "structured_response" in data
    
    @patch('app.routes.chat.games_collection')
    @patch('app.routes.chat.content_collection')
    def test_chat_query_special_characters(self, mock_content, mock_games, mock_game_data, mock_rules_data):
        """Test chat query with special characters"""
        # Mock database responses
        mock_games.find_one.return_value = mock_game_data
        mock_content_cursor = AsyncMock()
        mock_content_cursor.to_list.return_value = mock_rules_data
        mock_content.find.return_value = mock_content_cursor
        
        special_query = "How do pawns move? 🎲 ♟️ ♞"
        
        response = client.post(
            "/api/chat/query",
            json={"query": special_query, "game_system": "chess"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == special_query
        assert "structured_response" in data
    
    @patch('app.routes.chat.games_collection') 
    @patch('app.routes.chat.content_collection')
    @patch('app.routes.chat.ai_chat_service')
    def test_chat_query_ai_timeout_fallback(self, mock_ai_service, mock_content, mock_games,
                                          mock_game_data, mock_rules_data):
        """Test fallback when AI service times out"""
        # Mock database responses
        mock_games.find_one.return_value = mock_game_data
        mock_content_cursor = AsyncMock()
        mock_content_cursor.to_list.return_value = mock_rules_data
        mock_content.find.return_value = mock_content_cursor
        
        # Mock AI service timeout
        mock_ai_service.generate_rule_response.side_effect = Exception("Request timeout")
        
        response = client.post(
            "/api/chat/query",
            json={"query": "How do pawns move?", "game_system": "chess"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should fallback to intelligent scoring
        assert data["search_method"] == "intelligent_scoring"
        assert "structured_response" in data
    
    @patch('app.routes.chat.games_collection')
    @patch('app.routes.chat.content_collection')
    def test_chat_query_piece_specific_scoring(self, mock_content, mock_games, mock_game_data):
        """Test intelligent scoring for piece-specific queries"""
        # Mock database responses with multiple piece types
        mock_games.find_one.return_value = mock_game_data
        
        piece_rules = [
            {
                "title": "Pawn Movement", 
                "content": "Pawns move forward one square",
                "category_id": "chess_movement"
            },
            {
                "title": "Knight Movement",
                "content": "Knights move in L-shape",
                "category_id": "chess_movement"
            },
            {
                "title": "General Rules",
                "content": "All pieces must follow basic rules",
                "category_id": "chess_general"
            }
        ]
        
        mock_content_cursor = AsyncMock()
        mock_content_cursor.to_list.return_value = piece_rules
        mock_content.find.return_value = mock_content_cursor
        
        response = client.post(
            "/api/chat/query",
            json={"query": "How do pawns move?", "game_system": "chess"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should prioritize pawn-related content
        structured = data["structured_response"]
        assert "pawn" in structured["summary"]["text"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])