# Tool System

The **Tool System** allows agents to extend their capabilities by using reusable functions. Tools can perform a wide range of tasks, from simple calculations to complex API calls. This section covers:

1. **Tool Class**: The foundation for creating tools.
2. **RunContext**: Contextual information for tool execution.
3. **Creating Custom Tools**: How to define and use custom tools.
4. **LLMTool**: A tool for interacting with LLMs.
5. **Tool Validation and Error Handling**: Best practices for robust tool execution.

---

## **Tool Class**

The `Tool` class is the foundation for creating tools. It provides methods for executing tools, validating inputs, and handling errors.

### **Key Features**
- **Input Validation**: Automatically validates inputs using Pydantic models.
- **Retry Mechanism**: Supports retries for unreliable operations (default: `3` retries).
- **Execution Logging**: Records tool execution in the agent's tape.

### **Example**

```python
from robotape.tools import Tool, RunContext
from robotape.tape import Step, StepMetadata, StepType

# Define a tool function
async def search_tool(ctx: RunContext[str], query: str) -> Dict[str, Any]:
    """Perform a search and return results."""
    return {"results": [f"Result for {query}"]}

# Create a tool
tool = Tool(search_tool, max_retries=3)

# Use the tool in an agent
context = RunContext(
    deps="search_dependencies",
    usage=0,
    prompt="search query",
    tape=Tape()
)

# Execute the tool
result = await tool.execute({"query": "python programming"}, context)
print(result)
```

---

## **RunContext**

The `RunContext` class provides contextual information for tool execution, such as dependencies, usage tracking, and the agent's tape.

### **Parameters**

| Parameter     | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| `deps`        | Dependencies required for the tool (e.g., API clients, databases).          |
| `usage`       | Simplified usage tracking (e.g., API call count).                           |
| `prompt`      | The prompt or input that triggered the tool execution.                      |
| `tape`        | The agent's tape for recording execution history.                           |
| `tool_name`   | The name of the tool (optional).                                            |
| `retry`       | The current retry attempt (default: `0`).                                   |

---

## **Creating Custom Tools**

You can create custom tools by defining a function and wrapping it in the `Tool` class.

### **Example: Custom Tool**

```python
from typing import Dict, Any
from robotape.tools import Tool, RunContext

# Define a custom tool function
async def calculate_tool(ctx: RunContext[str], a: float, b: float) -> Dict[str, Any]:
    """Perform a calculation."""
    return {"sum": a + b, "product": a * b}

# Create a tool
calculate_tool = Tool(calculate_tool)

# Use the tool
context = RunContext(
    deps="math_dependencies",
    usage=0,
    prompt="calculate 2 + 3",
    tape=Tape()
)

# Execute the tool
result = await calculate_tool.execute({"a": 2, "b": 3}, context)
print(result)  # Output: {"sum": 5, "product": 6}
```

---

## **LLMTool**

The `LLMTool` is a specialized tool for interacting with **Large Language Models (LLMs)**. It uses an instance of `BaseLLM` to generate text based on a given prompt. The `LLMTool` is particularly useful for agents that need to leverage LLMs for tasks like text generation, summarization, or question answering.

### **Key Features**
- **LLM Integration**: Works with any LLM that implements the `BaseLLM` interface.
- **Prompt-Based Execution**: Takes a prompt as input and returns the generated text.
- **Retry Mechanism**: Supports retries for unreliable LLM operations (default: `3` retries).

### **Example**

```python
from robotape.tools import LLMTool
from robotape.llm import BaseLLM

# Define a mock LLM for demonstration
class MockLLM(BaseLLM):
    async def generate(self, prompt: str) -> str:
        return f"Generated text for: {prompt}"

# Create an LLMTool with the mock LLM
llm = MockLLM()
llm_tool = LLMTool(llm)

# Use the tool
context = RunContext(
    deps="llm_dependencies",
    usage=0,
    prompt="generate text",
    tape=Tape()
)

# Execute the tool
result = await llm_tool.execute({"prompt": "Write a poem about the sea"}, context)
print(result)  # Output: "Generated text for: Write a poem about the sea"
```

### **Parameters**

| Parameter     | Description                                                                 |
|---------------|-----------------------------------------------------------------------------|
| `llm`         | An instance of `BaseLLM` used for text generation.                          |
| `max_retries` | The maximum number of retries for LLM operations (default: `3`).            |

---

## **Tool Validation and Error Handling**

### **Input Validation**

The `Tool` class automatically validates inputs using Pydantic models. If the inputs don’t match the expected schema, a validation error is raised.

### **Error Handling**

The `Tool` class supports retries for unreliable operations. If a tool fails, it will retry up to the specified `max_retries` (default: `3`) before raising an error.

#### **Example**

```python
from robotape.tools import Tool, RunContext

# Define a tool with retries
async def unreliable_tool(ctx: RunContext[str]) -> str:
    """A tool that fails 50% of the time."""
    import random
    if random.random() < 0.5:
        raise ValueError("Tool failed!")
    return "Success"

# Create a tool with max_retries=3
tool = Tool(unreliable_tool, max_retries=3)

# Use the tool
context = RunContext(
    deps="dependencies",
    usage=0,
    prompt="unreliable operation",
    tape=Tape()
)

# Execute the tool
try:
    result = await tool.execute({}, context)
    print(result)
except Exception as e:
    print(f"Tool failed after retries: {e}")
```

---

## **Next Steps**

Now that you’ve learned about the **Tool System**, here are some next steps:
- Explore the **Tape System** to record and analyze agent execution history.
- Learn about **MCP (Multi-Component Processing)** for building complex workflows.
- Dive into **Advanced Patterns** for error handling, concurrency, and performance optimization.