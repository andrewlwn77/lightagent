"""LLM-aware agent implementations."""

from typing import Dict, Any
import json
from .base import BaseAgent
from ..models.steps import StepResult
from ..llm import LLMConfig, create_llm

class LLMAwareAgent(BaseAgent):
    """Agent with LLM capabilities using Mirascope."""
    
    def __init__(self, name: str, llm_config: LLMConfig, **kwargs):
        super().__init__(name, **kwargs)
        self.llm = create_llm(llm_config)
    
    async def think(self, context: Dict[str, Any]) -> StepResult:
        """Generate thoughts using LLM."""
        try:
            prompt = self._create_thinking_prompt(context)
            response = await self.llm.generate(prompt)
            
            return StepResult(
                success=True,
                output=response.text,
                metadata={
                    "context_keys": list(context.keys()),
                    "model": response.model,
                    "usage": response.usage
                }
            )
        except Exception as e:
            return StepResult(success=False, error=str(e))
    
    async def act(self, thought: Any) -> StepResult:
        """Execute action based on thought."""
        return StepResult(
            success=True,
            output={"action": "process_thought", "thought": thought.content}
        )
    
    async def observe(self, action: Any) -> StepResult:
        """Process observation after action."""
        return StepResult(
            success=True,
            output=f"Observed result of action: {action.content}"
        )
    
    def _create_thinking_prompt(self, context: Dict[str, Any]) -> str:
        """Create prompt for thinking step."""
        return f"Given the context {json.dumps(context)}, what should be the next action?"