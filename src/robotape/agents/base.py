# src/robotape/agents/base.py
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

from ..tape import Tape, Step
from ..models.steps import StepType, StepStatus, StepResult
from ..utils.logging import get_logger

logger = get_logger(__name__)

class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        logger.debug(f"Initializing agent: {name} with config: {config}")
        self.name = name
        self.config = config or {}
        self.current_tape: Optional[Tape] = None
        logger.debug(f"Agent {name} initialized successfully")

    @abstractmethod
    async def think(self, context: Dict[str, Any]) -> StepResult:
        """Generate a thought step."""
        logger.debug(f"Agent {self.name} thinking with context: {context}")
        pass

    @abstractmethod
    async def act(self, thought: Step) -> StepResult:
        """Generate an action based on a thought."""
        logger.debug(f"Agent {self.name} acting on thought: {thought.content}")
        pass

    @abstractmethod
    async def observe(self, action: Step) -> StepResult:
        """Process an observation after an action."""
        logger.debug(f"Agent {self.name} observing result of action: {action.content}")
        pass

    async def execute_step(self, step: Step) -> StepResult:
        """Execute a single step."""
        if not self.current_tape:
            logger.error(f"Agent {self.name} attempted to execute step without active tape")
            raise ValueError("No active tape")

        logger.debug(f"Agent {self.name} executing step type: {step.type}")
        try:
            if step.type == StepType.THOUGHT:
                logger.debug(f"Agent {self.name} processing thought step")
                result = await self.think(step.content)
            elif step.type == StepType.ACTION:
                logger.debug(f"Agent {self.name} processing action step")
                result = await self.act(step)
            elif step.type == StepType.OBSERVATION:
                logger.debug(f"Agent {self.name} processing observation step")
                result = await self.observe(step)
            else:
                logger.error(f"Agent {self.name} encountered unknown step type: {step.type}")
                raise ValueError(f"Unknown step type: {step.type}")

            if result.success:
                logger.debug(f"Agent {self.name} successfully executed {step.type} step")
            else:
                logger.warning(f"Agent {self.name} step execution failed: {result.error}")
            return result
        except Exception as e:
            logger.error(f"Agent {self.name} encountered error executing {step.type} step: {str(e)}", exc_info=True)
            return StepResult(
                success=False,
                error=str(e),
                metadata={"exception_type": type(e).__name__}
            )