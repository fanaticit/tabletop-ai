#!/usr/bin/env python3
"""
Test script to compare OpenAI and Anthropic responses
Usage: python test_dual_ai.py
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_QUERIES = [
    {
        "query": "How do pawns move in chess?",
        "game_system": "chess"
    },
    {
        "query": "What is checkmate?",
        "game_system": "chess"
    },
    {
        "query": "How does castling work?", 
        "game_system": "chess"
    }
]

async def get_auth_token():
    """Get authentication token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{API_BASE_URL}/token",
            data={"username": "admin", "password": "secret"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Auth failed: {response.status_code} - {response.text}")
            return None

async def test_single_provider(query_data, provider=None):
    """Test a single AI provider"""
    async with httpx.AsyncClient() as client:
        # Test using the enhanced endpoint
        test_data = {
            **query_data,
            "ai_provider": provider,
            "compare_providers": False
        }
        
        response = await client.post(
            f"{API_BASE_URL}/api/chat/query/enhanced",
            json=test_data,
            timeout=30.0
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                "success": True,
                "provider": provider or "default",
                "search_method": result.get("search_method", "unknown"),
                "response_preview": result.get("structured_response", {}).get("content", {}).get("summary", {}).get("text", "No response")[:150]
            }
        else:
            return {
                "success": False,
                "provider": provider or "default", 
                "error": f"HTTP {response.status_code}: {response.text}"
            }

async def test_provider_comparison(query_data):
    """Test both providers simultaneously"""
    async with httpx.AsyncClient() as client:
        test_data = {
            **query_data,
            "compare_providers": True
        }
        
        response = await client.post(
            f"{API_BASE_URL}/api/chat/query/enhanced",
            json=test_data,
            timeout=45.0
        )
        
        if response.status_code == 200:
            result = response.json()
            comparison = result.get("results", {})
            
            summary = {}
            for provider, provider_result in comparison.items():
                if provider_result.get("success"):
                    usage = provider_result.get("usage", {})
                    summary[provider] = {
                        "success": True,
                        "model": provider_result.get("model", "unknown"),
                        "response_time": provider_result.get("response_time", 0),
                        "cost": usage.get("estimated_cost", 0),
                        "tokens": usage.get("total_tokens", 0),
                        "response_preview": provider_result.get("response", "")[:100] + "..."
                    }
                else:
                    summary[provider] = {
                        "success": False,
                        "error": provider_result.get("error", "Unknown error")
                    }
            
            return {"success": True, "comparison": summary}
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}

async def test_ai_connections():
    """Test AI service connections"""
    async with httpx.AsyncClient() as client:
        # Test multi-AI service
        response = await client.get(f"{API_BASE_URL}/api/chat/ai-test/multi")
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"Connection test failed: {response.status_code}"}

async def main():
    """Main test function"""
    print("🤖 Dual AI Provider Testing")
    print("="*50)
    
    # Test connections first
    print("\n1. Testing AI Provider Connections...")
    connection_test = await test_ai_connections()
    print(json.dumps(connection_test, indent=2))
    
    if not connection_test.get("results"):
        print("❌ No AI providers available. Check your API keys in .env file.")
        return
    
    print("\n2. Testing Individual Providers...")
    
    for i, query_data in enumerate(TEST_QUERIES, 1):
        print(f"\n📝 Query {i}: {query_data['query']}")
        print("-" * 40)
        
        # Test each provider individually
        for provider in ["openai", "anthropic"]:
            if provider in connection_test.get("results", {}):
                if connection_test["results"][provider].get("status") == "connected":
                    print(f"\n🧠 Testing {provider.upper()}:")
                    result = await test_single_provider(query_data, provider)
                    
                    if result["success"]:
                        print(f"   ✅ Success ({result['search_method']})")
                        print(f"   📄 Response: {result['response_preview']}")
                    else:
                        print(f"   ❌ Failed: {result['error']}")
                else:
                    print(f"\n⚠️  {provider.upper()}: {connection_test['results'][provider].get('error', 'Not configured')}")
    
    print("\n3. Testing Side-by-Side Comparison...")
    
    # Test one query with side-by-side comparison
    test_query = TEST_QUERIES[0]
    print(f"\n🔍 Comparing providers for: {test_query['query']}")
    print("-" * 50)
    
    comparison_result = await test_provider_comparison(test_query)
    
    if comparison_result["success"]:
        for provider, result in comparison_result["comparison"].items():
            print(f"\n{provider.upper()}:")
            if result["success"]:
                print(f"   Model: {result['model']}")
                print(f"   Time: {result['response_time']:.2f}s")
                print(f"   Cost: ${result['cost']:.6f}")
                print(f"   Tokens: {result['tokens']}")
                print(f"   Preview: {result['response_preview']}")
            else:
                print(f"   ❌ Error: {result['error']}")
    else:
        print(f"❌ Comparison failed: {comparison_result['error']}")
    
    print("\n✅ Testing Complete!")
    print("\nTo use in your application:")
    print("• Use /api/chat/query for default provider")
    print("• Use /api/chat/query/enhanced with ai_provider='openai' or 'anthropic'")
    print("• Use /api/chat/query/enhanced with compare_providers=true for side-by-side")

if __name__ == "__main__":
    asyncio.run(main())