import pytest
import asyncio
from sqlmodel import SQLModel
from typing import AsyncGenerator, Generator
from lightagent.storage import TapeStore
from lightagent.tape import Tape, Step, StepMetadata, StepType
from lightagent.agents.simple import SimpleAgent

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
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
async def simple_agent() -> AsyncGenerator[SimpleAgent, None]:
    """Create a simple agent for testing."""
    agent = SimpleAgent("test_agent")
    yield agent