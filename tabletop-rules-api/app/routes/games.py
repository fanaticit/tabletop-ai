# app/routes/games.py - Fixed version

from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_database
from typing import List, Optional

router = APIRouter(prefix="/api/games", tags=["games"])

@router.get("/")
async def list_games(db: AsyncIOMotorDatabase = Depends(get_database)):
    """List all available games."""
    try:
        games = await db.games.find({}).to_list(length=100)
        
        return {
            "games": [
                {
                    "game_id": game["game_id"],
                    "name": game["name"],
                    "publisher": game.get("publisher", "Unknown"),
                    "description": game.get("description", ""),
                    "complexity": game.get("complexity", "medium"),
                    "rule_count": game.get("rule_count", 0),
                    "min_players": game.get("min_players", 1),
                    "max_players": game.get("max_players", 4)
                }
                for game in games
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch games: {str(e)}")

@router.get("/{game_id}")
async def get_game_details(
    game_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get detailed information about a specific game."""
    try:
        game = await db.games.find_one({"game_id": game_id})
        
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        
        return {
            "game_id": game["game_id"],
            "name": game["name"],
            "publisher": game.get("publisher", "Unknown"),
            "version": game.get("version", "1.0"),
            "description": game.get("description", ""),
            "complexity": game.get("complexity", "medium"),
            "min_players": game.get("min_players", 1),
            "max_players": game.get("max_players", 4),
            "rule_count": game.get("rule_count", 0),
            "categories": game.get("categories", []),
            "ai_tags": game.get("ai_tags", []),
            "created_at": game.get("created_at"),
            "updated_at": game.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch game details: {str(e)}")

@router.get("/{game_id}/stats")
async def get_game_stats(
    game_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Get statistics for a specific game."""
    try:
        # Get game info
        game = await db.games.find_one({"game_id": game_id})
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        
        # Get rule count
        rule_count = await db.content_chunks.count_documents({"game_id": game_id})
        
        # Get categories
        categories = await db.content_chunks.distinct("category_id", {"game_id": game_id})
        
        # Get content types
        content_types = await db.content_chunks.distinct("content_type", {"game_id": game_id})
        
        return {
            "game_id": game_id,
            "name": game["name"],
            "rule_count": rule_count,
            "categories": categories,
            "content_types": content_types,
            "complexity": game.get("complexity", "medium"),
            "last_updated": game.get("updated_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch game stats: {str(e)}")