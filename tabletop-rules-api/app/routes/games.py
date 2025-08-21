# app/routes/games.py - Fixed MongoDB None comparison
from fastapi import APIRouter, HTTPException
from typing import List
from app.models import Game, GameSummary, GamesListResponse
from app.database import get_database

router = APIRouter()

@router.get("/", response_model=GamesListResponse)
async def get_games():
    """Get list of available games"""
    try:
        db = get_database()
        if db is None:
            # Return empty list if no database connection
            return GamesListResponse(
                games=[],
                total_count=0,
                message="Database not connected - no games available"
            )
        
        games_collection = db["games"]
        
        games = []
        async for game in games_collection.find():
            game_summary = GameSummary(
                game_id=game["game_id"],
                name=game.get("name", game["game_id"]),
                rule_count=game.get("rule_count", 0),
                complexity=game.get("complexity", "medium"),
                ai_tags=game.get("ai_tags", [])
            )
            games.append(game_summary)
        
        return GamesListResponse(
            games=games,
            total_count=len(games),
            message=f"Found {len(games)} games" if games else "No games uploaded yet"
        )
        
    except Exception as e:
        # Graceful error handling
        return GamesListResponse(
            games=[],
            total_count=0,
            message=f"Error retrieving games: {str(e)}"
        )

@router.get("/{game_id}")
async def get_game_details(game_id: str):
    """Get detailed information about a specific game"""
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        games_collection = db["games"]
        game = await games_collection.find_one({"game_id": game_id})
        
        if not game:
            raise HTTPException(status_code=404, detail=f"Game '{game_id}' not found")
        
        # Remove MongoDB _id field
        if "_id" in game:
            del game["_id"]
        
        return game
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving game: {str(e)}")

@router.get("/{game_id}/stats")
async def get_game_stats(game_id: str):
    """Get statistics for a specific game"""
    try:
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        # Check if game exists
        games_collection = db["games"]
        game = await games_collection.find_one({"game_id": game_id})
        
        if not game:
            raise HTTPException(status_code=404, detail=f"Game '{game_id}' not found")
        
        # Get rule statistics
        rules_collection = db["content_chunks"]
        total_rules = await rules_collection.count_documents({"game_id": game_id})
        
        # Get categories
        pipeline = [
            {"$match": {"game_id": game_id}},
            {"$group": {"_id": "$category_id", "count": {"$sum": 1}}}
        ]
        
        categories = {}
        async for result in rules_collection.aggregate(pipeline):
            categories[result["_id"]] = result["count"]
        
        return {
            "game_id": game_id,
            "game_name": game.get("name", game_id),
            "total_rules": total_rules,
            "categories": categories,
            "total_categories": len(categories)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving game stats: {str(e)}")