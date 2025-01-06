# Agents Documentation

This guide covers the agent system in the Lightweight Agent Framework, including agent types, implementation patterns, and best practices.

## Agent Architecture

Agents in the framework follow a three-phase execution cycle:

1. **Think**: Generate plans and decisions
2. **Act**: Execute actions based on thoughts
3. **Observe**: Process and analyze results

## Base Agent

All agents inherit from the `BaseAgent` class:

```python
from robotape.agents import BaseAgent
from robotape.models.steps import StepResult

class BaseAgent(ABC):
    async def think(self, context: Dict[str, Any]) -> StepResult:
        """Generate a thought step."""
        pass

    async def act(self, thought: Step) -> StepResult:
        """Generate an action based on a thought."""
        pass

    async def observe(self, action: Step) -> StepResult:
        """Process an observation after an action."""
        pass
```

## Built-in Agents

### SimpleAgent

The framework includes a `SimpleAgent` implementation:

```python
from robotape.agents import SimpleAgent

agent = SimpleAgent("my_agent")
```

Key features:
- Basic think-act-observe cycle
- Error handling
- Tape integration
- Tool support

### LLM-Aware Agents

The framework provides built-in support for LLM (Large Language Model) agents, which can interact with various LLM providers such as OpenAI, Anthropic, and HuggingFace. These agents are designed to integrate seamlessly with the LLM capabilities provided by the framework.

#### LLMAwareAgent

The `LLMAwareAgent` is a specialized agent that leverages LLMs for decision-making and text generation. It uses the `LLMConfig` class to configure the LLM provider and model.

```python
from robotape.agents.llm import LLMAwareAgent
from robotape.llm import LLMConfig

# Configure the LLM
llm_config = LLMConfig(
    model="gpt-4",
    api_key="your-api-key",
    provider_name="openai"
)

# Create an LLM-aware agent
agent = LLMAwareAgent("llm_agent", llm_config)
```

Key features:
- **LLM Integration**: Supports multiple LLM providers (OpenAI, Anthropic, HuggingFace).
- **Prompt Management**: Automatically generates prompts for the LLM based on the context.
- **Usage Tracking**: Tracks token usage and other metrics from the LLM response.

#### Example Usage

```python
# Example of using LLMAwareAgent
async def run_llm_agent():
    llm_config = LLMConfig(
        model="gpt-4",
        api_key="your-api-key",
        provider_name="openai"
    )
    
    agent = LLMAwareAgent("llm_agent", llm_config)
    
    # Generate a thought using the LLM
    context = {"task": "Write a summary of the meeting"}
    result = await agent.think(context)
    
    if result.success:
        print(f"LLM Response: {result.output}")
    else:
        print(f"Error: {result.error}")

# Run the agent
import asyncio
asyncio.run(run_llm_agent())
```

#### Supported LLM Providers

The `LLMAwareAgent` supports the following LLM providers:

- **OpenAI**: Use `provider_name="openai"` and specify the model (e.g., `gpt-4`).
- **Anthropic**: Use `provider_name="anthropic"` and specify the model (e.g., `claude-3-sonnet-20240229`).
- **HuggingFace**: Use `provider_name="huggingface"` and specify the model (e.g., `meta-llama/Llama-2-70b-chat-hf`).

#### Customizing LLM Behavior

You can customize the behavior of the LLM by passing additional parameters to the `LLMConfig`:

```python
llm_config = LLMConfig(
    model="gpt-4",
    api_key="your-api-key",
    provider_name="openai",
    temperature=0.5,  # Control creativity
    max_tokens=100,   # Limit response length
    additional_params={
        "presence_penalty": 0.5  # Additional provider-specific parameters
    }
)
```

---

### MCPLLMAgent

The `MCPLLMAgent` is a specialized agent that combines the capabilities of LLMs with the **Model Control Protocol (MCP)**. It allows agents to interact with external tools and services through an MCP server, enabling more complex workflows and integrations.

#### Key Features:
- **MCP Integration**: Connects to an MCP server to execute tools and services.
- **Tool Management**: Provides a set of predefined tools (e.g., `get_data`, `process_data`) that can be extended.
- **LLM + MCP Synergy**: Uses LLMs to generate thoughts and MCP to execute actions.

#### Example Usage

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
    "args": ["path/to/mcp_server.py"],
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

#### Available Tools

The `MCPLLMAgent` comes with a set of predefined tools that can be extended:

- **get_data**: Retrieves data from the system based on a query.
- **process_data**: Processes data using predefined logic.

You can extend the available tools by modifying the `available_tools` dictionary in the `MCPLLMAgent` class.

#### Example of Extending Tools

```python
class CustomMCPLLMAgent(MCPLLMAgent):
    def __init__(self, name: str, llm_config: LLMConfig, mcp_config: Dict[str, Any]):
        super().__init__(name, llm_config, mcp_config)
        
        # Add a custom tool
        self.available_tools["custom_tool"] = {
            "description": "A custom tool for specific tasks",
            "args": {"param1": "string", "param2": "int"}
        }

    async def act(self, thought: Step) -> StepResult:
        # Override the act method to handle custom tools
        if thought.content.get("tool_name") == "custom_tool":
            # Implement custom tool logic
            return StepResult(
                success=True,
                output={"result": "Custom tool executed successfully"}
            )
        else:
            # Fall back to the default implementation
            return await super().act(thought)
```

---

### Creating Custom Agents

#### Basic Custom Agent

```python
from robotape.agents import BaseAgent
from robotape.models.steps import StepResult

class MyCustomAgent(BaseAgent):
    async def think(self, context):
        # Analyze context and plan next action
        return StepResult(
            success=True,
            output="I should process the data",
            metadata={"context_keys": list(context.keys())}
        )
    
    async def act(self, thought):
        # Execute planned action
        return StepResult(
            success=True,
            output={"action": "process", "data": thought.content},
            metadata={"thought_id": thought.metadata.id}
        )
    
    async def observe(self, action):
        # Analyze action results
        return StepResult(
            success=True,
            output="Action completed successfully",
            metadata={"action_id": action.metadata.id}
        )
```

---

### Error Handling

Implement robust error handling in agents:

```python
class RobustAgent(BaseAgent):
    async def execute_step(self, step: Step) -> StepResult:
        try:
            # Normal execution
            return await super().execute_step(step)
        except Exception as e:
            # Log error
            logger.error(f"Error executing step: {str(e)}")
            
            # Create error result
            return StepResult(
                success=False,
                error=str(e),
                metadata={
                    "error_type": type(e).__name__,
                    "step_type": step.type
                }
            )
```

---

### Advanced Patterns

#### Composable Agents

Create agents that can work together:

```python
class ComposableAgent(BaseAgent):
    def __init__(self, name: str, sub_agents: List[BaseAgent]):
        super().__init__(name)
        self.sub_agents = sub_agents
    
    async def think(self, context):
        # Collect thoughts from all sub-agents
        thoughts = []
        for agent in self.sub_agents:
            result = await agent.think(context)
            if result.success:
                thoughts.append(result.output)
        
        # Combine thoughts
        return StepResult(
            success=True,
            output={"combined_thoughts": thoughts}
        )
```

---

### Best Practices

1. **Agent Design**
   - Keep agents focused on specific tasks
   - Implement proper error handling
   - Use meaningful metadata
   - Document agent behavior

2. **State Management**
   - Use clear state interfaces
   - Handle state persistence
   - Clean up state when appropriate

3. **Tool Integration**
   - Validate tool inputs
   - Handle tool errors gracefully
   - Record tool usage in tape

4. **Testing**
   ```python
   import pytest
   
   async def test_custom_agent():
       agent = MyCustomAgent("test_agent")
       
       # Test thinking
       result = await agent.think({"test": "data"})
       assert result.success
       
       # Test action
       thought_step = Step(
           type=StepType.THOUGHT,
           content="test thought",
           metadata=StepMetadata(agent="test", node="test")
       )
       result = await agent.act(thought_step)
       assert result.success
   ```
