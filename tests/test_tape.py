import pytest
from robotape.tape import Tape, Step, StepMetadata, StepType
from uuid import UUID

def test_tape_creation():
    """Test basic tape creation."""
    tape = Tape()
    assert tape.steps == []
    assert tape.metadata.author == "root"
    assert isinstance(UUID(tape.metadata.tape_id), UUID)

def test_step_creation():
    """Test step creation."""
    step = Step(
        type=StepType.THOUGHT,
        content="Test thought",
        metadata=StepMetadata(agent="test_agent", node="test_node")
    )
    assert step.type == StepType.THOUGHT
    assert step.content == "Test thought"
    assert step.metadata.agent == "test_agent"

def test_tape_append():
    """Test appending steps to tape."""
    tape = Tape()
    step = Step(
        type=StepType.THOUGHT,
        content="Test thought",
        metadata=StepMetadata(agent="test_agent", node="test_node")
    )
    tape.append(step)
    assert len(tape.steps) == 1
    assert tape.steps[0].content == "Test thought"

def test_tape_get_steps_by_type(sample_tape):
    """Test filtering steps by type."""
    thoughts = sample_tape.get_steps_by_type(StepType.THOUGHT)
    actions = sample_tape.get_steps_by_type(StepType.ACTION)
    assert len(thoughts) == 1
    assert len(actions) == 1
    assert thoughts[0].content == "Test thought"

def test_tape_get_steps_by_agent(sample_tape):
    """Test filtering steps by agent."""
    agent_steps = sample_tape.get_steps_by_agent("test_agent")
    assert len(agent_steps) == 2

def test_tape_clone(sample_tape):
    """Test tape cloning."""
    new_tape = sample_tape.clone()
    assert new_tape.metadata.parent_id == sample_tape.metadata.tape_id
    assert len(new_tape.steps) == len(sample_tape.steps)