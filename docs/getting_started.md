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

## Next Steps

- Explore the [Tape System](tape_system.md) documentation for advanced tape operations
- Learn about different agent types in the [Agents](agents.md) guide
- Check out example implementations in the `examples` directory
- Review the test suite for more usage patterns

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