"""Base classes for LLM integration."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from mirascope.core import BaseDynamicConfig
from abc import ABC, abstractmethod

class LLMConfig(BaseModel):
    """Configuration for LLM providers."""
    api_key: Optional[str] = None
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    additional_params: Dict[str, Any] = Field(default_factory=dict)
    provider_name: str = "openai"  # Default to OpenAI

class LLMResponse(BaseModel):
    """Standardized response from LLM providers."""
    text: str
    raw_response: Dict[str, Any]
    usage: Dict[str, int]
    model: str

class BaseLLM(ABC):
    """Base class for LLM integrations using Mirascope."""
    
    def __init__(self, config: LLMConfig):
        self.config = config
    
    @abstractmethod
    async def generate(self, prompt: str) -> LLMResponse:
        """Generate text from prompt."""
        pass

    @abstractmethod
    async def close(self):
        """Clean up resources."""
        pass

def create_llm(config: LLMConfig) -> BaseLLM:
    """Factory function to create LLM instances."""
    from .providers import AnthropicLLM, OpenAILLM, HuggingFaceLLM
    
    providers = {
        "anthropic": AnthropicLLM,
        "openai": OpenAILLM,
        "huggingface": HuggingFaceLLM
    }
    
    provider_class = providers.get(config.provider_name)
    if not provider_class:
        raise ValueError(f"Unsupported LLM provider: {config.provider_name}")
    
    return provider_class(config)