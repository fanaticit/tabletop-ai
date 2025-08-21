# app/routes/chat.py - Fixed chat routes with regex search
from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse
from app.database import get_database
import re

router = APIRouter()

@router.post("/query", response_model=ChatResponse)
async def query_rules(request: ChatRequest):
    """Query game rules using regex search (no index required)"""
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        collection = db["content_chunks"]
        
        # Use regex search instead of text search (no index required)
        search_pattern = re.escape(request.query.lower())
        
        search_results = []
        async for rule in collection.find({
            "game_id": request.game_system,
            "$or": [
                {"content": {"$regex": search_pattern, "$options": "i"}},
                {"title": {"$regex": search_pattern, "$options": "i"}}
            ]
        }).limit(5):
            if "_id" in rule:
                del rule["_id"]
            if "rule_embedding" in rule:
                del rule["rule_embedding"]  # Remove large embedding data
            search_results.append(rule)
        
        # Generate response
        if search_results:
            response_text = f"I found {len(search_results)} relevant rules for '{request.query}' in {request.game_system}:\n\n"
            
            for i, rule in enumerate(search_results, 1):
                response_text += f"**{i}. {rule['title']}**\n"
                
                # Show relevant content snippet
                content = rule['content']
                query_lower = request.query.lower()
                
                # Find the query in the content for context
                content_lower = content.lower()
                if query_lower in content_lower:
                    start_idx = content_lower.find(query_lower)
                    start = max(0, start_idx - 50)
                    end = min(len(content), start_idx + len(request.query) + 100)
                    snippet = content[start:end].strip()
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(content):
                        snippet = snippet + "..."
                    response_text += f"{snippet}\n\n"
                else:
                    # If query not found, show first part of content
                    response_text += f"{content[:150]}...\n\n"
                    
        else:
            response_text = f"I couldn't find any rules about '{request.query}' in {request.game_system}. Try different keywords or check if the game has been uploaded."
        
        return ChatResponse(
            response=response_text,
            sources=search_results,
            confidence_score=0.8 if search_results else 0.1
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@router.get("/games/{game_id}/rules")
async def get_game_rules(game_id: str, limit: int = 10):
    """Get all rules for a specific game"""
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        collection = db["content_chunks"]
        
        rules = []
        async for rule in collection.find({"game_id": game_id}).limit(limit):
            if "_id" in rule:
                del rule["_id"]
            if "rule_embedding" in rule:
                del rule["rule_embedding"]  # Remove large embedding data
            rules.append(rule)
        
        return {
            "game_id": game_id,
            "rules": rules,
            "total_found": len(rules),
            "message": f"Found {len(rules)} rules for {game_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving rules: {str(e)}")

@router.get("/search/{game_id}")
async def search_rules_by_keyword(game_id: str, q: str, limit: int = 5):
    """Search rules by keyword (simple endpoint for testing)"""
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        collection = db["content_chunks"]
        
        # Simple regex search
        search_pattern = re.escape(q.lower())
        
        rules = []
        async for rule in collection.find({
            "game_id": game_id,
            "$or": [
                {"content": {"$regex": search_pattern, "$options": "i"}},
                {"title": {"$regex": search_pattern, "$options": "i"}}
            ]
        }).limit(limit):
            if "_id" in rule:
                del rule["_id"]
            if "rule_embedding" in rule:
                del rule["rule_embedding"]
            rules.append({
                "title": rule["title"],
                "content_preview": rule["content"][:200] + "..." if len(rule["content"]) > 200 else rule["content"],
                "category_id": rule.get("category_id", "unknown")
            })
        
        return {
            "query": q,
            "game_id": game_id,
            "results": rules,
            "total_found": len(rules)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching rules: {str(e)}")