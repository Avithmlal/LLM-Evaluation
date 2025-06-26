import time
import random
from typing import Dict, Any
from .base import BaseLLMProvider, LLMResponse

class MockProvider(BaseLLMProvider):
    """Mock LLM Provider for testing and demo purposes"""
    
    def __init__(self, model_config: Dict[str, Any]):
        super().__init__(model_config)
    
    async def generate_completion(self, prompt: str, **kwargs) -> LLMResponse:
        """Generate mock completion"""
        start_time = time.time()
        
        # Simulate processing time
        await self._simulate_processing_time()
        
        # Generate mock content based on prompt
        content = self._generate_mock_content(prompt)
        
        # Mock token calculation
        tokens_used = self.estimate_tokens(prompt + content)
        
        return self._create_response(content, tokens_used, start_time)
    
    async def _simulate_processing_time(self):
        """Simulate realistic API response time"""
        import asyncio
        delay = random.uniform(0.1, 0.8)  # 100-800ms delay
        await asyncio.sleep(delay)
    
    def _generate_mock_content(self, prompt: str) -> str:
        """Generate mock content based on prompt characteristics"""
        prompt_lower = prompt.lower()
        
        # Mock responses for different categories
        if any(word in prompt_lower for word in ["summarize", "summary"]):
            return self._mock_summarization_response(prompt)
        elif "?" in prompt:
            return self._mock_qa_response(prompt)
        elif any(word in prompt_lower for word in ["reasoning", "logic", "conclude"]):
            return self._mock_reasoning_response(prompt)
        else:
            return self._mock_general_response(prompt)
    
    def _mock_summarization_response(self, prompt: str) -> str:
        """Generate mock summarization response"""
        templates = [
            "The main points of the text include: key developments in the field, important trends and patterns, and significant implications for stakeholders.",
            "Summary: The content discusses several critical aspects including primary findings, methodological approaches, and practical applications.",
            "Key takeaways from the text: major themes, supporting evidence, and conclusions drawn from the analysis."
        ]
        return random.choice(templates)
    
    def _mock_qa_response(self, prompt: str) -> str:
        """Generate mock Q&A response"""
        templates = [
            "Based on the available information, the answer addresses the specific question while providing relevant context and supporting details.",
            "The response to your question involves multiple factors that contribute to a comprehensive understanding of the topic.",
            "To answer your question: the key information indicates specific findings that directly relate to your inquiry."
        ]
        return random.choice(templates)
    
    def _mock_reasoning_response(self, prompt: str) -> str:
        """Generate mock reasoning response"""
        return """Following logical analysis:

Step 1: Examine the given premises and identify key relationships
Step 2: Apply relevant logical rules and principles
Step 3: Draw valid conclusions based on the established premises

Therefore, the logical conclusion follows from the systematic application of reasoning principles to the given information."""
    
    def _mock_general_response(self, prompt: str) -> str:
        """Generate mock general response"""
        return f"This is a mock response from {self.name}. The system has processed your input and generated this sample output to demonstrate functionality. In a real implementation, this would contain the actual model response."
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for mock provider"""
        return len(text) // 4  # Standard approximation 