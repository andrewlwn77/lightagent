from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from ..tape import Tape, Step
from ..models.steps import StepType, StepStatus, StepResult

class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
        self.current_tape: Optional[Tape] = None

    @abstractmethod
    async def think(self, context: Dict[str, Any]) -> StepResult:
        """Generate a thought step."""
        pass

    @abstractmethod
    async def act(self, thought: Step) -> StepResult:
        """Generate an action based on a thought."""
        pass

    @abstractmethod
    async def observe(self, action: Step) -> StepResult:
        """Process an observation after an action."""
        pass

    async def execute_step(self, step: Step) -> StepResult:
        """Execute a single step."""
        if not self.current_tape:
            raise ValueError("No active tape")

        try:
            if step.type == StepType.THOUGHT:
                result = await self.think(step.content)
            elif step.type == StepType.ACTION:
                result = await self.act(step)
            elif step.type == StepType.OBSERVATION:
                result = await self.observe(step)
            else:
                raise ValueError(f"Unknown step type: {step.type}")

            return result
        except Exception as e:
            return StepResult(
                success=False,
                error=str(e),
                metadata={"exception_type": type(e).__name__}
            )