# tests/test_tools.py
import pytest
from typing import Dict, Any, Optional
from pydantic import BaseModel
from robotape.tools import Tool, RunContext
from robotape.tape import Tape, Step, StepMetadata, StepType

# Test models for tool validation
class SearchParams(BaseModel):
    query: str
    max_results: Optional[int] = 10

class SearchResult(BaseModel):
    results: list[str]
    total_found: int

# Example tool functions for testing
def sync_search_tool(ctx: RunContext[str], query: str, max_results: int = 10) -> Dict[str, Any]:
    """Synchronous search tool for testing."""
    return {
        "results": [f"Result {i} for {query}" for i in range(max_results)],
        "total_found": max_results
    }

async def async_search_tool(ctx: RunContext[str], query: str, max_results: int = 10) -> Dict[str, Any]:
    """Asynchronous search tool for testing."""
    return {
        "results": [f"Async Result {i} for {query}" for i in range(max_results)],
        "total_found": max_results
    }

def test_tool_creation():
    """Test basic tool creation and metadata."""
    tool = Tool(sync_search_tool)
    
    assert tool.name == "sync_search_tool"
    assert "Synchronous search tool" in tool.description
    assert tool.takes_ctx
    assert tool.max_retries == 3  # Default value

def test_tool_schema_generation():
    """Test JSON schema generation for tool parameters."""
    tool = Tool(sync_search_tool)
    
    schema = tool.parameters_json_schema
    assert schema["type"] == "object"
    assert "query" in schema["properties"]
    assert "max_results" in schema["properties"]
    assert "query" in schema["required"]
    assert "max_results" not in schema["required"]

@pytest.mark.asyncio
async def test_sync_tool_execution():
    """Test execution of synchronous tool."""
    tool = Tool(sync_search_tool)
    context = RunContext(
        deps="test",
        usage=0,
        prompt="test search",
        tape=Tape()
    )
    
    result = await tool.execute(
        {"query": "test query", "max_results": 5},
        context
    )
    
    assert len(result["results"]) == 5
    assert result["total_found"] == 5
    assert "test query" in result["results"][0]

@pytest.mark.asyncio
async def test_async_tool_execution():
    """Test execution of asynchronous tool."""
    tool = Tool(async_search_tool)
    context = RunContext(
        deps="test",
        usage=0,
        prompt="test search",
        tape=Tape()
    )
    
    result = await tool.execute(
        {"query": "test query", "max_results": 5},
        context
    )
    
    assert len(result["results"]) == 5
    assert result["total_found"] == 5
    assert "Async Result" in result["results"][0]

@pytest.mark.asyncio
async def test_tool_validation_error():
    """Test tool parameter validation."""
    tool = Tool(sync_search_tool)
    context = RunContext(
        deps="test",
        usage=0,
        prompt="test search",
        tape=Tape()
    )
    
    with pytest.raises(Exception) as exc_info:
        # Missing required 'query' parameter
        await tool.execute({"max_results": 5}, context)
    
    assert "query" in str(exc_info.value)

@pytest.mark.asyncio
async def test_tool_retry_mechanism():
    """Test tool retry mechanism."""
    failing_count = 0
    
    async def failing_tool(ctx: RunContext[str], param: str):
        nonlocal failing_count
        failing_count += 1
        if failing_count < 3:  # Fail twice then succeed
            raise ValueError("Temporary error")
        return {"status": "success"}
    
    tool = Tool(failing_tool, max_retries=3)
    context = RunContext(
        deps="test",
        usage=0,
        prompt="test retry",
        tape=Tape()
    )
    
    result = await tool.execute({"param": "test"}, context)
    assert result["status"] == "success"
    assert failing_count == 3  # Verify it took 3 attempts

@pytest.mark.asyncio
async def test_tool_tape_recording():
    """Test that tool execution is properly recorded in tape."""
    tool = Tool(sync_search_tool)
    tape = Tape()
    context = RunContext(
        deps="test",
        usage=0,
        prompt="test search",
        tape=tape
    )
    
    await tool.execute(
        {"query": "test query"},
        context
    )
    
    # Verify steps were recorded
    assert len(tape.steps) == 1
    step = tape.steps[0]
    assert step.type == StepType.ACTION
    assert "test query" in str(step.content["args"])

@pytest.mark.asyncio
async def test_complex_validation():
    """Test tool with complex parameter validation."""
    async def complex_tool(
        ctx: RunContext[str],
        required_str: str,
        optional_int: Optional[int] = None,
        nested_dict: Optional[Dict[str, Any]] = None
    ):
        return {
            "required_str": required_str,
            "optional_int": optional_int,
            "nested_dict": nested_dict
        }
    
    tool = Tool(complex_tool)
    context = RunContext(
        deps="test",
        usage=0,
        prompt="test complex",
        tape=Tape()
    )
    
    # Test with minimal parameters
    result = await tool.execute(
        {"required_str": "test"},
        context
    )
    assert result["required_str"] == "test"
    assert result["optional_int"] is None
    
    # Test with all parameters
    result = await tool.execute(
        {
            "required_str": "test",
            "optional_int": 42,
            "nested_dict": {"key": "value"}
        },
        context
    )
    assert result["optional_int"] == 42
    assert result["nested_dict"]["key"] == "value"

@pytest.mark.asyncio
async def test_tool_error_recording():
    """Test that tool errors are properly recorded."""
    async def error_tool(ctx: RunContext[str]):
        raise ValueError("Expected error")
    
    tool = Tool(error_tool, max_retries=1)
    tape = Tape()
    context = RunContext(
        deps="test",
        usage=0,
        prompt="test error",
        tape=tape
    )
    
    with pytest.raises(ValueError):
        await tool.execute({}, context)
    
    # Verify error was recorded
    thought_steps = tape.get_steps_by_type(StepType.THOUGHT)
    assert len(thought_steps) == 1
    assert "Expected error" in thought_steps[0].content