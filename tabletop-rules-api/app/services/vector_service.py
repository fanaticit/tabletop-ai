from typing import List, Dict, Any
from app.database import get_database
from app.services.ai_service import ai_service
import numpy as np

class VectorService:
    def __init__(self):
        self.collection_name = "game_rules"

    async def search_similar_rules(
        self, 
        query: str, 
        game_system: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar rules using vector similarity"""
        db = get_database()
        collection = db[self.collection_name]
        
        try:
            # Generate embedding for the query
            query_embedding = await ai_service.generate_embedding(query)
            
            # Perform vector search (basic implementation)
            # Note: This requires MongoDB Atlas Vector Search to be properly configured
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",
                        "path": "rule_embedding",
                        "queryVector": query_embedding,
                        "numCandidates": limit * 3,
                        "limit": limit,
                        "filter": {"game_id": game_system}
                    }
                },
                {
                    "$project": {
                        "rule_text": 1,
                        "rule_category": 1,
                        "page_reference": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                }
            ]
            
            results = []
            async for doc in collection.aggregate(pipeline):
                results.append(doc)
            
            return results
            
        except Exception as e:
            print(f"Vector search error: {e}")
            # Fallback to text search if vector search fails
            return await self._fallback_text_search(query, game_system, limit)

    async def _fallback_text_search(
        self, 
        query: str, 
        game_system: str, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Fallback text search when vector search is unavailable"""
        db = get_database()
        collection = db[self.collection_name]
        
        try:
            results = []
            async for doc in collection.find({
                "game_id": game_system,
                "$text": {"$search": query}
            }).limit(limit):
                results.append(doc)
            
            return results
        except Exception as e:
            print(f"Fallback search error: {e}")
            return []

    async def add_rule_with_embedding(self, rule_data: Dict[str, Any]) -> str:
        """Add a new rule with vector embedding"""
        db = get_database()
        collection = db[self.collection_name]
        
        try:
            # Generate embedding for the rule text
            embedding = await ai_service.generate_embedding(rule_data["rule_text"])
            rule_data["rule_embedding"] = embedding
            
            result = await collection.insert_one(rule_data)
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"Error adding rule: {e}")
            raise

vector_service = VectorService()