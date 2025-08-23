# app/routes/chat.py - Fixed version

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_database
from pydantic import BaseModel
from typing import List, Optional
import re

router = APIRouter(prefix="/api/chat", tags=["chat"])

class ChatQuery(BaseModel):
    query: str
    game_system: str
    conversation_id: Optional[str] = None

@router.post("/query")
async def query_rules(
    chat_query: ChatQuery,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Query game rules using natural language."""
    try:
        # Basic text search for now (no AI until OpenAI issues are resolved)
        query_text = chat_query.query.lower()
        game_id = chat_query.game_system.lower()
        
        # Create search regex pattern
        search_terms = query_text.split()
        search_pattern = "|".join([re.escape(term) for term in search_terms])
        
        # Search for relevant rules
        rules = await db.content_chunks.find({
            "game_id": game_id,
            "$or": [
                {"title": {"$regex": search_pattern, "$options": "i"}},
                {"content": {"$regex": search_pattern, "$options": "i"}}
            ]
        }).limit(5).to_list(length=5)
        
        if not rules:
            return {
                "query": chat_query.query,
                "results": [],
                "game_system": game_id,
                "search_method": "text_regex"
            }
        
        # Format response
        response_parts = [f"Here's what I found about '{chat_query.query}' in {game_id}:"]
        
        for i, rule in enumerate(rules, 1):
            content_preview = rule["content"][:200] + "..." if len(rule["content"]) > 200 else rule["content"]
            response_parts.append(f"\n{i}. **{rule['title']}**\n{content_preview}")
        
        return {
            "query": chat_query.query,
            "results": [
                {
                    "game_id": game_id,
                    "category_id": rule.get("category_id", "general"),
                    "title": rule["title"],
                    "content": rule["content"],
                    "chunk_metadata": rule.get("chunk_metadata", {})
                }
                for rule in rules
            ],
            "search_method": "text_regex"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/search/{game_id}")
async def keyword_search(
    game_id: str,
    q: str = Query(..., description="Search query"),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Simple keyword search for rules."""
    try:
        # Create search pattern
        search_pattern = re.escape(q.lower())
        
        # Search for rules
        rules = await db.content_chunks.find({
            "game_id": game_id,
            "$or": [
                {"title": {"$regex": search_pattern, "$options": "i"}},
                {"content": {"$regex": search_pattern, "$options": "i"}}
            ]
        }).limit(10).to_list(length=10)
        
        return {
            "game_id": game_id,
            "query": q,
            "results": [
                {
                    "title": rule["title"],
                    "content_preview": rule["content"][:150] + ("..." if len(rule["content"]) > 150 else ""),
                    "category": rule.get("category_id", "general")
                }
                for rule in rules
            ],
            "total_found": len(rules)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/games/{game_id}/rules")
async def get_all_game_rules(
    game_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    limit: int = Query(50, le=100),
    skip: int = Query(0, ge=0)
):
    """Get all rules for a specific game."""
    try:
        # Get rules with pagination
        rules = await db.content_chunks.find({
            "game_id": game_id
        }).skip(skip).limit(limit).to_list(length=limit)
        
        # Get total count
        total_count = await db.content_chunks.count_documents({"game_id": game_id})
        
        return {
            "game_id": game_id,
            "rules": [
                {
                    "title": rule["title"],
                    "content": rule["content"],
                    "category": rule.get("category_id", "general"),
                    "created_at": rule.get("created_at")
                }
                for rule in rules
            ],
            "pagination": {
                "skip": skip,
                "limit": limit,
                "total": total_count,
                "has_more": skip + limit < total_count
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rules: {str(e)}")

@router.get("/games/{game_id}/categories")
async def get_game_categories(
    game_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get all categories for a specific game."""
    try:
        categories = await db.content_chunks.distinct("category_id", {"game_id": game_id})
        
        # Get rule count per category
        category_stats = []
        for category in categories:
            count = await db.content_chunks.count_documents({
                "game_id": game_id,
                "category_id": category
            })
            category_stats.append({
                "category_id": category,
                "rule_count": count
            })
        
        return {
            "game_id": game_id,
            "categories": category_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")