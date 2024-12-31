import pytest
from lightagent.agents.simple import SimpleAgent
from lightagent.models.steps import StepType, StepStatus, StepResult
from lightagent.tape import Step, StepMetadata

@pytest.mark.asyncio
async def test_agent_think(simple_agent):
    """Test agent thinking."""
    context = {"test": "data"}
    result = await simple_agent.think(context)
    assert result.success
    assert "Processing context" in result.output

@pytest.mark.asyncio
async def test_agent_act(simple_agent):
    """Test agent acting."""
    thought = Step(
        type=StepType.THOUGHT,
        content="Test thought",
        metadata=StepMetadata(agent="test_agent", node="test_node")
    )
    result = await simple_agent.act(thought)
    assert result.success
    assert isinstance(result.output, dict)
    assert "based_on_thought" in result.output

@pytest.mark.asyncio
async def test_agent_observe(simple_agent):
    """Test agent observation."""
    action = Step(
        type=StepType.ACTION,
        content={"type": "test_action"},
        metadata=StepMetadata(agent="test_agent", node="test_node")
    )
    result = await simple_agent.observe(action)
    assert result.success
    assert isinstance(result.output, str)

@pytest.mark.asyncio
async def test_agent_execute_step(simple_agent):
    """Test full step execution."""
    # Create a tape
    tape = Tape()
    simple_agent.current_tape = tape
    
    # Create and execute a thought step
    step = Step(
        type=StepType.THOUGHT,
        content={"test": "data"},
        metadata=StepMetadata(agent="test_agent", node="test_node")
    )
    result = await simple_agent.execute_step(step)
    assert result.success