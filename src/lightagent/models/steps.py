from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict

class StepType(str, Enum):
    """Types of steps in a tape."""
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"
    ERROR = "error"

class StepStatus(str, Enum):
    """Status of a step's execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class StepResult(BaseModel):
    """Result of a step execution."""
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)