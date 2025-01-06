# Getting Started with Lightweight Agent Framework

This guide will help you get up and running with the Lightweight Agent Framework (LAF).

## Installation

### Basic Installation

For basic usage, install using pip:

```bash
pip install robotape
```

### Development Installation

For development or to access additional tools:

```bash
pip install robotape[dev]
```

## Core Concepts

Before diving into code, let's understand the key concepts:

1. **Agents**: Autonomous entities that can think, act, and observe
2. **Tapes**: Record of an agent's execution history
3. **Steps**: Individual actions or thoughts within a tape
4. **Tools**: Reusable functions that agents can utilize
5. **MCP (Model Control Protocol)**: A protocol for integrating external tools and services via an MCP server

## Your First Agent

Let's create a simple agent that processes some text:

```python
from robotape.agents import SimpleAgent
from robotape.tape import Tape, Step, StepMetadata, StepType

# Create an agent
agent = SimpleAgent("text_processor")

# Create a tape to record the agent's actions
tape = Tape()

# Add an initial thought
initial_thought = Step(
    type=StepType.THOUGHT,
    content="I should process the input text",
    metadata=StepMetadata(
        agent="text_processor",
        node="planning"
    )
)
tape.append(initial_thought)

# Execute the agent asynchronously
async def process_text():
    result = await agent.execute_step(tape.get_last_step())
    print(f"Agent result: {result.output}")

# Run in an async context
import asyncio
asyncio.run(process_text())
```

---

## Using MCPLLMAgent

The `MCPLLMAgent` is a specialized agent that combines the capabilities of LLMs with the **Model Control Protocol (MCP)**. It allows agents to interact with external tools and services through an MCP server, enabling more complex workflows and integrations.

### Setting Up the MCP Server

Before using the `MCPLLMAgent`, you need to set up an MCP server. The server should expose tools that the agent can use, such as `get_data` and `process_data`.

Here’s an example of a simple MCP server:

```python
# test_server.py
from mirascope.mcp import MCPServer

app = MCPServer("test-server")

@app.tool()
async def get_data(query: str) -> dict:
    """Get test data based on query."""
    return {
        "result": f"Test result for {query}",
        "timestamp": "2024-01-05T12:00:00Z"
    }

@app.tool()
async def process_data(data: dict) -> dict:
    """Process provided data."""
    return {
        "processed": data,
        "status": "success"
    }

if __name__ == "__main__":
    import asyncio
    asyncio.run(app.run())
```

Run the server using:

```bash
python test_server.py
```

### Using MCPLLMAgent

Once the MCP server is running, you can create and use the `MCPLLMAgent`:

```python
from robotape.agents.mcpllm import MCPLLMAgent
from robotape.llm import LLMConfig

# Configure the LLM
llm_config = LLMConfig(
    model="gpt-4",
    api_key="your-api-key",
    provider_name="openai"
)

# Configure the MCP server
mcp_config = {
    "command": "python",
    "args": ["path/to/test_server.py"],
    "env": {"ENV_VAR": "value"}
}

# Create an MCPLLMAgent
agent = MCPLLMAgent("mcp_agent", llm_config, mcp_config)

# Connect to the MCP server
await agent.connect()

# Execute a full think-act-observe cycle
context = {"task": "Analyze test data"}
thought_result = await agent.think(context)
action_result = await agent.act(thought_result)
observe_result = await agent.observe(action_result)
```

### Available Tools

The `MCPLLMAgent` comes with a set of predefined tools that can be extended:

- **get_data**: Retrieves data from the system based on a query.
- **process_data**: Processes data using predefined logic.

You can extend the available tools by modifying the `available_tools` dictionary in the `MCPLLMAgent` class.

---

## Creating Custom Agents

Extend the `BaseAgent` class to create your own agent:

```python
from robotape.agents import BaseAgent
from robotape.models.steps import StepResult

class MyCustomAgent(BaseAgent):
    async def think(self, context):
        # Implement thinking logic
        return StepResult(
            success=True,
            output="I have thought about it"
        )
    
    async def act(self, thought):
        # Implement action logic
        return StepResult(
            success=True,
            output={"action": "completed"}
        )
    
    async def observe(self, action):
        # Implement observation logic
        return StepResult(
            success=True,
            output="I observed the results"
        )
```

---

## Using Tools

Tools extend an agent's capabilities:

```python
from robotape.tools import Tool, RunContext

# Define a tool function
async def search_tool(ctx: RunContext[str], query: str):
    # Implement search logic
    return {"results": [f"Result for {query}"]}

# Create and use the tool
tool = Tool(search_tool, max_retries=3)

# Use in an agent
context = RunContext(
    deps="search_dependencies",
    usage=0,
    prompt="search query",
    tape=Tape()
)

result = await tool.execute(
    {"query": "python programming"},
    context
)
```

---

## Working with Tapes

Tapes record agent execution history:

```python
from robotape.tape import Tape

# Create a tape
tape = Tape()

# Add steps
tape.append(Step(
    type=StepType.THOUGHT,
    content="Initial thought",
    metadata=StepMetadata(agent="my_agent", node="planning")
))

# Get steps by type
thoughts = tape.get_steps_by_type(StepType.THOUGHT)

# Clone a tape for branching
new_tape = tape.clone()
```

---

## Storing Execution History

Use the built-in storage system:

```python
from robotape.storage import TapeStore

# Initialize storage
store = TapeStore("sqlite:///agents.db")

# Save a tape
tape_id = store.save_tape(tape)

# Load a tape
loaded_tape = store.load_tape(tape_id)

# Search tapes
results = store.search_tapes(agent="my_agent")
```

---

## Next Steps

- Explore the [Tape System](tape_system.md) documentation for advanced tape operations
- Learn about different agent types in the [Agents](agents.md) guide
- Check out example implementations in the `examples` directory
- Review the test suite for more usage patterns

---

## Common Issues and Solutions

1. **Async/Await Usage**
   - Always use `async/await` with agent methods
   - Run async code in an event loop

2. **Tool Development**
   - Always validate input parameters
   - Handle errors gracefully
   - Use retry mechanisms for unreliable operations

3. **Storage Management**
   - Regularly clean up old tapes
   - Use tags for better organization
   - Consider implementing tape archival for long-term storage
