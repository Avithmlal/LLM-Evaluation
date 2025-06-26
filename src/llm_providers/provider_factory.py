from typing import Dict, Any
from .base import BaseLLMProvider
from .openai_provider import OpenAIProvider
from .anthropic_provider import AnthropicProvider
from .mock_provider import MockProvider

class LLMProviderFactory:
    """Factory for creating LLM providers"""
    
    _providers = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "mock": MockProvider
    }
    
    @classmethod
    def create_provider(cls, model_config: Dict[str, Any]) -> BaseLLMProvider:
        """Create provider instance based on configuration"""
        provider_type = model_config.get("provider", "mock")
        
        if provider_type not in cls._providers:
            raise ValueError(f"Unknown provider type: {provider_type}")
        
        provider_class = cls._providers[provider_type]
        return provider_class(model_config)
    
    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider types"""
        return list(cls._providers.keys())
    
    @classmethod
    def register_provider(cls, name: str, provider_class: type):
        """Register a new provider type"""
        cls._providers[name] = provider_class 