# app/services/upload_service.py - Simple Markdown upload service
import frontmatter
import re
from typing import Dict, List, Any
from datetime import datetime
from app.database import get_database
from app.services.ai_service import ai_service

class UploadService:
    
    async def process_markdown_file(self, content: str, filename: str) -> Dict[str, Any]:
        """Process a markdown file and store rules in database"""
        
        # Parse frontmatter
        post = frontmatter.loads(content)
        
        # Extract game info
        game_id = post.metadata.get('game_id') or self._extract_game_id_from_filename(filename)
        
        # Update game if exists
        await self._update_game_from_metadata(game_id, post.metadata, filename)
        
        # Chunk the content
        chunks = self._chunk_markdown_content(post.content, game_id, filename)
        
        # Generate embeddings and store chunks
        stored_chunks = 0
        errors = []
        
        for chunk in chunks:
            try:
                # Generate embedding
                embedding = await ai_service.generate_embedding(chunk["content"])
                chunk["rule_embedding"] = embedding
                
                # Store in database
                await self._store_chunk(chunk)
                stored_chunks += 1
                
            except Exception as e:
                errors.append(f"Error processing chunk '{chunk['title']}': {str(e)}")
        
        # Update game rule count
        await self._update_game_rule_count(game_id, stored_chunks)
        
        return {
            "game_id": game_id,
            "chunks_processed": stored_chunks,
            "total_chunks": len(chunks),
            "errors": errors,
            "filename": filename
        }
    
    def _extract_game_id_from_filename(self, filename: str) -> str:
        """Extract game ID from filename"""
        base_name = filename.replace('.md', '').replace('.markdown', '').lower()
        parts = re.split(r'[_\-\s]+', base_name)
        return parts[0] if parts else 'unknown'
    
    async def _update_game_from_metadata(self, game_id: str, metadata: Dict[str, Any], filename: str):
        """Update game information from frontmatter metadata"""
        db = get_database()
        if db is None:
            return
        
        games_collection = db["games"]
        
        # Get existing game or create update data
        update_data = {
            "updated_at": datetime.utcnow()
        }
        
        # Add metadata fields if present
        if "name" in metadata:
            update_data["name"] = metadata["name"]
        if "publisher" in metadata:
            update_data["publisher"] = metadata["publisher"]
        if "description" in metadata:
            update_data["description"] = metadata["description"]
        if "complexity" in metadata:
            update_data["complexity"] = metadata["complexity"]
        if "min_players" in metadata:
            update_data["min_players"] = metadata["min_players"]
        if "max_players" in metadata:
            update_data["max_players"] = metadata["max_players"]
        if "ai_tags" in metadata:
            update_data["ai_tags"] = metadata["ai_tags"]
        
        # Update existing game or do nothing if game doesn't exist
        # (Game should already exist from manual registration)
        await games_collection.update_one(
            {"game_id": game_id},
            {"$set": update_data}
        )
    
    def _chunk_markdown_content(self, content: str, game_id: str, filename: str) -> List[Dict[str, Any]]:
        """Chunk markdown content into rule sections"""
        
        # Split by ## headers
        sections = re.split(r'\n## ', content)
        chunks = []
        
        for section_idx, section in enumerate(sections):
            if not section.strip():
                continue
            
            # Add back the ## for non-first sections
            if section_idx > 0:
                section = "## " + section
            
            # Extract rule info
            rule_info = self._extract_rule_info(section)
            
            chunk = {
                "game_id": game_id,
                "category_id": f"{game_id}_{rule_info['category'].lower().replace(' ', '_').replace('→', '_')}",
                "content_type": "rule_text",
                "title": rule_info['title'],
                "content": section,
                "ancestors": [
                    game_id, 
                    f"{game_id}_rules", 
                    f"{game_id}_{rule_info['category'].lower().replace(' ', '_').replace('→', '_')}"
                ],
                "chunk_metadata": {
                    "complexity_score": rule_info['complexity_score'],
                    "mandatory": rule_info['mandatory'],
                    "source_file": filename,
                    "section_index": section_idx
                },
                "created_at": datetime.utcnow()
            }
            chunks.append(chunk)
        
        return chunks
    
    def _extract_rule_info(self, section: str) -> Dict[str, Any]:
        """Extract rule information from markdown section"""
        
        lines = section.split('\n')
        title = "Unknown Rule"
        category = "general"
        complexity_score = 0.5
        mandatory = True
        
        # Extract title from first line
        if lines and lines[0].startswith('## '):
            title = lines[0][3:].strip()
            if title.startswith('Rule: '):
                title = title[6:]
        
        # Look for metadata
        for line in lines:
            if '**Category**:' in line:
                category = line.split('**Category**:')[1].strip()
            elif '**Complexity**:' in line:
                complexity_text = line.split('**Complexity**:')[1].strip().lower()
                if 'beginner' in complexity_text or 'easy' in complexity_text:
                    complexity_score = 0.3
                elif 'intermediate' in complexity_text:
                    complexity_score = 0.6
                elif 'advanced' in complexity_text:
                    complexity_score = 0.9
            elif '**Mandatory**:' in line:
                mandatory_text = line.split('**Mandatory**:')[1].strip().lower()
                mandatory = mandatory_text in ['yes', 'true', 'required']
        
        return {
            "title": title,
            "category": category,
            "complexity_score": complexity_score,
            "mandatory": mandatory
        }
    
    async def _store_chunk(self, chunk: Dict[str, Any]):
        """Store a chunk in the database"""
        db = get_database()
        if db is None:
            raise Exception("Database not connected")
        
        collection = db["content_chunks"]
        await collection.insert_one(chunk)
    
    async def _update_game_rule_count(self, game_id: str, new_rules: int):
        """Update the rule count for a game"""
        db = get_database()
        if db is None:
            return
        
        games_collection = db["games"]
        await games_collection.update_one(
            {"game_id": game_id},
            {
                "$inc": {"rule_count": new_rules},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )

upload_service = UploadService()