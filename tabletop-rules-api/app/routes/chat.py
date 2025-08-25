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
    """Generate a direct answer following CLAUDE.md template format."""
    query_lower = query.lower()
    
    # Generate bold direct answers (1-2 sentences max)
    if "how" in query_lower and ("move" in query_lower or "moves" in query_lower):
        if "pawn" in query_lower:
            return "**Pawns move one square forward, or two squares forward on their first move.**"
        elif "knight" in query_lower:
            return "**Knights move in an L-shape: two squares in one direction, then one square perpendicular.**"
        elif "king" in query_lower:
            return "**The king moves one square in any direction (horizontal, vertical, or diagonal).**"
        elif "queen" in query_lower:
            return "**The queen moves any number of squares in any direction—horizontally, vertically, or diagonally.**"
        elif "bishop" in query_lower:
            return "**Bishops move diagonally any number of squares.**"
        elif "rook" in query_lower:
            return "**Rooks move horizontally or vertically any number of squares.**"
        else:
            return "**Each chess piece has unique movement patterns.**"
    
    elif "what" in query_lower:
        if "checkmate" in query_lower:
            return "**Checkmate occurs when the king is in check and cannot escape capture, ending the game.**"
        elif "check" in query_lower and "checkmate" not in query_lower:
            return "**Check is when the king is under attack and must be moved to safety immediately.**"
        elif "castling" in query_lower or "castle" in query_lower:
            return "**Castling is a special move that allows the king and rook to move simultaneously for king safety.**"
        elif "en passant" in query_lower:
            return "**En passant is a special pawn capture rule for pawns that move two squares forward.**"
    
    elif "can" in query_lower:
        if "pawn" in query_lower:
            return "**Pawns can move forward, capture diagonally, and promote when reaching the opposite end.**"
        elif "king" in query_lower and "castle" in query_lower:
            return "**The king can castle if neither piece has moved and there are no pieces between them.**"
    
    # Generic fallback with bold formatting
    return f"**Found specific rules about {query.lower().replace('how does', '').replace('what is', '').strip()}.**"

def generate_detailed_explanation(query_lower: str, primary_rule: dict, rules: List) -> str:
    """Generate detailed explanation with concrete example following CLAUDE.md format."""
    
    if "pawn" in query_lower and "move" in query_lower:
        return """Pawns are unique pieces with special movement rules. They move straight forward one square to an unoccupied square. On a pawn's very first move from its starting position, it has the option to advance two squares forward instead of one, provided both squares are unoccupied. Unlike other pieces, pawns capture differently than they move—they capture diagonally forward one square.

Example: A pawn on e2 can move to e3, or jump to e4 on its first move. If there's an opponent piece on d3 or f3, the pawn can capture it by moving diagonally."""
    
    elif "knight" in query_lower and "move" in query_lower:
        return """The knight has the most distinctive movement pattern in chess. It moves in an "L" shape: exactly two squares in one direction (horizontal or vertical), then exactly one square perpendicular to that direction. Knights are the only pieces that can "jump over" other pieces during their move.

Example: A knight on d4 can move to c2, e2, b3, f3, b5, f5, c6, or e6. Even if there are pieces blocking the path, the knight can still reach its destination squares."""
    
    elif "king" in query_lower and "move" in query_lower:
        return """The king is the most important piece but has limited mobility. It can move exactly one square in any direction: horizontally, vertically, or diagonally. The king can never move into check (a square attacked by an opponent's piece).

Example: A king on e1 can move to d1, d2, e2, f2, or f1, provided these squares are not under attack by enemy pieces."""
    
    elif "queen" in query_lower and "move" in query_lower:
        return """The queen is the most powerful piece, combining the movement abilities of both the rook and bishop. She can move any number of squares horizontally, vertically, or diagonally, but cannot jump over other pieces.

Example: A queen on d4 can move to any square along the d-file, 4th rank, or the diagonals (a1-h8 and g1-a7), as long as the path is clear."""
    
    elif "bishop" in query_lower and "move" in query_lower:
        return """Bishops move exclusively along diagonal lines. Each player starts with two bishops: one on light squares and one on dark squares, and they remain on their respective colored squares throughout the game.

Example: A bishop on c1 can move to b2, a3, d2, e3, f4, g5, or h6, but cannot reach any dark squares."""
    
    elif "rook" in query_lower and "move" in query_lower:
        return """Rooks move in straight lines along ranks (horizontal) and files (vertical). They can move any number of squares in these directions but cannot move diagonally or jump over pieces.

Example: A rook on a1 can move anywhere along the a-file (a2-a8) or the first rank (b1-h1), provided the path is unobstructed."""
    
    elif "checkmate" in query_lower:
        return """Checkmate ends the game immediately. It occurs when the king is in check (under attack) and has no legal moves to escape capture. This includes being unable to move to a safe square, block the attack, or capture the attacking piece.

Example: If a queen on d8 attacks a king on e8, and the king cannot move to f8 (blocked by own pieces) or capture the queen, it's checkmate."""
    
    elif "check" in query_lower and "checkmate" not in query_lower:
        return """When a king is in check, the player must immediately resolve the threat on their next move. There are three ways to get out of check: move the king to a safe square, capture the attacking piece, or block the attack with another piece.

Example: If a rook attacks your king, you can move the king away, capture the rook with another piece, or place a piece between the rook and king."""
    
    elif "castling" in query_lower or "castle" in query_lower:
        return """Castling is a special defensive move involving the king and either rook. The king moves two squares toward the rook, and the rook moves to the square the king crossed. This can only be done if neither piece has moved, there are no pieces between them, and the king is not in check.

Example: In kingside castling, the king moves from e1 to g1, and the rook moves from h1 to f1, all in one turn."""
    
    # Generic fallback using actual rule content
    if primary_rule and primary_rule.get("content"):
        content = primary_rule["content"]
        # Extract first meaningful paragraph
        clean_content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
        paragraphs = [p.strip() for p in clean_content.split('\n\n') if len(p.strip()) > 50]
        if paragraphs:
            return paragraphs[0][:400] + ("..." if len(paragraphs[0]) > 400 else "")
    
    return f"This rule covers the specific mechanics and applications within {query_lower}."

def generate_related_rules(query_lower: str, related_rules: List) -> str:
    """Generate related rules bullet points following CLAUDE.md format."""
    
    if "pawn" in query_lower and "move" in query_lower:
        return """• **En Passant**: Special pawn capture rule when opponent pawn moves two squares
• **Pawn Promotion**: Pawns reaching the opposite end transform into any piece
• **Illegal Moves**: Moving pawns backward or sideways is forbidden"""
    
    elif "knight" in query_lower and "move" in query_lower:
        return """• **Knight Forks**: Knights can attack multiple pieces simultaneously
• **Knight vs Bishop**: Knights and bishops have roughly equal value in most positions  
• **Knight Outposts**: Knights are strongest when placed on secure squares in enemy territory"""
    
    elif "king" in query_lower and "move" in query_lower:
        return """• **Castling**: Special king move for safety and rook development
• **King and Pawn Endings**: Basic endgame technique with king and pawns
• **Stalemate**: When the king has no legal moves but is not in check"""
    
    elif "queen" in query_lower and "move" in query_lower:
        return """• **Queen Development**: Generally develop minor pieces before the queen
• **Queen Trades**: Exchanging queens often leads to endgames
• **Queen vs Multiple Pieces**: Queen can sometimes fight several minor pieces"""
    
    elif "bishop" in query_lower and "move" in query_lower:
        return """• **Bishop Pair**: Having both bishops is usually advantageous
• **Good vs Bad Bishop**: Bishops blocked by own pawns are considered "bad"
• **Fianchetto**: Developing bishops on long diagonals from knight squares"""
    
    elif "rook" in query_lower and "move" in query_lower:
        return """• **Castling**: Rooks participate in the special castling move
• **Rook Endgames**: Most common type of chess endgame
• **Open Files**: Rooks are most effective on open or semi-open files"""
    
    elif "checkmate" in query_lower:
        return """• **Check**: When the king is under attack but can escape
• **Stalemate**: King has no legal moves but is not in check (draw)
• **Basic Checkmate Patterns**: Queen and king vs king, rook and king vs king"""
    
    elif "check" in query_lower:
        return """• **Checkmate**: When check cannot be escaped, ending the game
• **Discovery Check**: Moving a piece to reveal check from another piece
• **Double Check**: Rare situation when king is in check from two pieces"""
    
    elif "castling" in query_lower:
        return """• **Kingside Castling**: More common, castling toward the h-file
• **Queenside Castling**: Less common, castling toward the a-file
• **Castling Rights**: Permanently lost if king or rook moves"""
    
    # Generate from actual related rules if available
    if related_rules:
        bullets = []
        for rule in related_rules[:5]:
            title = rule.get("title", "Unknown Rule")
            content = rule.get("content", "")
            # Extract first sentence as description
            first_sentence = content.split('.')[0].strip() if content else "Additional rule information"
            if len(first_sentence) > 100:
                first_sentence = first_sentence[:100] + "..."
            bullets.append(f"• **{title}**: {first_sentence}")
        return '\n'.join(bullets)
    
    return """• **General Rules**: Basic chess principles and guidelines
• **Special Moves**: Advanced techniques and exceptions
• **Strategy Tips**: Positional and tactical considerations"""

def create_structured_gaming_response(rules: List, query: str, game_id: str) -> StructuredRuleResponse:
    """Create structured gaming response following CLAUDE.md template format."""
    
    if not rules:
        return StructuredRuleResponse(
            id=str(uuid.uuid4()),
            content={
                "summary": {
                    "text": f"**No specific rules found for '{query}' in {game_id}.** Try a different search term.",
                    "confidence": 0.3
                },
                "sections": [],
                "sources": []
            }
        )
    
    primary_rule = rules[0]
    query_lower = query.lower()
    
    # 1. DIRECT ANSWER (Bold, 1-2 sentences)
    direct_answer = generate_contextual_summary(query, primary_rule, len(rules))
    
    # 2. DETAILED EXPLANATION with concrete example
    detailed_explanation = generate_detailed_explanation(query_lower, primary_rule, rules)
    
    # 3. RELATED RULES (3-5 bullet points)
    related_rules_content = generate_related_rules(query_lower, rules[1:5] if len(rules) > 1 else [])
    
    # Create single section with the complete template format
    template_content = f"""{direct_answer}

{detailed_explanation}

**Related Rules**
{related_rules_content}"""
    
    sections = [RuleSection(
        id=f"template_response_{uuid.uuid4().hex[:8]}",
        title="Rule Explanation",
        content=template_content,
        type=ContentType.EXPLANATION,
        level=1,
        collapsible=True,
        expanded=True
    )]
    
    # Create sources
    sources = []
    for rule in rules[:3]:
        category = rule.get("category_id", "general")
        sources.append(RuleSource(
            type="rulebook",
            reference=f"{game_id.title()} Rules - {category.title()}",
            page=None
        ))
    
    # High confidence for template responses
    confidence = 0.95
    
    return StructuredRuleResponse(
        id=str(uuid.uuid4()),
        content={
            "summary": {
                "text": direct_answer,
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