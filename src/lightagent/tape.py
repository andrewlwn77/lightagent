# src/lightagent/tape.py
from enum import Enum
from typing import List, Optional, Any
from datetime import datetime
import uuid
from pydantic import BaseModel, Field
from .models.base import BaseMetadata
from .utils.logging import get_logger

logger = get_logger(__name__)

class StepType(str, Enum):
    THOUGHT = "thought"
    ACTION = "action"
    OBSERVATION = "observation"

class StepMetadata(BaseMetadata):
    """Metadata for a step in the tape."""
    agent: str = Field(description="Hierarchical name of the agent that generated the step")
    node: str = Field(description="Name of the node that generated the step")
    prompt_id: Optional[str] = Field(default=None, description="ID linking to the prompt that generated this step")

class Step(BaseModel):
    """A single step in the tape."""
    type: StepType
    content: Any = Field(description="The actual content of the step")
    metadata: StepMetadata
    step_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class TapeMetadata(BaseModel):
    """Metadata for the entire tape."""
    author: str = Field(description="Agent or environment that created/modified the tape")
    parent_id: Optional[str] = Field(default=None, description="ID of parent tape if this is a continuation")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    tape_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class Tape(BaseModel):
    """A sequence of steps representing an agent's memory and actions."""
    steps: List[Step] = Field(default_factory=list)
    metadata: TapeMetadata = Field(default_factory=lambda: TapeMetadata(author="root"))

    def append(self, step: Step) -> None:
        """Add a new step to the tape."""
        logger.debug(f"Adding step to tape: type={step.type}, agent={step.metadata.agent}, node={step.metadata.node}")
        self.steps.append(step)
        logger.debug(f"Step {step.step_id} added successfully")
    
    def get_steps_by_type(self, step_type: StepType) -> List[Step]:
        """Get all steps of a specific type."""
        logger.debug(f"Retrieving steps of type: {step_type}")
        steps = [step for step in self.steps if step.type == step_type]
        logger.debug(f"Found {len(steps)} steps of type {step_type}")
        return steps

    def get_steps_by_agent(self, agent_name: str) -> List[Step]:
        """Get all steps generated by a specific agent."""
        logger.debug(f"Retrieving steps for agent: {agent_name}")
        steps = [step for step in self.steps if step.metadata.agent == agent_name]
        logger.debug(f"Found {len(steps)} steps for agent {agent_name}")
        return steps

    def get_last_step(self) -> Optional[Step]:
        """Get the most recent step in the tape."""
        if not self.steps:
            logger.debug("No steps found in tape")
            return None
        last_step = self.steps[-1]
        logger.debug(f"Retrieved last step: type={last_step.type}, agent={last_step.metadata.agent}")
        return last_step

    def clone(self) -> 'Tape':
        """Create a copy of the tape with new metadata."""
        return Tape(
            steps=self.steps.copy(),
            metadata=TapeMetadata(
                author=self.metadata.author,
                parent_id=self.metadata.tape_id
            )
        )

# Example usage showing how to create thoughts and actions with specific content types
class SearchAction(BaseModel):
    """Example of a structured action content."""
    tool: str
    query: str

class SearchResult(BaseModel):
    """Example of a structured observation content."""
    results: List[str]

def create_example_tape() -> Tape:
    # Create a new tape
    tape = Tape()
    
    # Add a thought step
    thought = Step(
        type=StepType.THOUGHT,
        content="I should search for information about TapeAgents",
        metadata=StepMetadata(agent="search_agent", node="planning_node")
    )
    tape.append(thought)
    
    # Add an action step with structured content
    action = Step(
        type=StepType.ACTION,
        content=SearchAction(tool="web_search", query="TapeAgents github"),
        metadata=StepMetadata(agent="search_agent", node="action_node")
    )
    tape.append(action)
    
    # Add an observation step with structured content
    observation = Step(
        type=StepType.OBSERVATION,
        content=SearchResult(results=["Found github.com/ServiceNow/TapeAgents"]),
        metadata=StepMetadata(agent="environment", node="web_search")
    )
    tape.append(observation)
    
    return tape

if __name__ == "__main__":
    # Example usage
    tape = create_example_tape()
    
    # Demonstrate JSON serialization
    print("Tape JSON:")
    print(tape.model_dump_json(indent=2))
    
    # Get all thoughts
    thoughts = tape.get_steps_by_type(StepType.THOUGHT)
    print(f"\nNumber of thoughts: {len(thoughts)}")
    
    # Get all steps by the search agent
    search_steps = tape.get_steps_by_agent("search_agent")
    print(f"Number of search agent steps: {len(search_steps)}")
    
    # Create a continuation tape
    new_tape = tape.clone()
    print(f"New tape parent ID: {new_tape.metadata.parent_id}")