# scripts/test_api.py
import asyncio
import aiohttp
import json
import time

API_BASE_URL = "http://localhost:8000"

async def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/health") as response:
            if response.status == 200:
                data = await response.json()
                print(f"✅ Health check passed: {data}")
                return True
            else:
                print(f"❌ Health check failed: {response.status}")
                return False

async def test_games_endpoint():
    """Test the games endpoint"""
    print("\n🎲 Testing games endpoint...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_BASE_URL}/api/games/") as response:
            if response.status == 200:
                games = await response.json()
                print(f"✅ Found {len(games)} games")
                for game in games:
                    print(f"   - {game['name']} ({game['publisher']})")
                return True
            else:
                print(f"❌ Games endpoint failed: {response.status}")
                return False

async def test_chat_query():
    """Test the chat query endpoint"""
    print("\n💬 Testing chat query endpoint...")
    
    test_queries = [
        {"query": "How does resource production work?", "game_system": "Catan"},
        {"query": "What is castling?", "game_system": "Chess"},
        {"query": "How does combat work?", "game_system": "Warhammer Age of Sigmar"}
    ]
    
    async with aiohttp.ClientSession() as session:
        for test_query in test_queries:
            print(f"\n🤔 Asking: '{test_query['query']}' about {test_query['game_system']}")
            
            try:
                async with session.post(
                    f"{API_BASE_URL}/api/chat/query",
                    headers={"Content-Type": "application/json"},
                    json=test_query
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Response received ({len(data['response'])} chars)")
                        print(f"   Sources found: {len(data['sources'])}")
                        if data['sources']:
                            print(f"   First source: {data['sources'][0].get('category', 'N/A')}")
                        # Print first 150 chars of response
                        preview = data['response'][:150] + "..." if len(data['response']) > 150 else data['response']
                        print(f"   Preview: {preview}")
                    else:
                        print(f"❌ Query failed: {response.status}")
                        error_text = await response.text()
                        print(f"   Error: {error_text}")
                        
            except Exception as e:
                print(f"❌ Query exception: {e}")

async def test_streaming_chat():
    """Test the streaming chat endpoint"""
    print("\n🌊 Testing streaming chat endpoint...")
    
    test_query = {
        "query": "Explain the robber rules in Catan",
        "game_system": "Catan"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{API_BASE_URL}/api/chat/stream",
                headers={"Content-Type": "application/json"},
                json=test_query
            ) as response:
                if response.status == 200:
                    print("✅ Streaming response:")
                    content_chunks = []
                    
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        if line_str.startswith('data: '):
                            try:
                                data = json.loads(line_str[6:])  # Remove 'data: ' prefix
                                
                                if data['type'] == 'context':
                                    print(f"   📚 Context: {data['data']}")
                                elif data['type'] == 'content':
                                    chunk = data['data']['chunk']
                                    content_chunks.append(chunk)
                                    print(chunk, end='', flush=True)
                                elif data['type'] == 'complete':
                                    print(f"\n   ✅ Streaming complete!")
                                    break
                                elif data['type'] == 'error':
                                    print(f"\n   ❌ Streaming error: {data['data']['message']}")
                                    break
                                    
                            except json.JSONDecodeError:
                                continue  # Skip malformed JSON
                                
                    full_response = ''.join(content_chunks)
                    print(f"\n   Total response length: {len(full_response)} characters")
                    
                else:
                    print(f"❌ Streaming failed: {response.status}")
                    
        except Exception as e:
            print(f"❌ Streaming exception: {e}")

async def test_add_game_and_rule():
    """Test adding a new game and rule"""
    print("\n➕ Testing game and rule creation...")
    
    new_game = {
        "name": "Test Game",
        "publisher": "Test Publisher", 
        "complexity": 5.0,
        "min_players": 2,
        "max_players": 4,
        "description": "A test game for API testing"
    }
    
    async with aiohttp.ClientSession() as session:
        # Add game
        try:
            async with session.post(
                f"{API_BASE_URL}/api/games/",
                headers={"Content-Type": "application/json"},
                json=new_game
            ) as response:
                if response.status == 200:
                    game_data = await response.json()
                    print(f"✅ Game created with ID: {game_data['id']}")
                    
                    # Add a rule to the game
                    new_rule = {
                        "rule_text": "This is a test rule for the test game. Players must follow this rule during gameplay.",
                        "rule_category": "basic_rules",
                        "complexity_score": 3.0,
                        "page_reference": "pg. 1",
                        "related_rules": ["setup", "gameplay"]
                    }
                    
                    async with session.post(
                        f"{API_BASE_URL}/api/games/Test Game/rules",
                        headers={"Content-Type": "application/json"},
                        json=new_rule
                    ) as rule_response:
                        if rule_response.status == 200:
                            rule_data = await rule_response.json()
                            print(f"✅ Rule created with ID: {rule_data['id']}")
                        else:
                            print(f"❌ Rule creation failed: {rule_response.status}")
                            
                else:
                    print(f"❌ Game creation failed: {response.status}")
                    
        except Exception as e:
            print(f"❌ Game/Rule creation exception: {e}")

async def run_all_tests():
    """Run all API tests"""
    print("🚀 Starting API tests...")
    print("=" * 50)
    
    start_time = time.time()
    
    # Basic connectivity test
    health_ok = await test_health()
    if not health_ok:
        print("❌ Health check failed - stopping tests")
        return
    
    # Test all endpoints
    await test_games_endpoint()
    await test_chat_query()
    await test_streaming_chat()
    await test_add_game_and_rule()
    
    end_time = time.time()
    print("\n" + "=" * 50)
    print(f"🏁 All tests completed in {end_time - start_time:.2f} seconds")
    print("\n💡 If all tests passed, your API is working correctly!")
    print("💡 You can now build a frontend or integrate with other services.")

if __name__ == "__main__":
    # Run the tests
    asyncio.run(run_all_tests())