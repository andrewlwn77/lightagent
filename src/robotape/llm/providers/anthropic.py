"""Anthropic Claude integration using Mirascope."""

from typing import Any, Dict, Optional
from mirascope.core.anthropic import anthropic_call, AnthropicCallParams
from anthropic import AsyncAnthropic
from ..base import BaseLLM, LLMConfig, LLMResponse
from ...utils.logging import get_logger

logger = get_logger(__name__)

class AnthropicLLM(BaseLLM):
    """Anthropic Claude integration."""
    
    def __init__(self, config: LLMConfig, client: Optional[AsyncAnthropic] = None):
        super().__init__(config)
        self.client = client or AsyncAnthropic(api_key=config.api_key)
        self.call_params = {
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            **config.additional_params
        }
    
    async def generate(self, prompt: str) -> LLMResponse:
        """Generate text using Anthropic's Claude."""
        from mirascope.core.anthropic import anthropic_call
        
        @anthropic_call(
            model=self.config.model,
            client=self.client,
            call_params=self.call_params
        )
        async def _generate_text(text: str) -> str:
            return text
        
        try:
            response = await _generate_text(prompt)

            # Log the response object for debugging
            logger.debug(f"Response object: {response}")
            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"Response attributes: {dir(response)}")

            usage = response.usage if response.usage else None
            usage_dict = {
                "input_tokens": usage.input_tokens if usage else 0,
                "output_tokens": usage.output_tokens if usage else 0
            }
            
            return LLMResponse(
                text=response.content,
                raw_response=response.response.model_dump(),
                usage=usage_dict,
                model=self.config.model
            )
        except Exception as e:
            logger.error(f"Error generating text with Anthropic: {str(e)}")
            raise ValueError(f"Error generating text with Anthropic: {str(e)}")
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self.client, 'close') and callable(self.client.close):
            await self.client.close()