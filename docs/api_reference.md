# API Reference

This section provides detailed documentation for the major classes and functions in the Lightweight Agent Framework. Each entry includes:
- A brief description of the class or function.
- Key methods and properties.
- Example usage.

---

## **Base Classes**

### **BaseAgent**

The foundation for all agents. Defines the core lifecycle of an agent: **think**, **act**, and **observe**.

#### **Methods**

| Method                     | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `async think(context)`      | Generates a thought step based on the context.                              |
| `async act(thought)`        | Executes an action based on a thought.                                      |
| `async observe(action)`     | Processes an observation after an action.                                   |
| `async execute_step(step)`  | Executes a step (thought, action, or observation).                          |

#### **Example**

```python
from robotape.agents import BaseAgent
from robotape.models.steps import StepResult, Step

class MyCustomAgent(BaseAgent):
    async def think(self, context: Dict[str, Any]) -> StepResult:
        return StepResult(success=True, output="I have thought about it")
    
    async def act(self, thought: Step) -> StepResult:
        return StepResult(success=True, output={"action": "process"})
    
    async def observe(self, action: Step) -> StepResult:
        return StepResult(success=True, output="I observed the results")
```

---

### **BaseLLM**

The base class for LLM integrations. Provides methods for generating text and cleaning up resources.

#### **Methods**

| Method                     | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `async generate(prompt)`    | Generates text from a prompt.                                               |
| `async close()`             | Cleans up resources (e.g., closes connections).                             |

#### **Example**

```python
from robotape.llm import BaseLLM, LLMConfig, LLMResponse

class CustomLLM(BaseLLM):
    async def generate(self, prompt: str) -> LLMResponse:
        return LLMResponse(text="Generated text", raw_response={}, usage={}, model="custom")
    
    async def close(self):
        pass
```

---

## **Built-in Agents**

### **SimpleAgent**

A basic implementation of `BaseAgent` with a straightforward think-act-observe cycle.

#### **Methods**

| Method                     | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `async think(context)`      | Generates a thought step based on the context.                              |
| `async act(thought)`        | Executes an action based on a thought.                                      |
| `async observe(action)`     | Processes an observation after an action.                                   |

#### **Example**

```python
from robotape.agents import SimpleAgent
from robotape.tape import Tape, Step, StepMetadata, StepType

agent = SimpleAgent("my_agent")
tape = Tape()
tape.append(Step(
    type=StepType.THOUGHT,
    content="I should process the input data",
    metadata=StepMetadata(agent="my_agent", node="planning")
))

async def run_agent():
    result = await agent.execute_step(tape.get_last_step())
    print(f"Agent result: {result.output}")

import asyncio
asyncio.run(run_agent())
```

---

### **LLMAwareAgent**

An agent that integrates with Large Language Models (LLMs). Uses `LLMConfig` to configure the LLM.

#### **Methods**

| Method                     | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `async think(context)`      | Generates a thought step using the LLM.                                     |
| `async act(thought)`        | Executes an action based on a thought.                                      |
| `async observe(action)`     | Processes an observation after an action.                                   |
| `_create_thinking_prompt(context)` | Creates a prompt for the LLM based on the context.                   |

#### **Example**

```python
from robotape.agents.llm import LLMAwareAgent
from robotape.llm import LLMConfig

llm_config = LLMConfig(
    model="gpt-4",
    api_key="your-api-key",
    provider_name="openai"
)

agent = LLMAwareAgent("llm_agent", llm_config)

async def run_llm_agent():
    context = {"task": "Write a summary of the meeting"}
    result = await agent.think(context)
    print(f"LLM Response: {result.output}")

import asyncio
asyncio.run(run_llm_agent())
```

---

## **Tool System**

### **Tool**

A reusable function that agents can use to extend their capabilities.

#### **Methods**

| Method                     | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `async execute(args, context)` | Executes the tool with validated inputs.                                |
| `function_schema(function)` | Generates a JSON schema for the tool's inputs.                              |

#### **Example**

```python
from robotape.tools import Tool, RunContext

async def search_tool(ctx: RunContext[str], query: str) -> Dict[str, Any]:
    return {"results": [f"Result for {query}"]}

tool = Tool(search_tool, max_retries=3)

context = RunContext(
    deps="search_dependencies",
    usage=0,
    prompt="search query",
    tape=Tape()
)

result = await tool.execute({"query": "python programming"}, context)
print(result)
```

---

### **RunContext**

Contextual information for tool execution.

#### **Properties**

| Property                   | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `deps`                     | Dependencies required for the tool.                                         |
| `usage`                    | Simplified usage tracking.                                                  |
| `prompt`                   | The prompt or input that triggered the tool execution.                      |
| `tape`                     | The agent's tape for recording execution history.                           |
| `tool_name`                | The name of the tool.                                                       |
| `retry`                    | The current retry attempt.                                                  |

---

## **Tape System**

### **Tape**

A sequential record of steps.

#### **Methods**

| Method                     | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `append(step)`             | Adds a step to the tape.                                                    |
| `get_steps_by_type(type)`  | Returns all steps of a specific type.                                       |
| `get_steps_by_agent(agent)`| Returns all steps by a specific agent.                                      |
| `get_last_step()`          | Returns the last step in the tape.                                          |
| `clone()`                  | Creates a new tape with a reference to the parent tape.                     |

#### **Example**

```python
from robotape.tape import Tape, Step, StepMetadata, StepType

tape = Tape()
tape.append(Step(
    type=StepType.THOUGHT,
    content="I should search for information",
    metadata=StepMetadata(agent="my_agent", node="planning")
))

thoughts = tape.get_steps_by_type(StepType.THOUGHT)
print(thoughts)
```

---

### **Step**

An individual record within a tape.

#### **Properties**

| Property                   | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `type`                     | The type of step (e.g., THOUGHT, ACTION, OBSERVATION).                      |
| `content`                  | The data associated with the step.                                          |
| `metadata`                 | Additional information about the step (e.g., agent, node).                  |

---

## **Storage System**

### **TapeStore**

A built-in storage system for persisting tapes.

#### **Methods**

| Method                     | Description                                                                 |
|----------------------------|-----------------------------------------------------------------------------|
| `save_tape(tape)`          | Saves a tape to the storage backend.                                        |
| `load_tape(tape_id)`       | Loads a tape from the storage backend.                                      |
| `get_tape_history(tape_id)`| Returns the history of a tape (e.g., parent-child relationships).           |
| `search_tapes(**filters)`  | Searches tapes based on filters (e.g., agent, node, tags).                  |

#### **Example**

```python
from robotape.storage import TapeStore

store = TapeStore("sqlite:///tapes.db")
tape_id = store.save_tape(tape)
loaded_tape = store.load_tape(tape_id)
```

---

## **Next Steps**

Now that you’ve explored the **API Reference**, here are some next steps:
- Dive into **Examples and Tutorials** for end-to-end workflows.
- Explore **Advanced Patterns** for error handling, concurrency, and performance optimization.
- Learn about **Testing and Debugging** to ensure your agents and tools work as expected.