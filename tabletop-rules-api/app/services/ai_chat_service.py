# app/services/ai_chat_service.py - GPT-4o-mini Integration for Rule Responses
from typing import List, Dict, Optional, Any
import json
import time
from datetime import datetime
from openai import AsyncOpenAI
from app.config import settings

class AIChatService:
    def __init__(self):
        self.client = None
        self.usage_log = []
    
    def _ensure_client(self):
        """Initialize OpenAI client with proper error handling"""
        if self.client is None:
            if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here":
                raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
            
            self.client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    def _log_usage(self, model: str, input_tokens: int, output_tokens: int, cost_estimate: float):
        """Log API usage for cost monitoring"""
        usage_entry = {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "estimated_cost": cost_estimate
        }
        self.usage_log.append(usage_entry)
        
        # Keep only last 100 entries to prevent memory issues
        if len(self.usage_log) > 100:
            self.usage_log = self.usage_log[-100:]
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on GPT-4o-mini pricing"""
        if model == "gpt-4o-mini":
            # GPT-4o-mini pricing: $0.15/1M input tokens, $0.60/1M output tokens
            input_cost = (input_tokens / 1_000_000) * 0.15
            output_cost = (output_tokens / 1_000_000) * 0.60
            return input_cost + output_cost
        return 0.0
    
    def _format_rules_context(self, rules: List[Dict[str, Any]], query: str, game_id: str) -> str:
        """Format rules as context for AI consumption"""
        if not rules:
            return f"No specific rules found in the {game_id} rulebook for this query."
        
        context_parts = [f"Game: {game_id.title()}", f"User Query: {query}", "", "Relevant Rules:"]
        
        for i, rule in enumerate(rules[:5], 1):  # Limit to top 5 rules
            title = rule.get("title", f"Rule {i}")
            content = rule.get("content", "")
            category = rule.get("category_id", "general")
            
            # Clean and truncate content to prevent token bloat
            clean_content = content.replace('\n\n', ' ').strip()
            if len(clean_content) > 500:
                clean_content = clean_content[:500] + "..."
            
            context_parts.append(f"{i}. **{title}** (Category: {category})")
            context_parts.append(f"   {clean_content}")
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _create_system_prompt(self, game_id: str) -> str:
        """Create game-specific system prompt"""
        return f"""You are an expert {game_id} rules advisor. Provide accurate, helpful responses about {game_id} rules based on the provided context.

RESPONSE FORMAT REQUIREMENTS:
1. **Direct Answer**: Start with a bold, clear 1-2 sentence answer
2. **Detailed Explanation**: Provide context and examples 
3. **Related Rules**: List 3-5 related rules with brief descriptions

GUIDELINES:
- Always cite specific rules from the provided context
- Use concrete examples when possible
- If you're not certain, say so rather than guess
- Keep responses focused and practical
- Use the exact template format as shown in previous examples

Example format:
**[Direct answer in 1-2 sentences]**

[Detailed explanation with example]

**Related Rules**
• **Rule Name**: Brief description
• **Rule Name**: Brief description
• **Rule Name**: Brief description"""
    
    async def generate_rule_response(
        self, 
        query: str, 
        game_id: str, 
        rules_context: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate AI-powered rule response using GPT-4o-mini"""
        
        try:
            self._ensure_client()
            
            # Format context for AI
            formatted_context = self._format_rules_context(rules_context, query, game_id)
            system_prompt = self._create_system_prompt(game_id)
            
            # Create messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{formatted_context}\n\nQuestion: {query}"}
            ]
            
            # Make API call to GPT-4o-mini
            start_time = time.time()
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=800,  # Limit response length for cost control
                temperature=0.1,  # Low temperature for consistent rule explanations
                top_p=0.9
            )
            
            # Extract response data
            ai_response = response.choices[0].message.content
            usage = response.usage
            response_time = time.time() - start_time
            
            # Calculate and log costs
            input_tokens = usage.prompt_tokens if usage else 0
            output_tokens = usage.completion_tokens if usage else 0
            cost_estimate = self._calculate_cost("gpt-4o-mini", input_tokens, output_tokens)
            
            self._log_usage("gpt-4o-mini", input_tokens, output_tokens, cost_estimate)
            
            return {
                "response": ai_response,
                "ai_powered": True,
                "model": "gpt-4o-mini",
                "response_time": response_time,
                "usage": {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                    "estimated_cost": cost_estimate
                },
                "rules_used": len(rules_context),
                "confidence": "high" if rules_context else "low"
            }
            
        except Exception as e:
            # Return error info for fallback handling
            return {
                "error": str(e),
                "ai_powered": False,
                "fallback_required": True,
                "error_type": type(e).__name__
            }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test OpenAI connection with minimal cost"""
        try:
            self._ensure_client()
            
            start_time = time.time()
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say 'test successful' if you can read this."}],
                max_tokens=10,
                temperature=0
            )
            
            response_time = time.time() - start_time
            usage = response.usage
            cost = self._calculate_cost("gpt-4o-mini", usage.prompt_tokens, usage.completion_tokens)
            
            return {
                "success": True,
                "response_time": response_time,
                "test_cost": cost,
                "model": "gpt-4o-mini"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get usage statistics for monitoring"""
        if not self.usage_log:
            return {
                "total_requests": 0, 
                "total_cost": 0.0, 
                "total_tokens": 0,
                "average_cost_per_request": 0
            }
        
        total_cost = sum(entry["estimated_cost"] for entry in self.usage_log)
        total_tokens = sum(entry["total_tokens"] for entry in self.usage_log)
        total_requests = len(self.usage_log)
        
        return {
            "total_requests": total_requests,
            "total_cost": round(total_cost, 4),
            "total_tokens": total_tokens,
            "average_cost_per_request": round(total_cost / total_requests, 4) if total_requests > 0 else 0,
            "last_24h": len([e for e in self.usage_log if (datetime.now() - datetime.fromisoformat(e["timestamp"])).total_seconds() < 86400])
        }
    
    async def close(self):
        """Close the client connection"""
        if self.client:
            await self.client.aclose()

# Create singleton instance
ai_chat_service = AIChatService()