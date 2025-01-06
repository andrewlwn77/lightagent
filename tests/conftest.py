import pytest
import asyncio
import subprocess
import signal
import sys
from pathlib import Path
from typing import Generator, AsyncGenerator, Tuple
from sqlmodel import SQLModel

from robotape.storage import TapeStore
from robotape.tape import Tape, Step, StepMetadata, StepType
from robotape.agents.simple import SimpleAgent
from robotape.agents.mcpllm import MCPLLMAgent
from robotape.llm import LLMConfig
from robotape.utils.mcp import StdioServerParameters
from robotape.utils.logging import get_logger

logger = get_logger(__name__)

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

async def start_test_server() -> AsyncGenerator[subprocess.Popen, None]:
    """Start the test MCP server."""
    server_path = Path(__file__).parent / "data" / "test_server.py"
    
    logger.debug(f"Starting test MCP server from {server_path}")
    process = subprocess.Popen(
        [sys.executable, str(server_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Allow server time to start
    await asyncio.sleep(1)
    logger.debug("Test MCP server started")
    
    try:
        yield process
    finally:
        logger.debug("Shutting down test MCP server")
        process.send_signal(signal.SIGTERM)
        process.wait()
        logger.debug("Test MCP server shutdown complete")

@pytest.fixture
async def test_server():
    """Provide test MCP server."""
    async for server in start_test_server():
        yield server

@pytest.fixture
async def mcp_llm_agent():
    """Provide configured MCPLLMAgent."""
    logger.debug("Creating MCPLLMAgent for testing")
    
    # Configure LLM for testing
    llm_config = LLMConfig(
        model="gpt-4",
        api_key="test-key",
        provider_name="openai"
    )
    
    # Configure MCP
    mcp_config = {
        "command": sys.executable,
        "args": [str(Path(__file__).parent / "data" / "test_server.py")],
        "env": None
    }
    
    # Create and initialize agent
    agent = MCPLLMAgent("test_agent", llm_config, mcp_config)
    logger.debug("Connecting MCPLLMAgent to test server")
    await agent.connect()
    logger.debug("MCPLLMAgent connected successfully")
    
    try:
        yield agent
    finally:
        logger.debug("Cleaning up MCPLLMAgent")
        await agent.cleanup()
        logger.debug("MCPLLMAgent cleanup complete")