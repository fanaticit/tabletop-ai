#!/usr/bin/env python3
# test_openai.py - Clean OpenAI test script

import asyncio
import os
from dotenv import load_dotenv

async def test_openai():
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"API Key configured: {bool(api_key and api_key != 'your-openai-api-key-here')}")
    
    if api_key and len(api_key) > 14:
        print(f"API Key preview: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("API Key too short or not set")
        return False
    
    try:
        # Import OpenAI with minimal configuration
        from openai import AsyncOpenAI
        
        # Create client with only the API key
        client = AsyncOpenAI(api_key=api_key)
        
        print("✅ OpenAI client created successfully")
        
        # Test with a simple embedding
        print("🔄 Testing embedding generation...")
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input="Hello, this is a test."
        )
        
        print("✅ OpenAI connection successful!")
        print(f"Embedding generated: {len(response.data[0].embedding)} dimensions")
        
        # Clean up
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    asyncio.run(test_openai())