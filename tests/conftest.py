import pytest
import asyncio
from sqlmodel import SQLModel
from typing import Generator
from robotape.storage import TapeStore
from robotape.tape import Tape, Step, StepMetadata, StepType
from robotape.agents.simple import SimpleAgent

@pytest.fixture(scope="function")
async def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture
def test_db():
    """Create test database."""
    database_url = "sqlite:///test.db"
    store = TapeStore(database_url)
    SQLModel.metadata.create_all(store.engine)
    yield store
    SQLModel.metadata.drop_all(store.engine)

@pytest.fixture
def sample_tape():
    """Create a sample tape for testing."""
    tape = Tape()
    
    # Add a thought step
    thought = Step(
        type=StepType.THOUGHT,
        content="Test thought",
        metadata=StepMetadata(agent="test_agent", node="test_node")
    )
    tape.append(thought)
    
    # Add an action step
    action = Step(
        type=StepType.ACTION,
        content={"action": "test_action"},
        metadata=StepMetadata(agent="test_agent", node="test_node")
    )
    tape.append(action)
    
    return tape

@pytest.fixture
def simple_agent(event_loop):
    """Create a simple agent for testing."""
    return SimpleAgent("test_agent")