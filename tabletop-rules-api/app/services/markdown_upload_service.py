# app/services/markdown_upload_service.py - Updated with games registry
import frontmatter
import markdown
import tiktoken
import re
from typing import Dict, List, Any, Tuple
from uuid import uuid4
from datetime import datetime
from app.database import get_database
from app.services.ai_service import ai_service
from app.services.games_service import games_service
import asyncio

class MarkdownUploadService:
    def __init__(self):
        self.upload_tasks = {}  # In production, use Redis or database
        self.encoding = tiktoken.get_encoding("cl100k_base")  # GPT-4 encoding

    async def start_markdown_upload(self, file: UploadFile, user_id: str) -> str:
        """Start background Markdown upload process"""
        task_id = str(uuid4())
        
        # Store initial task status
        self.upload_tasks[task_id] = {
            "status": "processing",
            "started_at": datetime.utcnow(),
            "user_id": user_id,
            "filename": file.filename,
            "progress": 0,
            "total_chunks": 0,
            "processed_chunks": 0,
            "games_registered": [],
            "errors": []
        }
        
        # Start background processing
        asyncio.create_task(self._process_markdown_upload(task_id, file))
        
        return task_id

    async def start_batch_upload(self, files: List[UploadFile], user_id: str) -> str:
        """Start batch upload of multiple Markdown files"""
        task_id = str(uuid4())
        
        self.upload_tasks[task_id] = {
            "status": "processing",
            "started_at": datetime.utcnow(),
            "user_id": user_id,
            "files": [f.filename for f in files],
            "progress": 0,
            "total_files": len(files),
            "processed_files": 0,
            "total_chunks": 0,
            "processed_chunks": 0,
            "games_registered": [],
            "errors": []
        }
        
        asyncio.create_task(self._process_batch_upload(task_id, files))
        
        return task_id

    async def _process_markdown_upload(self, task_id: str, file: UploadFile):
        """Background task for processing single Markdown upload"""
        try:
            contents = await file.read()
            markdown_content = contents.decode('utf-8')
            
            # Parse Markdown with frontmatter
            parsed_content = await self._parse_markdown_content(markdown_content, file.filename)
            
            # Register or update game information
            game_info = await self._register_game_from_content(parsed_content)
            self.upload_tasks[task_id]["games_registered"].append(game_info["game_id"])
            
            # Chunk the content semantically
            chunks = await self._chunk_markdown_content(parsed_content)
            
            # Update total chunks
            self.upload_tasks[task_id]["total_chunks"] = len(chunks)
            
            # Process chunks in batches
            await self._store_chunks_in_batches(task_id, chunks)
            
            # Update game rule count
            await games_service.update_rule_count(game_info["game_id"], len(chunks))
            
            # Mark as completed
            self.upload_tasks[task_id]["status"] = "completed"
            self.upload_tasks[task_id]["completed_at"] = datetime.utcnow()
            
        except Exception as e:
            self.upload_tasks[task_id]["status"] = "failed"
            self.upload_tasks[task_id]["error"] = str(e)

    async def _register_game_from_content(self, parsed_content: Dict[str, Any]) -> Dict[str, Any]:
        """Register game from parsed Markdown content"""
        
        # Extract game info from frontmatter and content
        frontmatter_data = parsed_content.get("metadata", {})
        content_game_info = games_service.extract_game_info_from_content(
            parsed_content["content"], 
            parsed_content["filename"]
        )
        
        # Merge frontmatter with extracted info (frontmatter takes precedence)
        game_data = {
            **content_game_info,
            **frontmatter_data  # Frontmatter overrides extracted data
        }
        
        # Register the game
        return await games_service.register_game(game_data)

    async def _parse_markdown_content(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse Markdown content and extract metadata"""
        
        # Parse frontmatter if present
        post = frontmatter.loads(content)
        
        return {
            "filename": filename,
            "metadata": post.metadata,
            "content": post.content,
            "full_markdown": content
        }

    async def _chunk_markdown_content(self, parsed_content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk Markdown content semantically (250-500 tokens per chunk)"""
        
        content = parsed_content["content"]
        
        # Get game_id from metadata or extract from filename
        game_id = (parsed_content["metadata"].get("game_id") or 
                  games_service.extract_game_id_from_filename(parsed_content["filename"]))
        
        # Split by major sections (## headers)
        sections = re.split(r'\n## ', content)
        
        chunks = []
        
        for section_idx, section in enumerate(sections):
            if not section.strip():
                continue
                
            # Add back the ## for non-first sections
            if section_idx > 0:
                section = "## " + section
            
            # Extract rule title and metadata
            rule_info = self._extract_rule_info(section)
            
            # Register category with game
            await games_service.add_category_to_game(game_id, rule_info['category'])
            
            # Split large sections into smaller chunks
            section_chunks = self._split_section_by_tokens(section, rule_info)
            
            for chunk_idx, chunk_content in enumerate(section_chunks):
                chunk = {
                    "game_id": game_id,
                    "category_id": f"{game_id}_{rule_info['category'].lower().replace(' ', '_').replace('→', '_')}",
                    "content_type": "rule_text",
                    "title": f"{rule_info['title']} (Part {chunk_idx + 1})" if len(section_chunks) > 1 else rule_info['title'],
                    "content": chunk_content,
                    "ancestors": [
                        game_id, 
                        f"{game_id}_rules", 
                        f"{game_id}_{rule_info['category'].lower().replace(' ', '_').replace('→', '_')}"
                    ],
                    "chunk_metadata": {
                        "tokens": len(self.encoding.encode(chunk_content)),
                        "complexity_score": rule_info['complexity_score'],
                        "mandatory": rule_info['mandatory'],
                        "frequently_referenced": rule_info.get('frequently_referenced', False),
                        "source_file": parsed_content["filename"],
                        "section_index": section_idx,
                        "chunk_index": chunk_idx
                    },
                    "created_at": datetime.utcnow()
                }
                chunks.append(chunk)
        
        return chunks

    def _extract_rule_info(self, section: str) -> Dict[str, Any]:
        """Extract rule information from Markdown section"""
        
        lines = section.split('\n')
        title = "Unknown Rule"
        category = "general"
        complexity_score = 0.5
        mandatory = True
        
        # Extract title from first line (## Rule Title)
        if lines and lines[0].startswith('## '):
            title = lines[0][3:].strip()
            # Remove "Rule: " prefix if present
            if title.startswith('Rule: '):
                title = title[6:]
        
        # Look for metadata in bold format
        for line in lines:
            if '**Category**:' in line:
                category = line.split('**Category**:')[1].strip()
            elif '**Complexity**:' in line:
                complexity_text = line.split('**Complexity**:')[1].strip().lower()
                if 'beginner' in complexity_text or 'easy' in complexity_text:
                    complexity_score = 0.3
                elif 'intermediate' in complexity_text or 'medium' in complexity_text:
                    complexity_score = 0.6
                elif 'advanced' in complexity_text or 'hard' in complexity_text:
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

    def _split_section_by_tokens(self, section: str, rule_info: Dict[str, Any]) -> List[str]:
        """Split large sections into token-appropriate chunks (250-500 tokens)"""
        
        tokens = self.encoding.encode(section)
        
        # If section is within token limit, return as single chunk
        if len(tokens) <= 500:
            return [section]
        
        # Split by subsections (### headers) first
        subsections = re.split(r'\n### ', section)
        chunks = []
        current_chunk = ""
        
        for subsection_idx, subsection in enumerate(subsections):
            if subsection_idx > 0:
                subsection = "### " + subsection
            
            subsection_tokens = len(self.encoding.encode(subsection))
            current_chunk_tokens = len(self.encoding.encode(current_chunk))
            
            # If adding this subsection would exceed 500 tokens, save current chunk
            if current_chunk and (current_chunk_tokens + subsection_tokens) > 500:
                chunks.append(current_chunk.strip())
                current_chunk = subsection
            else:
                current_chunk += "\n" + subsection if current_chunk else subsection
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks

    async def _store_chunks_in_batches(self, task_id: str, chunks: List[Dict[str, Any]]):
        """Store chunks in database with batch processing"""
        db = get_database()
        collection = db["content_chunks"]
        
        batch_size = 50  # Process 50 chunks at a time
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            
            # Generate embeddings for batch
            for chunk in batch:
                try:
                    embedding = await ai_service.generate_embedding(chunk["content"])
                    chunk["rule_embedding"] = embedding
                    
                except Exception as e:
                    self.upload_tasks[task_id]["errors"].append({
                        "chunk_title": chunk["title"],
                        "error": f"Embedding generation failed: {str(e)}"
                    })
                    # Skip chunks that fail embedding generation
                    continue
            
            # Filter out chunks without embeddings
            valid_chunks = [chunk for chunk in batch if "rule_embedding" in chunk]
            
            # Insert batch
            if valid_chunks:
                try:
                    await collection.insert_many(valid_chunks, ordered=False)
                    self.upload_tasks[task_id]["processed_chunks"] += len(valid_chunks)
                    
                except Exception as e:
                    self.upload_tasks[task_id]["errors"].append({
                        "batch_start": i,
                        "error": f"Database insertion failed: {str(e)}"
                    })
            
            # Update progress
            self.upload_tasks[task_id]["progress"] = (
                self.upload_tasks[task_id]["processed_chunks"] / 
                self.upload_tasks[task_id]["total_chunks"] * 100
            )

    async def _process_batch_upload(self, task_id: str, files: List[UploadFile]):
        """Background task for processing batch upload"""
        try:
            all_chunks = []
            games_registered = set()
            
            for file_idx, file in enumerate(files):
                try:
                    contents = await file.read()
                    markdown_content = contents.decode('utf-8')
                    
                    # Parse and chunk each file
                    parsed_content = await self._parse_markdown_content(markdown_content, file.filename)
                    
                    # Register game
                    game_info = await self._register_game_from_content(parsed_content)
                    games_registered.add(game_info["game_id"])
                    
                    file_chunks = await self._chunk_markdown_content(parsed_content)
                    all_chunks.extend(file_chunks)
                    
                    # Update progress
                    self.upload_tasks[task_id]["processed_files"] = file_idx + 1
                    
                except Exception as e:
                    self.upload_tasks[task_id]["errors"].append({
                        "file": file.filename,
                        "error": str(e)
                    })
            
            # Update games registered list
            self.upload_tasks[task_id]["games_registered"] = list(games_registered)
            
            # Update total chunks
            self.upload_tasks[task_id]["total_chunks"] = len(all_chunks)
            
            # Process all chunks
            await self._store_chunks_in_batches(task_id, all_chunks)
            
            # Update rule counts for all games
            for game_id in games_registered:
                game_chunks = [c for c in all_chunks if c["game_id"] == game_id]
                await games_service.update_rule_count(game_id, len(game_chunks))
            
            # Mark as completed
            self.upload_tasks[task_id]["status"] = "completed"
            self.upload_tasks[task_id]["completed_at"] = datetime.utcnow()
            
        except Exception as e:
            self.upload_tasks[task_id]["status"] = "failed"
            self.upload_tasks[task_id]["error"] = str(e)

    async def validate_markdown_file(self, file: UploadFile) -> Dict[str, Any]:
        """Validate Markdown file structure"""
        try:
            contents = await file.read()
            markdown_content = contents.decode('utf-8')
            
            # Parse frontmatter
            post = frontmatter.loads(markdown_content)
            
            # Extract game info
            game_id = (post.metadata.get('game_id') or 
                      games_service.extract_game_id_from_filename(file.filename))
            
            # Check for required structure
            has_headers = bool(re.search(r'^##\s+', post.content, re.MULTILINE))
            
            # Estimate chunks
            estimated_chunks = len(re.split(r'\n## ', post.content))
            
            return {
                "valid": True,
                "has_frontmatter": bool(post.metadata),
                "has_headers": has_headers,
                "estimated_chunks": estimated_chunks,
                "extracted_game_id": game_id,
                "preview": post.content[:500] + "..." if len(post.content) > 500 else post.content
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}

    async def get_upload_status(self, task_id: str) -> Dict[str, Any]:
        """Get current status of upload task"""
        return self.upload_tasks.get(task_id)

markdown_upload_service = MarkdownUploadService()