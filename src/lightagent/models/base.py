from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
from uuid import UUID, uuid4

class BaseMetadata(BaseModel):
    """Base metadata model for steps and tapes."""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    id: UUID = Field(default_factory=uuid4)

class BaseContent(BaseModel):
    """Base content model with validation."""
    raw_content: Any
    validated_content: Optional[Dict[str, Any]] = None
    validation_errors: Optional[Dict[str, str]] = None