# app/services/ai_service.py - Clean OpenAI integration
from typing import List
from app.config import settings

class AIService:
    def __init__(self):
        self.client = None
    
    def _ensure_client(self):
        """Initialize OpenAI client"""
        if self.client is None:
            if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here":
                raise ValueError("OpenAI API key not configured")
            
            from openai import AsyncOpenAI
            
            # Create client with only the API key - no other parameters
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embeddings for text using OpenAI"""
        self._ensure_client()
        
        response = await self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    async def test_connection(self) -> bool:
        """Test if OpenAI connection works"""
        try:
            self._ensure_client()
            # Test with a simple embedding
            await self.generate_embedding("test")
            return True
        except Exception as e:
            print(f"OpenAI test failed: {e}")
            return False
    
    async def close(self):
        """Close the client connection"""
        if self.client:
            await self.client.close()

# Create singleton instance
ai_service = AIService()