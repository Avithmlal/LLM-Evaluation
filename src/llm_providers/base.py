from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass
import time

@dataclass
class LLMResponse:
    """Standardized response from LLM providers"""
    content: str
    tokens_used: int
    response_time_ms: float
    cost_usd: float
    model_name: str
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    def __init__(self, model_config: Dict[str, Any]):
        self.model_config = model_config
        self.name = model_config.get("name", "unknown")
        self.model_id = model_config.get("model_id", "unknown")
        self.cost_per_1k_tokens = model_config.get("cost_per_1k_tokens", 0.0)
        self.max_tokens = model_config.get("max_tokens", 4096)
    
    @abstractmethod
    async def generate_completion(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate completion for given prompt"""
        pass
    
    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        pass
    
    def calculate_cost(self, tokens_used: int) -> float:
        """Calculate cost based on tokens used"""
        return (tokens_used / 1000) * self.cost_per_1k_tokens
    
    def _create_response(self, content: str, tokens_used: int, start_time: float, error: str = None) -> LLMResponse:
        """Helper to create standardized response"""
        response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        cost = self.calculate_cost(tokens_used) if not error else 0.0
        
        return LLMResponse(
            content=content,
            tokens_used=tokens_used,
            response_time_ms=response_time,
            cost_usd=cost,
            model_name=self.name,
            error=error
        ) 