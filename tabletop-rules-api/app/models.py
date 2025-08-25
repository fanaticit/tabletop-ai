# app/models.py - Corrected for Pydantic v2
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    game_system: str = Field(..., min_length=1, max_length=100)
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = []
    confidence_score: Optional[float] = None
    token_usage: Optional[Dict[str, int]] = None

# Enhanced chat response with structured content (using forward reference)
class StructuredChatResponse(BaseModel):
    query: str
    game_system: str
    structured_response: 'StructuredRuleResponse'
    search_method: str = "text_regex"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StreamResponse(BaseModel):
    type: str  # 'context', 'content', 'complete'
    data: Dict[str, Any]

# Fixed Game model with correct Pydantic v2 syntax
class Game(BaseModel):
    game_id: str = Field(..., min_length=1, max_length=50, description="Unique game identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Display name of the game")
    publisher: Optional[str] = Field(None, max_length=100)
    version: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    complexity: str = Field(default="medium", pattern="^(easy|medium|hard)$")  # Fixed: pattern instead of regex
    min_players: int = Field(default=1, ge=1, le=100)
    max_players: int = Field(default=2, ge=1, le=100)
    rule_count: int = Field(default=0, ge=0)
    categories: List[str] = Field(default_factory=list)
    ai_tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    auto_registered: bool = Field(default=True, description="True if registered automatically from upload")

class GameSummary(BaseModel):
    """Lightweight game model for lists"""
    game_id: str
    name: str
    rule_count: int
    complexity: str
    ai_tags: List[str] = []

# Upload-related models
class BulkUploadResponse(BaseModel):
    task_id: str
    status: str
    message: str

class UploadStatus(BaseModel):
    task_id: str
    status: str  # processing, completed, failed
    started_at: datetime
    completed_at: Optional[datetime] = None
    progress: float  # 0-100
    total_chunks: int = 0
    processed_chunks: int = 0
    games_registered: List[str] = []
    errors: List[Dict[str, Any]] = []
    filename: Optional[str] = None
    files: Optional[List[str]] = None

class MarkdownValidationResult(BaseModel):
    valid: bool
    has_frontmatter: bool = False
    has_headers: bool = False
    estimated_chunks: int = 0
    extracted_game_id: Optional[str] = None
    preview: Optional[str] = None
    error: Optional[str] = None

# Structured response models for gaming rule explanations
class ContentType(str, Enum):
    SUMMARY = "summary"
    EXPLANATION = "explanation" 
    EXAMPLES = "examples"
    EDGE_CASES = "edge_cases"

class RuleSection(BaseModel):
    id: str = Field(..., description="Unique section identifier")
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    type: ContentType
    level: int = Field(..., ge=0, le=3)
    collapsible: bool = True
    expanded: bool = False
    subsections: Optional[List['RuleSection']] = []

class RuleSource(BaseModel):
    type: str = Field(..., pattern="^(rulebook|faq|designer_notes|community)$")
    reference: str
    url: Optional[str] = None
    page: Optional[int] = None

class RuleSummary(BaseModel):
    text: str = Field(..., max_length=500)
    confidence: float = Field(..., ge=0.0, le=1.0)

class StructuredRuleResponse(BaseModel):
    id: str
    content: Dict[str, Any] = Field(default_factory=lambda: {
        "summary": {"text": "", "confidence": 0.0},
        "sections": [],
        "sources": []
    })

    class Config:
        # Enable forward references for self-referencing models
        from_attributes = True

# Update models to handle forward references
RuleSection.model_rebuild()
StructuredChatResponse.model_rebuild()

# Content chunk model
class ContentChunk(BaseModel):
    id: Optional[str] = None
    game_id: str
    category_id: str
    content_type: str
    title: str
    content: str
    ancestors: List[str]
    chunk_metadata: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)

# API response models
class GamesListResponse(BaseModel):
    games: List[GameSummary]
    total_count: int
    message: str = "Games are automatically registered when uploading Markdown rule files"

class APIStats(BaseModel):
    total_games: int
    total_rules: int
    games_by_complexity: Dict[str, int]
    average_rules_per_game: float