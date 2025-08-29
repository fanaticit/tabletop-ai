# app/routes/admin.py - Enhanced with CLI support endpoints

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_database
from app.services.auth_service import verify_admin_token, get_admin_user
from typing import List, Dict, Any, Optional
from datetime import datetime
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

@router.get("/games/")
async def list_games_detailed(
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin_user: dict = Depends(get_admin_user)
):
    """List all games with detailed metadata (CLI endpoint)."""
    try:
        games = await db.games.find({}).to_list(length=200)
        return {
            "games": [
                {
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
                    "auto_registered": game.get("auto_registered", False),
                    "created_at": game.get("created_at"),
                    "updated_at": game.get("updated_at")
                }
                for game in games
            ],
            "total": len(games),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch games: {str(e)}")

@router.get("/games/{game_id}/rules")
async def get_game_rules(
    game_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin_user: dict = Depends(get_admin_user)
):
    """Get rules for a specific game (CLI endpoint)."""
    try:
        # Check if game exists
        game = await db.games.find_one({"game_id": game_id})
        if not game:
            raise HTTPException(status_code=404, detail=f"Game not found: {game_id}")
        
        # Get rules with pagination
        rules_cursor = db.content_chunks.find({"game_id": game_id}).skip(offset).limit(limit)
        rules = await rules_cursor.to_list(length=limit)
        
        # Get total count
        total_count = await db.content_chunks.count_documents({"game_id": game_id})
        
        return {
            "game_id": game_id,
            "game_name": game["name"],
            "rules": [
                {
                    "rule_id": str(rule["_id"]),
                    "title": rule.get("title", "Untitled"),
                    "content": rule.get("content", ""),
                    "category_id": rule.get("category_id"),
                    "content_type": rule.get("content_type", "rule_text"),
                    "chunk_metadata": rule.get("chunk_metadata", {}),
                    "created_at": rule.get("created_at")
                }
                for rule in rules
            ],
            "total": total_count,
            "offset": offset,
            "limit": limit,
            "has_more": offset + len(rules) < total_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch rules: {str(e)}")

@router.put("/rules/{rule_id}")
async def update_rule(
    rule_id: str,
    rule_data: Dict[str, Any],
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin_user: dict = Depends(get_admin_user)
):
    """Update an individual rule (CLI endpoint)."""
    try:
        from bson import ObjectId
        
        # Validate rule_id format
        try:
            obj_id = ObjectId(rule_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid rule ID format")
        
        # Prepare update data
        update_data = {}
        allowed_fields = ["title", "content", "category_id", "content_type"]
        
        for field in allowed_fields:
            if field in rule_data:
                update_data[field] = rule_data[field]
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No valid fields to update")
        
        # Add update timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        # Update the rule
        result = await db.content_chunks.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        # Get updated rule
        updated_rule = await db.content_chunks.find_one({"_id": obj_id})
        
        return {
            "success": True,
            "rule_id": rule_id,
            "modified_fields": list(update_data.keys()),
            "updated_rule": {
                "rule_id": str(updated_rule["_id"]),
                "title": updated_rule.get("title"),
                "content": updated_rule.get("content"),
                "updated_at": updated_rule.get("updated_at")
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update rule: {str(e)}")

@router.delete("/rules/{rule_id}")
async def delete_rule(
    rule_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin_user: dict = Depends(get_admin_user)
):
    """Delete an individual rule (CLI endpoint)."""
    try:
        from bson import ObjectId
        
        # Validate rule_id format
        try:
            obj_id = ObjectId(rule_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid rule ID format")
        
        # Get rule info before deletion
        rule = await db.content_chunks.find_one({"_id": obj_id})
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        # Delete the rule
        result = await db.content_chunks.delete_one({"_id": obj_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Rule not found")
        
        # Update game rule count
        game_id = rule.get("game_id")
        if game_id:
            remaining_count = await db.content_chunks.count_documents({"game_id": game_id})
            await db.games.update_one(
                {"game_id": game_id},
                {"$set": {"rule_count": remaining_count, "updated_at": datetime.utcnow()}}
            )
        
        return {
            "success": True,
            "rule_id": rule_id,
            "deleted_rule": {
                "title": rule.get("title"),
                "game_id": game_id
            },
            "message": f"Rule '{rule.get('title', rule_id)}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete rule: {str(e)}")

@router.post("/games/{game_id}/validate")
async def validate_game_integrity(
    game_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin_user: dict = Depends(get_admin_user)
):
    """Validate game rules integrity (CLI endpoint)."""
    try:
        issues = []
        
        # Check if game exists
        game = await db.games.find_one({"game_id": game_id})
        if not game:
            raise HTTPException(status_code=404, detail=f"Game not found: {game_id}")
        
        # Check rule count consistency
        actual_rule_count = await db.content_chunks.count_documents({"game_id": game_id})
        stored_rule_count = game.get("rule_count", 0)
        
        if actual_rule_count != stored_rule_count:
            issues.append(f"Rule count mismatch: stored={stored_rule_count}, actual={actual_rule_count}")
        
        # Check for rules without titles
        rules_without_titles = await db.content_chunks.count_documents({
            "game_id": game_id,
            "$or": [{"title": {"$exists": False}}, {"title": ""}]
        })
        
        if rules_without_titles > 0:
            issues.append(f"{rules_without_titles} rules without titles")
        
        # Check for empty content
        rules_without_content = await db.content_chunks.count_documents({
            "game_id": game_id,
            "$or": [{"content": {"$exists": False}}, {"content": ""}]
        })
        
        if rules_without_content > 0:
            issues.append(f"{rules_without_content} rules without content")
        
        # Check for orphaned rules (rules without corresponding game)
        orphaned_rules = await db.content_chunks.count_documents({
            "game_id": {"$nin": [g["game_id"] for g in await db.games.find({}, {"game_id": 1}).to_list(length=None)]}
        })
        
        if orphaned_rules > 0:
            issues.append(f"{orphaned_rules} orphaned rules found")
        
        # Auto-fix rule count if needed
        if actual_rule_count != stored_rule_count:
            await db.games.update_one(
                {"game_id": game_id},
                {"$set": {"rule_count": actual_rule_count, "updated_at": datetime.utcnow()}}
            )
            issues.append("✓ Rule count automatically corrected")
        
        return {
            "game_id": game_id,
            "valid": len([i for i in issues if not i.startswith("✓")]) == 0,
            "issues": issues,
            "rule_count": actual_rule_count,
            "validated_at": datetime.utcnow().isoformat(),
            "auto_fixes_applied": len([i for i in issues if i.startswith("✓")])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.post("/batch/upload")
async def batch_upload_files(
    files: List[UploadFile] = File(...),
    db: AsyncIOMotorDatabase = Depends(get_database),
    admin_user: dict = Depends(get_admin_user)
):
    """Batch upload multiple markdown files (CLI endpoint)."""
    try:
        if len(files) > 50:
            raise HTTPException(status_code=400, detail="Maximum 50 files allowed per batch")
        
        results = []
        
        for file in files:
            try:
                if not file.filename.endswith('.md'):
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": "Only .md files are allowed"
                    })
                    continue
                
                # Read and process file
                content = await file.read()
                content_str = content.decode('utf-8')
                
                # Process using existing logic
                result = await basic_markdown_processing(content_str, file.filename, db)
                result["filename"] = file.filename
                results.append(result)
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
        
        successful = [r for r in results if r.get("success", False)]
        failed = [r for r in results if not r.get("success", False)]
        
        return {
            "total_files": len(files),
            "successful": len(successful),
            "failed": len(failed),
            "results": results,
            "summary": {
                "games_processed": len(set(r.get("game_id") for r in successful if r.get("game_id"))),
                "total_rules_stored": sum(r.get("rules_stored", 0) for r in successful),
                "processing_time": datetime.utcnow().isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")

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