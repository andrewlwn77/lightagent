# src/robotape/models/base.py
from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from uuid import UUID, uuid4

class BaseMetadata(BaseModel):
    """Base metadata for steps and tapes."""
    id: UUID = Field(default_factory=uuid4)
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class StepMetadata(BaseMetadata):
    """Metadata for a step in the tape."""
    agent: str = Field(description="Hierarchical name of the agent that generated the step")
    node: str = Field(description="Name of the node that generated the step")
    prompt_id: Optional[str] = Field(default=None, description="ID linking to the prompt that generated this step")