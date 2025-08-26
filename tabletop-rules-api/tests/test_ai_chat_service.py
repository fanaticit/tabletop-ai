# tests/test_ai_chat_service.py - Comprehensive tests for AI chat service
import pytest
import os
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.ai_chat_service import AIChatService
from openai import AsyncOpenAI


class TestAIChatService:
    """Test suite for AI Chat Service"""
    
    @pytest.fixture
    def ai_service(self):
        """Create fresh AI service instance for each test"""
        service = AIChatService()
        service.client = None  # Reset client
        service.usage_log = []  # Reset usage log
        return service
    
    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI API response"""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = """**Pawns move one square forward, or two squares forward on their first move.**

Pawns are unique pieces with special movement rules. They move straight forward one square to an unoccupied square. On a pawn's very first move from its starting position, it has the option to advance two squares forward instead of one, provided both squares are unoccupied.

Example: A pawn on e2 can move to e3, or jump to e4 on its first move.

**Related Rules**
• **En Passant**: Special pawn capture rule when opponent pawn moves two squares
• **Pawn Promotion**: Pawns reaching the opposite end transform into any piece"""
        
        mock_response.usage = MagicMock()
        mock_response.usage.prompt_tokens = 150
        mock_response.usage.completion_tokens = 100
        return mock_response
    
    @pytest.fixture
    def sample_rules(self):
        """Sample rules data for testing"""
        return [
            {
                "title": "Pawn Movement and Promotion",
                "content": "Pawns move forward one square, or two squares on first move. They capture diagonally.",
                "category_id": "movement"
            },
            {
                "title": "En Passant",
                "content": "Special pawn capture rule when opponent pawn moves two squares forward.",
                "category_id": "special_moves"
            }
        ]
    
    def test_init(self, ai_service):
        """Test AI service initialization"""
        assert ai_service.client is None
        assert ai_service.usage_log == []
    
    @patch('app.services.ai_chat_service.settings')
    def test_ensure_client_no_api_key(self, mock_settings, ai_service):
        """Test client initialization fails without API key"""
        mock_settings.openai_api_key = None
        
        with pytest.raises(ValueError, match="OpenAI API key not configured"):
            ai_service._ensure_client()
    
    @patch('app.services.ai_chat_service.settings')
    def test_ensure_client_invalid_api_key(self, mock_settings, ai_service):
        """Test client initialization fails with placeholder API key"""
        mock_settings.openai_api_key = "your-openai-api-key-here"
        
        with pytest.raises(ValueError, match="OpenAI API key not configured"):
            ai_service._ensure_client()
    
    @patch('app.services.ai_chat_service.settings')
    @patch('app.services.ai_chat_service.AsyncOpenAI')
    def test_ensure_client_success(self, mock_openai_class, mock_settings, ai_service):
        """Test successful client initialization"""
        mock_settings.openai_api_key = "sk-test-key"
        mock_client = AsyncMock()
        mock_openai_class.return_value = mock_client
        
        ai_service._ensure_client()
        
        assert ai_service.client is mock_client
        mock_openai_class.assert_called_once_with(api_key="sk-test-key")
    
    def test_calculate_cost_gpt4o_mini(self, ai_service):
        """Test cost calculation for GPT-4o-mini"""
        # Test with 1000 input tokens and 500 output tokens
        cost = ai_service._calculate_cost("gpt-4o-mini", 1000, 500)
        
        # Expected: (1000/1M * $0.15) + (500/1M * $0.60) = 0.00015 + 0.0003 = 0.00045
        expected_cost = (1000 / 1_000_000) * 0.15 + (500 / 1_000_000) * 0.60
        assert cost == expected_cost
        assert round(cost, 6) == 0.00045
    
    def test_calculate_cost_unknown_model(self, ai_service):
        """Test cost calculation for unknown model"""
        cost = ai_service._calculate_cost("unknown-model", 1000, 500)
        assert cost == 0.0
    
    def test_log_usage(self, ai_service):
        """Test usage logging functionality"""
        ai_service._log_usage("gpt-4o-mini", 100, 50, 0.001)
        
        assert len(ai_service.usage_log) == 1
        entry = ai_service.usage_log[0]
        
        assert entry["model"] == "gpt-4o-mini"
        assert entry["input_tokens"] == 100
        assert entry["output_tokens"] == 50
        assert entry["total_tokens"] == 150
        assert entry["estimated_cost"] == 0.001
        assert "timestamp" in entry
    
    def test_log_usage_limit(self, ai_service):
        """Test usage log doesn't exceed 100 entries"""
        # Add 105 entries
        for i in range(105):
            ai_service._log_usage("gpt-4o-mini", 10, 5, 0.001)
        
        # Should only keep last 100
        assert len(ai_service.usage_log) == 100
    
    def test_format_rules_context_empty(self, ai_service):
        """Test context formatting with no rules"""
        context = ai_service._format_rules_context([], "test query", "chess")
        assert "No specific rules found in the chess rulebook" in context
    
    def test_format_rules_context_with_rules(self, ai_service, sample_rules):
        """Test context formatting with rules"""
        context = ai_service._format_rules_context(sample_rules, "pawn movement", "chess")
        
        assert "Game: Chess" in context
        assert "User Query: pawn movement" in context
        assert "Pawn Movement and Promotion" in context
        assert "En Passant" in context
        assert "Category: movement" in context
    
    def test_format_rules_context_truncate_long_content(self, ai_service):
        """Test context formatting truncates long content"""
        long_rule = {
            "title": "Long Rule",
            "content": "A" * 600,  # Very long content
            "category_id": "test"
        }
        
        context = ai_service._format_rules_context([long_rule], "test", "chess")
        
        # Should be truncated to 500 chars + "..."
        assert "A" * 500 + "..." in context
    
    def test_create_system_prompt(self, ai_service):
        """Test system prompt creation"""
        prompt = ai_service._create_system_prompt("chess")
        
        assert "chess rules advisor" in prompt.lower()
        assert "RESPONSE FORMAT REQUIREMENTS" in prompt
        assert "Direct Answer" in prompt
        assert "Related Rules" in prompt
    
    @pytest.mark.asyncio
    @patch('app.services.ai_chat_service.settings')
    async def test_generate_rule_response_success(self, mock_settings, ai_service, mock_openai_response, sample_rules):
        """Test successful AI response generation"""
        mock_settings.openai_api_key = "sk-test-key"
        
        # Mock the OpenAI client
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_openai_response
        ai_service.client = mock_client
        
        result = await ai_service.generate_rule_response(
            "How does a pawn move?", 
            "chess", 
            sample_rules
        )
        
        assert result["ai_powered"] is True
        assert result["model"] == "gpt-4o-mini"
        assert "Pawns move one square forward" in result["response"]
        assert result["usage"]["input_tokens"] == 150
        assert result["usage"]["output_tokens"] == 100
        assert result["usage"]["total_tokens"] == 250
        assert result["rules_used"] == 2
        assert result["confidence"] == "high"
        
        # Check usage was logged
        assert len(ai_service.usage_log) == 1
    
    @pytest.mark.asyncio
    async def test_generate_rule_response_api_error(self, ai_service, sample_rules):
        """Test AI response generation with API error"""
        # Don't set API key to trigger error
        
        result = await ai_service.generate_rule_response(
            "test query", 
            "chess", 
            sample_rules
        )
        
        assert result["ai_powered"] is False
        assert result["fallback_required"] is True
        assert "error" in result
        assert result["error_type"] == "ValueError"
    
    @pytest.mark.asyncio
    @patch('app.services.ai_chat_service.settings')
    async def test_generate_rule_response_openai_exception(self, mock_settings, ai_service, sample_rules):
        """Test AI response generation with OpenAI exception"""
        mock_settings.openai_api_key = "sk-test-key"
        
        # Mock client to raise exception
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        ai_service.client = mock_client
        
        result = await ai_service.generate_rule_response(
            "test query", 
            "chess", 
            sample_rules
        )
        
        assert result["ai_powered"] is False
        assert result["fallback_required"] is True
        assert "API Error" in result["error"]
    
    @pytest.mark.asyncio
    @patch('app.services.ai_chat_service.settings')
    async def test_test_connection_success(self, mock_settings, ai_service):
        """Test successful connection test"""
        mock_settings.openai_api_key = "sk-test-key"
        
        # Mock successful response
        mock_response = MagicMock()
        mock_response.usage.prompt_tokens = 5
        mock_response.usage.completion_tokens = 3
        
        mock_client = AsyncMock()
        mock_client.chat.completions.create.return_value = mock_response
        ai_service.client = mock_client
        
        result = await ai_service.test_connection()
        
        assert result["success"] is True
        assert result["model"] == "gpt-4o-mini"
        assert "response_time" in result
        assert "test_cost" in result
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, ai_service):
        """Test connection test failure"""
        result = await ai_service.test_connection()
        
        assert result["success"] is False
        assert "error" in result
        assert result["error_type"] == "ValueError"
    
    def test_get_usage_summary_empty(self, ai_service):
        """Test usage summary with no usage"""
        summary = ai_service.get_usage_summary()
        
        assert summary["total_requests"] == 0
        assert summary["total_cost"] == 0.0
        assert summary["total_tokens"] == 0
        assert summary["average_cost_per_request"] == 0
    
    def test_get_usage_summary_with_data(self, ai_service):
        """Test usage summary with data"""
        # Add some usage entries
        ai_service._log_usage("gpt-4o-mini", 100, 50, 0.001)
        ai_service._log_usage("gpt-4o-mini", 200, 100, 0.002)
        
        summary = ai_service.get_usage_summary()
        
        assert summary["total_requests"] == 2
        assert summary["total_cost"] == 0.003
        assert summary["total_tokens"] == 450  # (100+50) + (200+100)
        assert summary["average_cost_per_request"] == 0.0015
    
    @pytest.mark.asyncio
    async def test_close(self, ai_service):
        """Test client close"""
        mock_client = AsyncMock()
        ai_service.client = mock_client
        
        await ai_service.close()
        
        mock_client.aclose.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])