# app/routes/admin.py - Minimal working version with upload
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import verify_admin_token
from app.database import get_database
from datetime import datetime

router = APIRouter()
security = HTTPBearer()

@router.get("/test")
async def admin_test(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Test admin endpoint"""
    user = await verify_admin_token(credentials.credentials)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return {"message": "Admin endpoint working", "user": user.username}

@router.post("/upload/markdown-simple")
async def upload_markdown_simple(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Upload markdown file WITHOUT AI embeddings"""
    user = await verify_admin_token(credentials.credentials)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not file.filename.endswith(('.md', '.markdown')):
        raise HTTPException(status_code=400, detail="Only Markdown files supported")
    
    try:
        # Read file content
        content = await file.read()
        markdown_content = content.decode('utf-8')
        
        # Simple parsing - look for game_id in frontmatter
        game_id = "unknown"
        
        # Try to extract game_id from frontmatter
        if markdown_content.startswith('---'):
            try:
                import frontmatter
                post = frontmatter.loads(markdown_content)
                game_id = post.metadata.get('game_id', 'unknown')
                content_to_parse = post.content
            except Exception as e:
                print(f"Frontmatter parsing failed: {e}")
                content_to_parse = markdown_content
        else:
            content_to_parse = markdown_content
        
        # Count sections (## headers)
        import re
        sections = re.split(r'\n## ', content_to_parse)
        valid_sections = [s for s in sections if s.strip()]
        
        # Store rules in database
        db = get_database()
        if db is None:
            raise HTTPException(status_code=503, detail="Database not connected")
        
        chunks_collection = db["content_chunks"]
        stored_count = 0
        
        for section_idx, section in enumerate(valid_sections):
            if section_idx > 0:
                section = "## " + section
            
            # Extract title
            lines = section.split('\n')
            title = f"Rule {section_idx + 1}"
            if lines and lines[0].startswith('## '):
                title = lines[0][3:].strip()
                if title.startswith('Rule: '):
                    title = title[6:]
            
            # Create chunk
            chunk = {
                "game_id": game_id,
                "category_id": f"{game_id}_general",
                "content_type": "rule_text",
                "title": title,
                "content": section,
                "ancestors": [game_id, f"{game_id}_rules"],
                "chunk_metadata": {
                    "source_file": file.filename,
                    "section_index": section_idx,
                    "uploaded_without_ai": True
                },
                "created_at": datetime.utcnow()
            }
            
            await chunks_collection.insert_one(chunk)
            stored_count += 1
        
        # Update game rule count
        games_collection = db["games"]
        await games_collection.update_one(
            {"game_id": game_id},
            {
                "$inc": {"rule_count": stored_count},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        return {
            "success": True,
            "message": f"Successfully uploaded {file.filename}",
            "game_id": game_id,
            "rules_stored": stored_count,
            "sections_parsed": len(valid_sections)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/debug/parse-markdown")
async def debug_parse_markdown(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Debug markdown parsing"""
    user = await verify_admin_token(credentials.credentials)
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        content = await file.read()
        markdown_content = content.decode('utf-8')
        
        # Show raw content preview
        debug_info = {
            "filename": file.filename,
            "file_size": len(markdown_content),
            "starts_with_frontmatter": markdown_content.startswith('---'),
            "first_100_chars": markdown_content[:100],
            "has_game_id_text": "game_id" in markdown_content
        }
        
        # Try frontmatter parsing
        if markdown_content.startswith('---'):
            try:
                import frontmatter
                post = frontmatter.loads(markdown_content)
                debug_info.update({
                    "frontmatter_parsed": True,
                    "frontmatter": post.metadata,
                    "game_id_found": post.metadata.get('game_id', 'NOT_FOUND'),
                    "content_preview": post.content[:100] + "..."
                })
            except Exception as e:
                debug_info.update({
                    "frontmatter_parsed": False,
                    "frontmatter_error": str(e)
                })
        
        return debug_info
        
    except Exception as e:
        return {"error": str(e)}