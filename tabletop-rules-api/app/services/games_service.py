# app/services/games_service.py - Dynamic games management
from typing import Dict, List, Any, Optional
from app.database import get_database
from datetime import datetime
import re

class GamesService:
    def __init__(self):
        self.collection_name = "games"

    async def register_game(self, game_data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new game or update existing one"""
        db = get_database()
        collection = db[self.collection_name]
        
        game_id = game_data.get("game_id")
        if not game_id:
            raise ValueError("game_id is required")
        
        # Check if game already exists
        existing_game = await collection.find_one({"game_id": game_id})
        
        if existing_game:
            # Update existing game
            update_data = {
                **game_data,
                "updated_at": datetime.utcnow(),
                "rule_count": existing_game.get("rule_count", 0)
            }
            
            await collection.update_one(
                {"game_id": game_id},
                {"$set": update_data}
            )
            
            return await collection.find_one({"game_id": game_id})
        else:
            # Create new game
            new_game = {
                "game_id": game_id,
                "name": game_data.get("name", game_id.title()),
                "publisher": game_data.get("publisher", "Unknown"),
                "version": game_data.get("version", "1.0"),
                "description": game_data.get("description", ""),
                "complexity": game_data.get("complexity", "medium"),
                "min_players": game_data.get("min_players", 1),
                "max_players": game_data.get("max_players", 2),
                "rule_count": 0,
                "categories": [],
                "ai_tags": game_data.get("ai_tags", []),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "auto_registered": True
            }
            
            result = await collection.insert_one(new_game)
            return await collection.find_one({"_id": result.inserted_id})

    async def get_all_games(self) -> List[Dict[str, Any]]:
        """Get all registered games"""
        db = get_database()
        collection = db[self.collection_name]
        
        games = []
        async for game in collection.find({}, {"_id": 0}):
            games.append(game)
        
        return sorted(games, key=lambda x: x.get("name", ""))

    async def get_game_by_id(self, game_id: str) -> Optional[Dict[str, Any]]:
        """Get specific game by ID"""
        db = get_database()
        collection = db[self.collection_name]
        
        return await collection.find_one({"game_id": game_id}, {"_id": 0})

    async def update_rule_count(self, game_id: str, increment: int = 1):
        """Update rule count for a game"""
        db = get_database()
        collection = db[self.collection_name]
        
        await collection.update_one(
            {"game_id": game_id},
            {
                "$inc": {"rule_count": increment},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

    async def add_category_to_game(self, game_id: str, category: str):
        """Add a category to a game if it doesn't exist"""
        db = get_database()
        collection = db[self.collection_name]
        
        await collection.update_one(
            {"game_id": game_id},
            {
                "$addToSet": {"categories": category},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

    def extract_game_id_from_filename(self, filename: str) -> str:
        """Extract game ID from filename - more flexible approach"""
        # Remove extension and clean up
        base_name = filename.replace('.md', '').replace('.markdown', '').lower()
        
        # Split by underscores or hyphens and take first part as game ID
        parts = re.split(r'[_\-\s]+', base_name)
        
        if parts:
            # Clean the first part to make it a valid game_id
            game_id = re.sub(r'[^a-z0-9]', '', parts[0])
            return game_id if game_id else 'unknown'
        
        return 'unknown'

    def extract_game_info_from_content(self, content: str, filename: str) -> Dict[str, Any]:
        """Extract game information from Markdown content"""
        
        # Default game info
        game_info = {
            "game_id": self.extract_game_id_from_filename(filename),
            "name": None,
            "publisher": None,
            "version": None,
            "description": None,
            "ai_tags": []
        }
        
        # Look for game title in content (# Game: Title)
        game_title_match = re.search(r'^#\s+Game:\s*(.+)$', content, re.MULTILINE)
        if game_title_match:
            game_info["name"] = game_title_match.group(1).strip()
        
        # Extract AI-relevant tags from content
        content_lower = content.lower()
        
        # Detect game types
        if any(term in content_lower for term in ['chess', 'checkmate', 'pawn', 'knight', 'bishop']):
            game_info["ai_tags"].extend(['strategy', 'board-game', 'two-player', 'classic'])
            game_info["min_players"] = 2
            game_info["max_players"] = 2
        
        if any(term in content_lower for term in ['dice', 'roll', 'd20', 'rpg']):
            game_info["ai_tags"].extend(['dice-based', 'rpg'])
        
        if any(term in content_lower for term in ['card', 'deck', 'hand']):
            game_info["ai_tags"].extend(['card-game'])
        
        # Set default name if not found
        if not game_info["name"]:
            game_info["name"] = game_info["game_id"].replace('_', ' ').title()
        
        return game_info

games_service = GamesService()