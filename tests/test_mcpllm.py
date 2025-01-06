"""Tests for MCPLLMAgent."""

import pytest
import logging
import json  # Import json for parsing the JSON string
from unittest.mock import patch, AsyncMock
from robotape.tape import Tape, Step, StepType, StepMetadata
from robotape.llm import LLMConfig, LLMResponse
from robotape.models.steps import StepResult

# Configure test logger
logger = logging.getLogger(__name__)

@pytest.fixture
def mock_openai_llm():
    """Mock the OpenAI LLM to avoid real API calls."""
    with patch("robotape.llm.providers.openai.OpenAILLM.generate", new_callable=AsyncMock) as mock_generate:
        # Mock the LLMResponse with all required fields, including raw_response
        mock_generate.return_value = LLMResponse(
            text='{"tool_name": "get_data", "parameters": {"query": "test"}, "reasoning": "Test reasoning"}',
            model="gpt-4",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
            raw_response={"mock": "response"}  # Add the required raw_response field
        )
        yield mock_generate

@pytest.mark.asyncio
async def test_mcpllm_agent_initialization(mcp_llm_agent, mock_openai_llm):
    """Test agent initialization and tool discovery."""
    logger.debug("Starting agent initialization test")
    async for agent in mcp_llm_agent:
        assert len(agent.available_tools) > 0
        assert "get_data" in agent.available_tools
        assert "process_data" in agent.available_tools

@pytest.mark.asyncio
async def test_mcpllm_agent_think(mcp_llm_agent, mock_openai_llm):
    """Test agent thinking process."""
    context = {"task": "analyze test data", "query": "test query"}
    async for agent in mcp_llm_agent:
        result = await agent.think(context)
        assert result.success
        assert isinstance(result.output, str)
        assert "tool_name" in result.output.lower()

@pytest.mark.asyncio
async def test_mcpllm_agent_act(mcp_llm_agent, mock_openai_llm):
    """Test agent action execution."""
    # Parse the JSON string into a dictionary for thought.content
    thought_content = json.loads('{"tool_name": "get_data", "parameters": {"query": "test"}, "reasoning": "Test execution"}')
    thought = Step(
        type=StepType.THOUGHT,
        content=thought_content,  # Pass the dictionary, not the JSON string
        metadata=StepMetadata(agent="test_agent", node="test")
    )
    async for agent in mcp_llm_agent:
        result = await agent.act(thought)
        assert result.success
        assert isinstance(result.output, dict)
        assert "result" in result.output

@pytest.mark.asyncio
async def test_mcpllm_full_cycle(mcp_llm_agent, mock_openai_llm):
    """Test complete agent execution cycle."""
    tape = Tape()
    async for agent in mcp_llm_agent:
        agent.current_tape = tape
        
        # Execute full cycle
        context = {"task": "analyze test data"}
        
        # Think
        thought_result = await agent.think(context)
        assert thought_result.success
        
        # Parse the JSON string into a dictionary for thought.content
        thought_content = json.loads(thought_result.output)
        thought_step = Step(
            type=StepType.THOUGHT,
            content=thought_content,  # Pass the dictionary, not the JSON string
            metadata=StepMetadata(agent=agent.name, node="think")
        )
        tape.append(thought_step)
        
        # Act
        action_result = await agent.act(thought_step)
        assert action_result.success
        action_step = Step(
            type=StepType.ACTION,
            content=action_result.output,
            metadata=StepMetadata(agent=agent.name, node="act")
        )
        tape.append(action_step)
        
        # Observe
        observe_result = await agent.observe(action_step)
        assert observe_result.success
        observation_step = Step(
            type=StepType.OBSERVATION,
            content=observe_result.output,
            metadata=StepMetadata(agent=agent.name, node="observe")
        )
        tape.append(observation_step)
        
        # Verify tape
        assert len(tape.steps) == 3