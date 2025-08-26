# tests/test_api_integration.py - Simple integration tests for API functionality
import pytest
import json
from unittest.mock import patch, MagicMock

class TestAPIIntegration:
    """Integration tests for API endpoints"""
    
    def test_ai_chat_service_import(self):
        """Test that AI chat service can be imported"""
        from app.services.ai_chat_service import AIChatService, ai_chat_service
        
        assert AIChatService is not None
        assert ai_chat_service is not None
        assert hasattr(ai_chat_service, 'generate_rule_response')
        assert hasattr(ai_chat_service, 'test_connection')
        assert hasattr(ai_chat_service, 'get_usage_summary')
    
    def test_ai_service_initialization(self):
        """Test AI service initializes correctly"""
        from app.services.ai_chat_service import AIChatService
        
        service = AIChatService()
        assert service.client is None
        assert service.usage_log == []
    
    def test_cost_calculation(self):
        """Test cost calculation works correctly"""
        from app.services.ai_chat_service import AIChatService
        
        service = AIChatService()
        
        # Test GPT-4o-mini pricing
        cost = service._calculate_cost("gpt-4o-mini", 1000, 500)
        expected = (1000 / 1_000_000) * 0.15 + (500 / 1_000_000) * 0.60
        assert cost == expected
        assert round(cost, 6) == 0.00045
        
        # Test unknown model
        cost_unknown = service._calculate_cost("unknown", 1000, 500)
        assert cost_unknown == 0.0
    
    def test_usage_logging(self):
        """Test usage logging functionality"""
        from app.services.ai_chat_service import AIChatService
        
        service = AIChatService()
        service._log_usage("gpt-4o-mini", 100, 50, 0.001)
        
        assert len(service.usage_log) == 1
        entry = service.usage_log[0]
        assert entry["model"] == "gpt-4o-mini"
        assert entry["input_tokens"] == 100
        assert entry["output_tokens"] == 50
        assert entry["total_tokens"] == 150
        assert entry["estimated_cost"] == 0.001
        assert "timestamp" in entry
    
    def test_usage_summary_empty(self):
        """Test usage summary with empty log"""
        from app.services.ai_chat_service import AIChatService
        
        service = AIChatService()
        summary = service.get_usage_summary()
        
        assert summary["total_requests"] == 0
        assert summary["total_cost"] == 0.0
        assert summary["total_tokens"] == 0
        assert summary["average_cost_per_request"] == 0
    
    def test_usage_summary_with_data(self):
        """Test usage summary with data"""
        from app.services.ai_chat_service import AIChatService
        
        service = AIChatService()
        service._log_usage("gpt-4o-mini", 100, 50, 0.001)
        service._log_usage("gpt-4o-mini", 200, 100, 0.002)
        
        summary = service.get_usage_summary()
        assert summary["total_requests"] == 2
        assert summary["total_cost"] == 0.003
        assert summary["total_tokens"] == 450  # (100+50) + (200+100)
        assert summary["average_cost_per_request"] == 0.0015
    
    def test_rules_context_formatting(self):
        """Test rules context formatting"""
        from app.services.ai_chat_service import AIChatService
        
        service = AIChatService()
        
        # Test empty rules
        context = service._format_rules_context([], "test query", "chess")
        assert "No specific rules found in the chess rulebook" in context
        
        # Test with rules
        rules = [
            {
                "title": "Test Rule",
                "content": "Test content",
                "category_id": "test"
            }
        ]
        context = service._format_rules_context(rules, "test query", "chess")
        assert "Game: Chess" in context
        assert "User Query: test query" in context
        assert "Test Rule" in context
    
    def test_system_prompt_creation(self):
        """Test system prompt creation"""
        from app.services.ai_chat_service import AIChatService
        
        service = AIChatService()
        prompt = service._create_system_prompt("chess")
        
        assert "chess" in prompt.lower()
        assert "RESPONSE FORMAT REQUIREMENTS" in prompt
        assert "Direct Answer" in prompt
        assert "Related Rules" in prompt
    
    @pytest.mark.asyncio
    async def test_ai_service_no_api_key_fallback(self):
        """Test AI service fallback when no API key"""
        from app.services.ai_chat_service import AIChatService
        
        service = AIChatService()
        rules = [{"title": "Test", "content": "Test content", "category_id": "test"}]
        
        with patch('app.services.ai_chat_service.settings') as mock_settings:
            mock_settings.openai_api_key = None
            
            result = await service.generate_rule_response("test", "chess", rules)
            
            assert result["ai_powered"] is False
            assert result["fallback_required"] is True
            assert result["error_type"] == "ValueError"
    
    @pytest.mark.asyncio
    async def test_connection_test_no_api_key(self):
        """Test connection test without API key"""
        from app.services.ai_chat_service import AIChatService
        
        service = AIChatService()
        
        with patch('app.services.ai_chat_service.settings') as mock_settings:
            mock_settings.openai_api_key = None
            
            result = await service.test_connection()
            
            assert result["success"] is False
            assert "error" in result
            assert result["error_type"] == "ValueError"
    
    def test_memory_management(self):
        """Test usage log memory management"""
        from app.services.ai_chat_service import AIChatService
        
        service = AIChatService()
        
        # Add more than 100 entries
        for i in range(105):
            service._log_usage("gpt-4o-mini", 10, 5, 0.001)
        
        # Should only keep last 100
        assert len(service.usage_log) == 100
    
    def test_content_truncation(self):
        """Test long content gets truncated"""
        from app.services.ai_chat_service import AIChatService
        
        service = AIChatService()
        
        long_rules = [
            {
                "title": "Long Rule",
                "content": "A" * 600,  # Very long content
                "category_id": "test"
            }
        ]
        
        context = service._format_rules_context(long_rules, "test", "chess")
        
        # Should be truncated to 500 chars + "..."
        assert "A" * 500 + "..." in context
        assert "A" * 600 not in context


class TestBasicAPIHealth:
    """Basic API health tests"""
    
    def test_fastapi_import(self):
        """Test FastAPI and related imports work"""
        try:
            from fastapi import FastAPI
            from fastapi.testclient import TestClient
            import main
            assert True
        except ImportError as e:
            pytest.fail(f"Failed to import required modules: {e}")
    
    def test_models_import(self):
        """Test models can be imported"""
        try:
            from app.models import ChatRequest, StructuredChatResponse
            assert ChatRequest is not None
            assert StructuredChatResponse is not None
        except ImportError as e:
            pytest.fail(f"Failed to import models: {e}")
    
    def test_database_import(self):
        """Test database module can be imported"""
        try:
            from app.database import db, connect_to_mongo
            assert db is not None
            assert connect_to_mongo is not None
        except ImportError as e:
            pytest.fail(f"Failed to import database: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])