import openai
import time
import os
from typing import Dict, Any
from .base import BaseLLMProvider, LLMResponse

class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM Provider"""
    
    def __init__(self, model_config: Dict[str, Any]):
        super().__init__(model_config)
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY", "dummy-key-for-demo")
        )
    
    async def generate_completion(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate completion using OpenAI API"""
        start_time = time.time()
        
        try:
            # Check if we have a real API key
            if os.getenv("OPENAI_API_KEY", "dummy-key-for-demo") == "dummy-key-for-demo":
                # Mock response for demo purposes
                return self._create_mock_response(prompt, start_time)
            
            response = await self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                temperature=kwargs.get("temperature", 0.7)
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            return self._create_response(content, tokens_used, start_time)
            
        except Exception as e:
            error_msg = f"OpenAI API error: {str(e)}"
            return self._create_response("", 0, start_time, error_msg)
    
    def _create_mock_response(self, prompt: str, start_time: float) -> LLMResponse:
        """Create mock response for demo purposes"""
        # Simulate processing time
        import asyncio
        import random
        
        # Mock responses based on prompt content
        if "summarize" in prompt.lower() or "summary" in prompt.lower():
            content = "This is a mock summary of the provided text. The key points include the main topics discussed and their relevance to the overall context."
        elif "?" in prompt:
            content = "This is a mock answer to your question. The response addresses the key aspects of your inquiry with relevant information."
        elif "reasoning" in prompt.lower() or "logic" in prompt.lower():
            content = "This is a mock reasoning response. Step 1: Analyze the premises. Step 2: Apply logical rules. Step 3: Draw conclusions based on the evidence."
        else:
            content = f"This is a mock response from {self.name}. The input was processed and this is the generated output based on the prompt."
        
        # Mock token estimation (roughly 4 chars per token)
        tokens_used = len(prompt + content) // 4
        
        # Add some randomness to simulate real API variance
        response_time = (time.time() - start_time) * 1000 + random.uniform(100, 500)
        cost = self.calculate_cost(tokens_used)
        
        return LLMResponse(
            content=content,
            tokens_used=tokens_used,
            response_time_ms=response_time,
            cost_usd=cost,
            model_name=self.name,
            error=None
        )
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation: 4 chars per token)"""
        return len(text) // 4 