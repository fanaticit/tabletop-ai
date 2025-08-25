# app/routes/chat.py - Fixed version

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database import get_database
from app.models import (
    StructuredChatResponse, 
    StructuredRuleResponse, 
    RuleSection, 
    RuleSource, 
    ContentType
)
from pydantic import BaseModel
from typing import List, Optional
import re
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/chat", tags=["chat"])

def score_rules_for_query(rules: List, query_text: str) -> List:
    """Score and rank rules based on relevance to the query."""
    
    # Extract key terms from query (ignore common words)
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'how', 'what', 'when', 'where', 'why', 'is', 'are', 'can', 'do', 'does'}
    query_terms = [term.strip('?.,!') for term in query_text.lower().split() if term not in stop_words]
    
    # Score each rule
    scored_rules = []
    for rule in rules:
        score = 0
        title = rule.get("title", "").lower()
        content = rule.get("content", "").lower()
        category = rule.get("category_id", "").lower()
        
        # High priority scoring for titles - exact matches get big boost
        for term in query_terms:
            if term in title:
                score += 10  # Title matches are highly relevant
                if term == title.lower():
                    score += 20  # Exact title match is extremely relevant
            
            # Medium priority for content matches
            content_matches = content.count(term)
            score += content_matches * 2
            
            # Category relevance
            if term in category:
                score += 5
        
        # Special chess-specific logic with more precise scoring
        if "pawn" in query_terms:
            if "pawn movement" in title.lower() or "pawn movement" in content.lower():
                score += 25  # Very high priority for pawn movement rules
            elif "pawn" in title.lower():
                score += 20  # High priority for pawn-specific titles
            elif "pawn" in content.lower():
                score += 15  # Medium priority for pawn mentions
            
            # Penalize rules that mention pawns negatively
            if "illegal" in title.lower() or "penalty" in title.lower():
                score -= 10
        elif "knight" in query_terms:
            if "knight movement" in title.lower() or "knight movement" in content.lower():
                score += 25
            elif "knight" in title.lower():
                score += 20
            elif "knight" in content.lower():
                score += 15
            if "illegal" in title.lower() or "penalty" in title.lower():
                score -= 10
        elif "king" in query_terms:
            if "king movement" in title.lower() or "king movement" in content.lower():
                score += 25
            elif "king" in title.lower():
                score += 20
            elif "king" in content.lower():
                score += 15
            if "illegal" in title.lower() or "penalty" in title.lower():
                score -= 10
        elif "queen" in query_terms:
            if "queen movement" in title.lower() or "queen movement" in content.lower():
                score += 25
            elif "queen" in title.lower():
                score += 20
            elif "queen" in content.lower():
                score += 15
            if "illegal" in title.lower() or "penalty" in title.lower():
                score -= 10
        elif "bishop" in query_terms:
            if "bishop movement" in title.lower() or "bishop movement" in content.lower():
                score += 25
            elif "bishop" in title.lower():
                score += 20
            elif "bishop" in content.lower():
                score += 15
            if "illegal" in title.lower() or "penalty" in title.lower():
                score -= 10
        elif "rook" in query_terms:
            if "rook movement" in title.lower() or "rook movement" in content.lower():
                score += 25
            elif "rook" in title.lower():
                score += 20
            elif "rook" in content.lower():
                score += 15
            if "illegal" in title.lower() or "penalty" in title.lower():
                score -= 10
        elif "castle" in query_terms or "castling" in query_terms:
            if "castle" in title or "castle" in content or "castling" in title or "castling" in content:
                score += 15
        elif "checkmate" in query_terms:
            if "checkmate" in title or "checkmate" in content:
                score += 15
        elif "check" in query_terms and "checkmate" not in query_terms:
            if "check" in title or "check" in content:
                score += 15
        elif "move" in query_terms or "movement" in query_terms:
            if "movement" in category or "move" in title or "move" in content:
                score += 10
            # Bonus for combining movement with piece type
            for piece in ["pawn", "knight", "king", "queen", "bishop", "rook"]:
                if piece in query_terms and piece in title.lower():
                    score += 15
                
        # Penalize very general rules unless specifically asked for
        if "overview" in title.lower() and "overview" not in query_terms:
            score -= 5
        if "setup" in title.lower() and "setup" not in query_terms and "start" not in query_terms:
            score -= 3
            
        scored_rules.append((score, rule))
    
    # Sort by score (highest first) and return rules only
    scored_rules.sort(key=lambda x: x[0], reverse=True)
    return [rule for score, rule in scored_rules if score > 0]

def create_structured_no_results_response(query: str, game_id: str) -> StructuredChatResponse:
    """Create structured response for no results."""
    empty_response = StructuredRuleResponse(
        id=str(uuid.uuid4()),
        content={
            "summary": {
                "text": f"No specific rules found for '{query}' in {game_id}. Try a different search term.",
                "confidence": 0.1
            },
            "sections": [],
            "sources": []
        }
    )
    
    return StructuredChatResponse(
        query=query,
        game_system=game_id,
        structured_response=empty_response,
        search_method="enhanced_scoring"
    )

def generate_contextual_summary(query: str, primary_rule: dict, num_rules: int) -> str:
    """Generate a contextual summary based on the query and primary rule."""
    query_lower = query.lower()
    title = primary_rule.get("title", "")
    content = primary_rule.get("content", "")
    
    # Try to extract specific information based on the question type
    if "how" in query_lower and ("move" in query_lower or "moves" in query_lower):
        # Movement questions
        if "pawn" in query_lower:
            return "Pawns move one square forward, or two squares on their first move."
        elif "knight" in query_lower:
            return "Knights move in an L-shape: two squares in one direction, then one square perpendicular."
        elif "king" in query_lower:
            return "The king moves one square in any direction (horizontal, vertical, or diagonal)."
        elif "queen" in query_lower:
            return "The queen moves any number of squares in any direction."
        elif "bishop" in query_lower:
            return "Bishops move diagonally any number of squares."
        elif "rook" in query_lower:
            return "Rooks move horizontally or vertically any number of squares."
        else:
            return f"Found movement rules for chess pieces."
    
    elif "what" in query_lower:
        if "checkmate" in query_lower:
            return "Checkmate occurs when the king is in check and cannot escape capture."
        elif "check" in query_lower:
            return "Check is when the king is under attack and must be moved to safety."
        elif "castling" in query_lower or "castle" in query_lower:
            return "Castling is a special move involving the king and a rook."
        elif "en passant" in query_lower:
            return "En passant is a special pawn capture rule."
    
    elif "can" in query_lower:
        if "pawn" in query_lower:
            return "Pawns can move forward one square, capture diagonally, and promote when reaching the end."
        elif "king" in query_lower and "castle" in query_lower:
            return "The king can castle if neither the king nor rook has moved and there are no pieces between them."
    
    # Extract first sentence from content as fallback
    if content:
        first_sentence = content.split('.')[0].strip()
        if len(first_sentence) > 20 and len(first_sentence) < 200:
            return first_sentence + "."
    
    # Default to rule title
    if title:
        return title.strip('.')
    
    return f"Found {num_rules} rule{'s' if num_rules > 1 else ''} about {query.lower()}."

def create_structured_gaming_response(rules: List, query: str, game_id: str) -> StructuredRuleResponse:
    """Create structured gaming response following three-tier architecture."""
    
    if not rules:
        return StructuredRuleResponse(
            id=str(uuid.uuid4()),
            content={
                "summary": {
                    "text": f"No specific rules found for '{query}' in {game_id}. Try a different search term.",
                    "confidence": 0.3
                },
                "sections": [],
                "sources": []
            }
        )
    
    # Generate contextual summary - brief answer (Level 1)
    primary_rule = rules[0]
    summary_text = generate_contextual_summary(query, primary_rule, len(rules))
    
    # Create sections with progressive disclosure (Level 2)
    sections = []
    
    # Basic explanation section
    if rules:
        main_content = ""
        for i, rule in enumerate(rules[:3]):  # Limit to top 3 for summary
            rule_content = rule["content"]
            # Clean up content - remove markdown headers and excess whitespace
            clean_content = re.sub(r'^#+\s*', '', rule_content, flags=re.MULTILINE)
            clean_content = re.sub(r'\n\s*\n', '\n\n', clean_content.strip())
            
            if i == 0:
                main_content = clean_content[:400] + ("..." if len(clean_content) > 400 else "")
            else:
                main_content += f"\n\n**Related: {rule['title']}**\n{clean_content[:200]}{'...' if len(clean_content) > 200 else ''}"
        
        sections.append(RuleSection(
            id=f"basic_rule_{uuid.uuid4().hex[:8]}",
            title="Rule Explanation",
            content=main_content,
            type=ContentType.EXPLANATION,
            level=1,
            collapsible=True,
            expanded=True
        ))
    
    # Examples section if we have multiple rules
    if len(rules) > 1:
        examples_content = "Here are related rules that might help:\n\n"
        for rule in rules[1:3]:  # Show 2nd and 3rd rules as examples
            examples_content += f"• **{rule['title']}**: {rule['content'][:150]}{'...' if len(rule['content']) > 150 else ''}\n\n"
        
        sections.append(RuleSection(
            id=f"examples_{uuid.uuid4().hex[:8]}",
            title="Related Rules",
            content=examples_content.strip(),
            type=ContentType.EXAMPLES,
            level=2,
            collapsible=True,
            expanded=False
        ))
    
    # Create sources (Level 3)
    sources = []
    for rule in rules[:3]:  # Top 3 rules only
        category = rule.get("category_id", "general")
        sources.append(RuleSource(
            type="rulebook",
            reference=f"{game_id.title()} Rules - {category.title()}",
            page=None  # Would be populated with actual page numbers in production
        ))
    
    # Calculate confidence based on relevance
    confidence = min(0.95, 0.6 + (len(rules) * 0.1))  # Higher confidence with more matches
    
    return StructuredRuleResponse(
        id=str(uuid.uuid4()),
        content={
            "summary": {
                "text": summary_text,
                "confidence": confidence
            },
            "sections": sections,
            "sources": sources
        }
    )

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
        query_text = chat_query.query.lower()
        game_id = chat_query.game_system.lower()
        
        # Get all rules for the game first
        all_rules = await db.content_chunks.find({
            "game_id": game_id
        }).to_list(length=50)
        
        if not all_rules:
            return create_structured_no_results_response(chat_query.query, game_id)
        
        # Improved search with relevance scoring
        scored_rules = score_rules_for_query(all_rules, query_text)
        
        # Take top 5 most relevant rules
        rules = scored_rules[:5]
        
        if not rules:
            return create_structured_no_results_response(chat_query.query, game_id)
        
        # Create structured response following gaming interface patterns
        structured_response = create_structured_gaming_response(rules, chat_query.query, game_id)
        
        return StructuredChatResponse(
            query=chat_query.query,
            game_system=game_id,
            structured_response=structured_response,
            search_method="enhanced_scoring"
        )
        
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