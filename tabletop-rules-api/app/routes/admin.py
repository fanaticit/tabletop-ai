# app/routes/admin.py - Fixed version compatible with auth service

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_database
from app.services.auth_service import verify_admin_token, get_admin_user
# from app.services.upload_service import process_markdown_file  # Not needed
import logging

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/test")
async def test_admin_auth(admin_user: dict = Depends(get_admin_user)):
    """Test admin authentication."""
    return {
        "message": "Admin authentication successful",
        "user": admin_user,
        "timestamp": "2024-01-01T00:00:00Z"
    }

@router.post("/upload/markdown-simple")
async def upload_markdown_simple(
    file: UploadFile = File(...),
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin_user: dict = Depends(get_admin_user)
):
    """Upload markdown file without AI processing (simple version)."""
    try:
        if not file.filename.endswith('.md'):
            raise HTTPException(status_code=400, detail="Only .md files are allowed")
        
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Try to use the upload service if available
        try:
            from app.services.upload_service import parse_markdown_simple
            result = await parse_markdown_simple(content_str, file.filename, db)
            return result
        except ImportError:
            # Fallback to basic processing
            return await basic_markdown_processing(content_str, file.filename, db)
            
    except Exception as e:
        logging.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def basic_markdown_processing(content: str, filename: str, db: AsyncIOMotorDatabase):
    """Basic markdown processing fallback."""
    import frontmatter
    from datetime import datetime
    
    # Parse frontmatter
    try:
        post = frontmatter.loads(content)
        metadata = post.metadata
        main_content = post.content
    except:
        metadata = {}
        main_content = content
    
    # Extract game info
    game_id = metadata.get('game_id', filename.replace('.md', '').lower())
    
    # Split content into sections
    sections = main_content.split('\n## ')
    chunks = []
    
    for i, section in enumerate(sections):
        if section.strip():
            if i == 0:
                title = "Introduction"
                content_text = section
            else:
                lines = section.split('\n', 1)
                title = lines[0].strip()
                content_text = lines[1] if len(lines) > 1 else ""
            
            chunk = {
                "game_id": game_id,
                "category_id": f"{game_id}_general",
                "content_type": "rule_text",
                "title": title,
                "content": f"## {title}\n{content_text}" if i > 0 else content_text,
                "ancestors": [game_id, f"{game_id}_rules"],
                "chunk_metadata": {
                    "source_file": filename,
                    "section_index": i,
                    "uploaded_without_ai": True
                },
                "created_at": datetime.utcnow()
            }
            chunks.append(chunk)
    
    # Insert chunks
    if chunks:
        await db.content_chunks.insert_many(chunks)
    
    # Register/update game
    game_doc = {
        "game_id": game_id,
        "name": metadata.get('name', game_id.title()),
        "publisher": metadata.get('publisher', 'Unknown'),
        "version": metadata.get('version', '1.0'),
        "description": metadata.get('description', ''),
        "complexity": metadata.get('complexity', 'medium'),
        "min_players": metadata.get('min_players', 1),
        "max_players": metadata.get('max_players', 4),
        "rule_count": len(chunks),
        "categories": list(set([chunk["category_id"] for chunk in chunks])),
        "ai_tags": metadata.get('ai_tags', []),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "auto_registered": True
    }
    
    await db.games.replace_one(
        {"game_id": game_id},
        game_doc,
        upsert=True
    )
    
    return {
        "success": True,
        "game_id": game_id,
        "rules_stored": len(chunks),
        "filename": filename
    }

@router.get("/games/registered")
async def list_registered_games(
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin_user: dict = Depends(get_admin_user)
):
    """List all registered games (admin view)."""
    try:
        games = await db.games.find({}).to_list(length=100)
        return {
            "games": [
                {
                    "game_id": game["game_id"],
                    "name": game["name"],
                    "rule_count": game.get("rule_count", 0),
                    "auto_registered": game.get("auto_registered", False),
                    "created_at": game.get("created_at")
                }
                for game in games
            ],
            "total": len(games)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch games: {str(e)}")

@router.delete("/games/{game_id}")
async def delete_game(
    game_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin_user: dict = Depends(get_admin_user)
):
    """Delete a game and all its rules."""
    try:
        # Delete rules
        rules_result = await db.content_chunks.delete_many({"game_id": game_id})
        
        # Delete game
        game_result = await db.games.delete_one({"game_id": game_id})
        
        if game_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Game not found")
        
        return {
            "success": True,
            "game_id": game_id,
            "rules_deleted": rules_result.deleted_count,
            "message": f"Deleted game '{game_id}' and {rules_result.deleted_count} rules"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete game: {str(e)}")

@router.post("/debug/parse-markdown")
async def debug_parse_markdown(
    file: UploadFile = File(...),
    admin_user: dict = Depends(get_admin_user)
):
    """Debug endpoint to parse markdown without storing."""
    try:
        content = await file.read()
        content_str = content.decode('utf-8')
        
        import frontmatter
        
        # Parse frontmatter
        post = frontmatter.loads(content_str)
        
        # Split content
        sections = post.content.split('\n## ')
        
        return {
            "filename": file.filename,
            "metadata": post.metadata,
            "sections_found": len(sections),
            "sections": [
                {
                    "index": i,
                    "title": section.split('\n')[0] if section.strip() else "Empty",
                    "length": len(section)
                }
                for i, section in enumerate(sections)
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parse failed: {str(e)}")