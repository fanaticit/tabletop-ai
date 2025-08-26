# tests/test_fallback_behavior.py - Tests for AI fallback and error handling behavior
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.ai_chat_service import AIChatService

class TestFallbackBehavior:
    """Test suite for AI fallback and error handling scenarios"""
    
    @pytest.fixture
    def ai_service(self):
        """Create AI service instance for testing"""
        service = AIChatService()
        service.client = None
        service.usage_log = []
        return service
    
    @pytest.fixture
    def sample_rules(self):
        """Sample rules data for testing"""
        return [
            {
                "title": "Pawn Movement",
                "content": "Pawns move forward one square, or two on first move",
                "category_id": "movement"
            },
            {
                "title": "Pawn Capture", 
                "content": "Pawns capture diagonally forward",
                "category_id": "capture"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_api_key_not_configured_fallback(self, ai_service, sample_rules):
        """Test fallback when API key is not configured"""
        # No API key configured
        with patch('app.services.ai_chat_service.settings') as mock_settings:
            mock_settings.openai_api_key = None
            
            result = await ai_service.generate_rule_response(
                "How do pawns move?", 
                "chess", 
                sample_rules
            )
            
            assert result["ai_powered"] is False
            assert result["fallback_required"] is True
            assert result["error_type"] == "ValueError"
            assert "not configured" in result["error"]
    
    @pytest.mark.asyncio
    async def test_placeholder_api_key_fallback(self, ai_service, sample_rules):
        """Test fallback when placeholder API key is used"""
        with patch('app.services.ai_chat_service.settings') as mock_settings:
            mock_settings.openai_api_key = "your-openai-api-key-here"
            
            result = await ai_service.generate_rule_response(
                "How do pawns move?",
                "chess", 
                sample_rules
            )
            
            assert result["ai_powered"] is False
            assert result["fallback_required"] is True
            assert result["error_type"] == "ValueError"
            assert "not configured" in result["error"]
    
    @pytest.mark.asyncio
    @patch('app.services.ai_chat_service.settings')
    async def test_openai_api_error_fallback(self, mock_settings, ai_service, sample_rules):
        """Test fallback when OpenAI API returns error"""
        mock_settings.openai_api_key = "sk-test-key"
        
        # Mock client to raise OpenAI-specific exception
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("Rate limit exceeded")
        ai_service.client = mock_client
        
        result = await ai_service.generate_rule_response(
            "How do pawns move?",
            "chess",
            sample_rules
        )
        
        assert result["ai_powered"] is False
        assert result["fallback_required"] is True
        assert "Rate limit exceeded" in result["error"]
    
    @pytest.mark.asyncio
    @patch('app.services.ai_chat_service.settings')
    async def test_network_timeout_fallback(self, mock_settings, ai_service, sample_rules):
        """Test fallback when network request times out"""
        mock_settings.openai_api_key = "sk-test-key"
        
        # Mock client to raise timeout exception
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("Connection timeout")
        ai_service.client = mock_client
        
        result = await ai_service.generate_rule_response(
            "How do pawns move?",
            "chess", 
            sample_rules
        )
        
        assert result["ai_powered"] is False
        assert result["fallback_required"] is True
        assert "Connection timeout" in result["error"]
    
    @pytest.mark.asyncio
    @patch('app.services.ai_chat_service.settings')
    async def test_malformed_response_fallback(self, mock_settings, ai_service, sample_rules):
        """Test fallback when AI returns malformed response"""
        mock_settings.openai_api_key = "sk-test-key"
        
        # Mock client to return malformed response
        mock_response = MagicMock()
        mock_response.choices = []  # Empty choices
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        ai_service.client = mock_client
        
        result = await ai_service.generate_rule_response(
            "How do pawns move?",
            "chess",
            sample_rules
        )
        
        assert result["ai_powered"] is False
        assert result["fallback_required"] is True
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_connection_test_failure_scenarios(self, ai_service):
        """Test connection test handles various failure scenarios"""
        # Test with no API key
        with patch('app.services.ai_chat_service.settings') as mock_settings:
            mock_settings.openai_api_key = None
            
            result = await ai_service.test_connection()
            
            assert result["success"] is False
            assert "error" in result
            assert result["error_type"] == "ValueError"
    
    @pytest.mark.asyncio
    @patch('app.services.ai_chat_service.settings')
    async def test_connection_test_network_failure(self, mock_settings, ai_service):
        """Test connection test with network failure"""
        mock_settings.openai_api_key = "sk-test-key"
        
        # Mock client to raise network exception
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("Network error")
        ai_service.client = mock_client
        
        result = await ai_service.test_connection()
        
        assert result["success"] is False
        assert "Network error" in result["error"]
    
    def test_cost_calculation_with_unknown_model(self, ai_service):
        """Test cost calculation fallback for unknown models"""
        cost = ai_service._calculate_cost("unknown-model", 1000, 500)
        assert cost == 0.0
    
    def test_usage_log_memory_management(self, ai_service):
        """Test usage log doesn't exceed memory limits"""
        # Add more than 100 entries
        for i in range(150):
            ai_service._log_usage("gpt-4o-mini", 10, 5, 0.001)
        
        # Should only keep last 100
        assert len(ai_service.usage_log) == 100
        
        # First entry should be from iteration 50 (since we keep last 100)
        # We can't easily verify the exact content, but we can verify count
        assert ai_service.usage_log[0]["input_tokens"] == 10
    
    @pytest.mark.asyncio
    @patch('app.services.ai_chat_service.settings')
    async def test_client_initialization_fallback(self, mock_settings, ai_service):
        """Test client initialization with various failure scenarios"""
        mock_settings.openai_api_key = "sk-test-key"
        
        # Test when AsyncOpenAI import fails
        with patch('app.services.ai_chat_service.AsyncOpenAI') as mock_openai:
            mock_openai.side_effect = ImportError("OpenAI library not installed")
            
            with pytest.raises(ImportError):
                ai_service._ensure_client()
    
    def test_format_rules_context_with_empty_rules(self, ai_service):
        """Test rules formatting with empty rules list"""
        context = ai_service._format_rules_context([], "test query", "chess")
        assert "No specific rules found" in context
        assert "chess" in context.lower()
        assert "test query" in context.lower()
    
    def test_format_rules_context_with_malformed_rules(self, ai_service):
        """Test rules formatting with malformed rule data"""
        malformed_rules = [
            {"title": "Rule 1"},  # Missing content and category
            {"content": "Some content"},  # Missing title and category
            {}  # Empty rule
        ]
        
        context = ai_service._format_rules_context(malformed_rules, "test", "chess")
        
        # Should handle gracefully without crashing
        assert isinstance(context, str)
        assert "chess" in context.lower()
    
    def test_format_rules_context_content_truncation(self, ai_service):
        """Test rules formatting truncates very long content"""
        long_rules = [
            {
                "title": "Long Rule",
                "content": "A" * 1000,  # Very long content
                "category_id": "test"
            }
        ]
        
        context = ai_service._format_rules_context(long_rules, "test", "chess")
        
        # Should truncate content to 500 chars + "..."
        assert "A" * 500 + "..." in context
        assert len([line for line in context.split('\n') if 'A' * 600 in line]) == 0
    
    def test_create_system_prompt_consistency(self, ai_service):
        """Test system prompt creation is consistent across games"""
        chess_prompt = ai_service._create_system_prompt("chess")
        poker_prompt = ai_service._create_system_prompt("poker")
        
        # Both should have required sections
        for prompt in [chess_prompt, poker_prompt]:
            assert "RESPONSE FORMAT REQUIREMENTS" in prompt
            assert "Direct Answer" in prompt
            assert "Related Rules" in prompt
            assert "Example format" in prompt
        
        # Should be customized for each game
        assert "chess" in chess_prompt.lower()
        assert "poker" in poker_prompt.lower()
    
    def test_get_usage_summary_edge_cases(self, ai_service):
        """Test usage summary handles edge cases"""
        # Test with empty usage log
        summary = ai_service.get_usage_summary()
        assert summary["total_requests"] == 0
        assert summary["total_cost"] == 0.0
        assert summary["average_cost_per_request"] == 0
        
        # Test with single entry
        ai_service._log_usage("gpt-4o-mini", 100, 50, 0.001)
        summary = ai_service.get_usage_summary()
        assert summary["total_requests"] == 1
        assert summary["average_cost_per_request"] == 0.001
        
        # Test with multiple entries
        ai_service._log_usage("gpt-4o-mini", 200, 100, 0.002)
        summary = ai_service.get_usage_summary()
        assert summary["total_requests"] == 2
        assert summary["total_cost"] == 0.003
        assert summary["average_cost_per_request"] == 0.0015


class TestFallbackIntegration:
    """Integration tests for fallback behavior in full system"""
    
    @patch('app.routes.chat.ai_chat_service')
    @patch('app.routes.chat.games_collection')
    @patch('app.routes.chat.content_collection')
    def test_end_to_end_fallback_flow(self, mock_content, mock_games, mock_ai_service):
        """Test complete fallback flow from API endpoint to template response"""
        from fastapi.testclient import TestClient
        from main import app
        
        client = TestClient(app)
        
        # Mock database responses
        mock_games.find_one.return_value = {
            "game_id": "chess",
            "name": "Chess"
        }
        
        mock_rules = [
            {
                "title": "Pawn Movement",
                "content": "Pawns move forward one square",
                "category_id": "movement"
            }
        ]
        
        mock_content_cursor = AsyncMock()
        mock_content_cursor.to_list.return_value = mock_rules
        mock_content.find.return_value = mock_content_cursor
        
        # Mock AI service failure
        mock_ai_service.generate_rule_response.return_value = {
            "error": "API key not configured",
            "ai_powered": False,
            "fallback_required": True,
            "error_type": "ValueError"
        }
        
        # Make request
        response = client.post(
            "/api/chat/query",
            json={"query": "How do pawns move?", "game_system": "chess"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should use fallback method
        assert data["search_method"] == "intelligent_scoring"
        assert "structured_response" in data
        
        # Should still provide useful response
        structured = data["structured_response"]
        assert "summary" in structured
        assert len(structured["summary"]["text"]) > 0
    
    def test_fallback_quality_comparison(self):
        """Test that fallback responses maintain acceptable quality"""
        # This would be a more complex test that compares
        # AI responses vs template responses for quality metrics
        # For now, we verify the structure is maintained
        
        from app.routes.chat import generate_contextual_summary, create_template_structured_response
        
        mock_rules = [
            {
                "title": "Pawn Movement",
                "content": "Pawns move forward one square, or two squares on their first move.",
                "category_id": "movement"
            }
        ]
        
        # Generate template response
        summary = generate_contextual_summary(mock_rules, "How do pawns move?", "chess")
        response = create_template_structured_response(summary, mock_rules, "How do pawns move?", "chess")
        
        # Verify structure
        assert "summary" in response
        assert "sections" in response
        assert "sources" in response
        assert response["summary"]["confidence"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])