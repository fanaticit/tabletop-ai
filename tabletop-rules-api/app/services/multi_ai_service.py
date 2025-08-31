# app/services/multi_ai_service.py - Multi-Provider AI Service
from typing import List, Dict, Optional, Any, Literal
import json
import time
from datetime import datetime
from openai import AsyncOpenAI
from app.config import settings
import httpx
import asyncio

AIProvider = Literal["openai", "anthropic"]

class MultiAIService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None  # We'll use httpx for Anthropic
        self.usage_log = []
    
    def _ensure_openai_client(self):
        """Initialize OpenAI client with proper error handling"""
        if self.openai_client is None:
            if not settings.openai_api_key or settings.openai_api_key == "your-openai-api-key-here":
                raise ValueError("OpenAI API key not configured. Set OPENAI_API_KEY environment variable.")
            
            self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
    
    def _ensure_anthropic_client(self):
        """Ensure Anthropic API key is available"""
        if not settings.anthropic_api_key or settings.anthropic_api_key == "your-anthropic-api-key-here":
            raise ValueError("Anthropic API key not configured. Set ANTHROPIC_API_KEY environment variable.")
    
    def _log_usage(self, provider: str, model: str, input_tokens: int, output_tokens: int, cost_estimate: float):
        """Log API usage for cost monitoring"""
        usage_entry = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
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
    
    def _calculate_cost(self, provider: str, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on provider pricing"""
        if provider == "openai" and model == "gpt-4o-mini":
            # GPT-4o-mini pricing: $0.15/1M input tokens, $0.60/1M output tokens
            input_cost = (input_tokens / 1_000_000) * 0.15
            output_cost = (output_tokens / 1_000_000) * 0.60
            return input_cost + output_cost
        elif provider == "anthropic":
            if "claude-3-5-sonnet" in model:
                # Claude 3.5 Sonnet pricing: $3.00/1M input tokens, $15.00/1M output tokens
                input_cost = (input_tokens / 1_000_000) * 3.00
                output_cost = (output_tokens / 1_000_000) * 15.00
                return input_cost + output_cost
            elif "claude-3-haiku" in model:
                # Claude 3 Haiku pricing: $0.25/1M input tokens, $1.25/1M output tokens
                input_cost = (input_tokens / 1_000_000) * 0.25
                output_cost = (output_tokens / 1_000_000) * 1.25
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
    
    def _create_system_prompt(self, game_id: str, provider: str) -> str:
        """Create game-specific system prompt optimized for each provider"""
        base_prompt = f"""You are an expert {game_id} rules advisor. Provide accurate, helpful responses about {game_id} rules based on the provided context.

RESPONSE FORMAT REQUIREMENTS:
1. **Direct Answer**: Start with a bold, clear 1-2 sentence answer
2. **Detailed Explanation**: Provide context and examples 
3. **Related Rules**: List 3-5 related rules with brief descriptions

GUIDELINES:
- Always cite specific rules from the provided context
- Use bold formatting for key terms and direct answers
- Provide concrete examples when possible
- If unsure, mention limitations rather than guessing
- Focus on practical gameplay implications"""
        
        if provider == "anthropic":
            # Claude prefers more structured instructions
            return f"{base_prompt}\n\nIMPORTANT: Structure your response clearly with the bold answer first, followed by explanation and related rules."
        
        return base_prompt
    
    async def _call_openai(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        self._ensure_openai_client()
        
        try:
            start_time = time.time()
            response = await self.openai_client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            response_time = time.time() - start_time
            
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content.strip()
                
                # Extract usage information
                usage = response.usage
                input_tokens = usage.prompt_tokens if usage else 0
                output_tokens = usage.completion_tokens if usage else 0
                cost = self._calculate_cost("openai", settings.openai_model, input_tokens, output_tokens)
                
                # Log usage
                self._log_usage("openai", settings.openai_model, input_tokens, output_tokens, cost)
                
                return {
                    "success": True,
                    "response": content,
                    "provider": "openai",
                    "model": settings.openai_model,
                    "response_time": response_time,
                    "usage": {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens,
                        "estimated_cost": cost
                    },
                    "ai_powered": True,
                    "error": None
                }
            else:
                return {"success": False, "error": "No response from OpenAI", "ai_powered": False}
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return {"success": False, "error": str(e), "ai_powered": False}
    
    async def _call_anthropic(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        """Call Anthropic Claude API using httpx"""
        self._ensure_anthropic_client()
        
        try:
            start_time = time.time()
            
            # Anthropic API call using httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                        "x-api-key": settings.anthropic_api_key
                    },
                    json={
                        "model": settings.anthropic_model,
                        "max_tokens": 800,
                        "temperature": 0.1,
                        "system": system_prompt,
                        "messages": [
                            {"role": "user", "content": user_message}
                        ]
                    },
                    timeout=30.0
                )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("content") and len(data["content"]) > 0:
                    content = data["content"][0].get("text", "").strip()
                    
                    # Extract usage information
                    usage = data.get("usage", {})
                    input_tokens = usage.get("input_tokens", 0)
                    output_tokens = usage.get("output_tokens", 0)
                    cost = self._calculate_cost("anthropic", settings.anthropic_model, input_tokens, output_tokens)
                    
                    # Log usage
                    self._log_usage("anthropic", settings.anthropic_model, input_tokens, output_tokens, cost)
                    
                    return {
                        "success": True,
                        "response": content,
                        "provider": "anthropic",
                        "model": settings.anthropic_model,
                        "response_time": response_time,
                        "usage": {
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                            "total_tokens": input_tokens + output_tokens,
                            "estimated_cost": cost
                        },
                        "ai_powered": True,
                        "error": None
                    }
                else:
                    return {"success": False, "error": "No content in Anthropic response", "ai_powered": False}
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {"error": response.text}
                return {"success": False, "error": f"Anthropic API error {response.status_code}: {error_data}", "ai_powered": False}
                
        except httpx.TimeoutException:
            return {"success": False, "error": "Anthropic API timeout", "ai_powered": False}
        except Exception as e:
            print(f"Anthropic API error: {e}")
            return {"success": False, "error": str(e), "ai_powered": False}
    
    async def generate_rule_response(
        self, 
        query: str, 
        game_id: str, 
        rules_context: List[Dict[str, Any]],
        provider: Optional[AIProvider] = None,
        compare_providers: bool = False
    ) -> Dict[str, Any]:
        """
        Generate rule response using specified AI provider(s)
        
        Args:
            query: User's question
            game_id: Game identifier
            rules_context: Relevant rules for context
            provider: Specific provider to use ("openai" or "anthropic")
            compare_providers: If True, call both providers and return comparison
        """
        
        # Use specified provider or default
        target_provider = provider or settings.default_ai_provider
        
        # Format context
        context = self._format_rules_context(rules_context, query, game_id)
        user_message = f"{context}\n\nPlease provide a comprehensive answer to: {query}"
        
        if compare_providers:
            # Call both providers for comparison
            tasks = []
            
            # Add OpenAI if key available
            if settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here":
                system_prompt_openai = self._create_system_prompt(game_id, "openai")
                tasks.append(("openai", self._call_openai(system_prompt_openai, user_message)))
            
            # Add Anthropic if key available
            if settings.anthropic_api_key and settings.anthropic_api_key != "your-anthropic-api-key-here":
                system_prompt_anthropic = self._create_system_prompt(game_id, "anthropic")
                tasks.append(("anthropic", self._call_anthropic(system_prompt_anthropic, user_message)))
            
            if not tasks:
                return {"success": False, "error": "No AI providers configured", "ai_powered": False}
            
            # Run both providers concurrently
            results = {}
            for provider_name, task in tasks:
                try:
                    result = await task
                    results[provider_name] = result
                except Exception as e:
                    results[provider_name] = {"success": False, "error": str(e), "ai_powered": False}
            
            return {
                "success": True,
                "comparison": results,
                "ai_powered": True,
                "query": query,
                "game_id": game_id
            }
        
        else:
            # Single provider call
            system_prompt = self._create_system_prompt(game_id, target_provider)
            
            if target_provider == "openai":
                return await self._call_openai(system_prompt, user_message)
            elif target_provider == "anthropic":
                return await self._call_anthropic(system_prompt, user_message)
            else:
                return {"success": False, "error": f"Unknown provider: {target_provider}", "ai_powered": False}
    
    async def test_connection(self, provider: Optional[AIProvider] = None) -> Dict[str, Any]:
        """Test connection to AI provider(s)"""
        
        if provider:
            providers_to_test = [provider]
        else:
            providers_to_test = []
            if settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here":
                providers_to_test.append("openai")
            if settings.anthropic_api_key and settings.anthropic_api_key != "your-anthropic-api-key-here":
                providers_to_test.append("anthropic")
        
        results = {}
        
        for prov in providers_to_test:
            try:
                test_result = await self.generate_rule_response(
                    query="What is chess?",
                    game_id="chess",
                    rules_context=[{
                        "title": "Chess Overview", 
                        "content": "Chess is a strategic board game played between two players.",
                        "category_id": "general"
                    }],
                    provider=prov
                )
                
                results[prov] = {
                    "status": "connected" if test_result.get("success") else "failed",
                    "model": test_result.get("model", "unknown"),
                    "response_length": len(test_result.get("response", "")),
                    "error": test_result.get("error")
                }
                
            except Exception as e:
                results[prov] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "providers_tested": providers_to_test,
            "results": results,
            "default_provider": settings.default_ai_provider
        }
    
    def get_usage_summary(self) -> Dict[str, Any]:
        """Get comprehensive usage summary for all providers"""
        if not self.usage_log:
            return {
                "total_requests": 0,
                "total_cost": 0.0,
                "providers": {},
                "recent_activity": []
            }
        
        # Group by provider
        provider_stats = {}
        total_cost = 0.0
        
        for entry in self.usage_log:
            provider = entry["provider"]
            cost = entry["estimated_cost"]
            
            if provider not in provider_stats:
                provider_stats[provider] = {
                    "requests": 0,
                    "total_tokens": 0,
                    "total_cost": 0.0,
                    "models": {}
                }
            
            provider_stats[provider]["requests"] += 1
            provider_stats[provider]["total_tokens"] += entry["total_tokens"]
            provider_stats[provider]["total_cost"] += cost
            total_cost += cost
            
            model = entry["model"]
            if model not in provider_stats[provider]["models"]:
                provider_stats[provider]["models"][model] = 0
            provider_stats[provider]["models"][model] += 1
        
        return {
            "total_requests": len(self.usage_log),
            "total_cost": round(total_cost, 6),
            "providers": provider_stats,
            "recent_activity": self.usage_log[-10:] if len(self.usage_log) > 10 else self.usage_log
        }

# Create global instance
multi_ai_service = MultiAIService()