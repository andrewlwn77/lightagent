"""HuggingFace integration through Mirascope OpenAI compatibility."""

from typing import Any, Dict, Optional
from mirascope.core.openai import openai_call, OpenAICallParams
from openai import AsyncOpenAI
from ..base import BaseLLM, LLMConfig, LLMResponse
from ...utils.logging import get_logger

logger = get_logger(__name__)

class HuggingFaceLLM(BaseLLM):
    """HuggingFace integration using OpenAI compatibility layer."""
    
    def __init__(self, config: LLMConfig, client: Optional[AsyncOpenAI] = None):
        super().__init__(config)
        # Configure for HF endpoint
        base_url = config.additional_params.get("base_url", "https://api.huggingface.co")
        self.client = client or AsyncOpenAI(api_key=config.api_key, base_url=base_url)
        self.call_params = {
            "model": config.model,
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
            **config.additional_params
        }    

    async def generate(self, prompt: str) -> LLMResponse:
        """Generate text using OpenAI/HuggingFace."""
        from mirascope.core.openai import openai_call

        @openai_call(
            model=self.config.model,
            client=self.client,
            call_params=self.call_params
        )
        async def _generate_text(text: str) -> str:
            return text

        try:
            # Call the decorated function, which will return the API response
            response = await _generate_text(prompt)
            
            # Log the response object for debugging
            logger.debug(f"Response object: {response}")
            logger.debug(f"Response type: {type(response)}")
            logger.debug(f"Response attributes: {dir(response)}")
            
            # Access the content from the response object
            content = response.content  # Access content directly
            
            # Access usage as an attribute
            usage = response.usage
            usage_dict = {
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "total_tokens": usage.total_tokens if usage else 0
            }

            return LLMResponse(
                text=content,
                raw_response=response.model_dump(),  # Convert the Pydantic model to a dictionary
                usage=usage_dict,
                model=self.config.model
            )
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise ValueError(f"Error generating text: {str(e)}")
    
    async def close(self):
        """Clean up resources."""
        if hasattr(self.client, 'close') and callable(self.client.close):
            await self.client.close()