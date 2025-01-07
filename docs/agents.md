# Agent System

The **Agent System** is the core of the Lightweight Agent Framework. Agents are autonomous entities that follow a **think-act-observe** cycle, enabling them to perform tasks, make decisions, and learn from their actions. This section covers the following topics:

1. **BaseAgent**: The foundation of all agents.
2. **Built-in Agents**: `SimpleAgent` and `LLMAwareAgent`.
3. **Custom Agents**: How to extend `BaseAgent` and built-in agents.
4. **Composable and Stateful Agents**: Advanced patterns for building complex agents.

---

## **BaseAgent**

All agents in the framework inherit from the `BaseAgent` class. This class defines the core lifecycle of an agent:

1. **Think**: Generate plans and decisions.
2. **Act**: Execute actions based on thoughts.
3. **Observe**: Process and analyze results.

Here’s the basic structure of `BaseAgent`:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
from robotape.models.steps import StepResult, Step

class BaseAgent(ABC):
    @abstractmethod
    async def think(self, context: Dict[str, Any]) -> StepResult:
        """Generate a thought step."""
        pass

    @abstractmethod
    async def act(self, thought: Step) -> StepResult:
        """Generate an action based on a thought."""
        pass

    @abstractmethod
    async def observe(self, action: Step) -> StepResult:
        """Process an observation after an action."""
        pass
```

---

## **Built-in Agents**

The framework provides two built-in agents:

1. **SimpleAgent**: A basic agent with a straightforward think-act-observe cycle.
2. **LLMAwareAgent**: An agent that integrates with Large Language Models (LLMs) for advanced decision-making.

---

### **SimpleAgent**

The `SimpleAgent` is a basic implementation of `BaseAgent`. It provides a simple think-act-observe cycle and is ideal for straightforward tasks.

#### **Example Usage**

```python
from robotape.agents import SimpleAgent
from robotape.tape import Tape, Step, StepMetadata, StepType

# Create a SimpleAgent
agent = SimpleAgent("my_agent")

# Create a tape and add a thought step
tape = Tape()
thought_step = Step(
    type=StepType.THOUGHT,
    content="I should process the input data",
    metadata=StepMetadata(agent="my_agent", node="planning")
)
tape.append(thought_step)

# Execute the agent
async def run_agent():
    result = await agent.execute_step(tape.get_last_step())
    print(f"Agent result: {result.output}")

# Run the agent
import asyncio
asyncio.run(run_agent())
```

---

### **LLMAwareAgent**

The `LLMAwareAgent` extends `BaseAgent` to integrate with LLMs. It uses the `LLMConfig` class to configure the LLM provider and model.

#### **Example Usage**

```python
from robotape.agents.llm import LLMAwareAgent
from robotape.llm import LLMConfig

# Configure the LLM
llm_config = LLMConfig(
    model="gpt-4",
    api_key="your-api-key",
    provider_name="openai"
)

# Create an LLMAwareAgent
agent = LLMAwareAgent("llm_agent", llm_config)

# Execute the agent
async def run_llm_agent():
    context = {"task": "Write a summary of the meeting"}
    result = await agent.think(context)
    print(f"LLM Response: {result.output}")

# Run the agent
import asyncio
asyncio.run(run_llm_agent())
```

---

## **Custom Agents**

You can extend **any of the provided agents** (`BaseAgent`, `SimpleAgent`, or `LLMAwareAgent`) to create custom agents tailored to your needs.

---

### **Extending BaseAgent**

When extending `BaseAgent`, you define your own `think`, `act`, and `observe` methods.

#### **Example**

```python
from typing import Dict, Any
from robotape.agents import BaseAgent
from robotape.models.steps import StepResult, Step

class MyCustomAgent(BaseAgent):
    async def think(self, context: Dict[str, Any]) -> StepResult:
        """Custom thinking logic."""
        return StepResult(
            success=True,
            output="I have thought about it",
            metadata={"context_keys": list(context.keys())}
        )
    
    async def act(self, thought: Step) -> StepResult:
        """Custom action logic."""
        return StepResult(
            success=True,
            output={"action": "process", "data": thought.content},
            metadata={"thought_id": thought.metadata.id}
        )
    
    async def observe(self, action: Step) -> StepResult:
        """Custom observation logic."""
        return StepResult(
            success=True,
            output="I observed the results",
            metadata={"action_id": action.metadata.id}
        )
```

---

### **Extending SimpleAgent**

When extending `SimpleAgent`, you can add custom logic while retaining the simplicity of the think-act-observe cycle.

#### **Example**

```python
from typing import Dict, Any
from robotape.agents import SimpleAgent
from robotape.models.steps import StepResult, Step

class EnhancedSimpleAgent(SimpleAgent):
    async def think(self, context: Dict[str, Any]) -> StepResult:
        """Add custom logic before or after the default thinking behavior."""
        print("Custom thinking logic")
        result = await super().think(context)
        return StepResult(
            success=result.success,
            output=f"Enhanced: {result.output}",
            metadata=result.metadata
        )
    
    async def act(self, thought: Step) -> StepResult:
        """Add custom logic before or after the default action behavior."""
        print("Custom action logic")
        result = await super().act(thought)
        return StepResult(
            success=result.success,
            output=f"Enhanced: {result.output}",
            metadata=result.metadata
        )
```

---

### **Extending LLMAwareAgent**

When extending `LLMAwareAgent`, you can customize LLM behavior or add additional functionality.

#### **Example**

```python
from typing import Dict, Any
from robotape.agents.llm import LLMAwareAgent
from robotape.models.steps import StepResult

class CustomPromptLLMAgent(LLMAwareAgent):
    def _create_thinking_prompt(self, context: Dict[str, Any]) -> str:
        """Override the default prompt creation logic."""
        return f"Custom prompt based on context: {context}"
    
    async def think(self, context: Dict[str, Any]) -> StepResult:
        """Use the custom prompt logic."""
        result = await super().think(context)
        return StepResult(
            success=result.success,
            output=f"Custom Prompt Result: {result.output}",
            metadata=result.metadata
        )
```

---

## **Composable and Stateful Agents**

### **Composable Agents**

Composable agents allow you to combine multiple agents into a single workflow. This is useful for complex tasks that require collaboration between agents.

#### **Example**

```python
from typing import List
from robotape.agents import BaseAgent
from robotape.models.steps import StepResult

class ComposableAgent(BaseAgent):
    def __init__(self, name: str, sub_agents: List[BaseAgent]):
        super().__init__(name)
        self.sub_agents = sub_agents
    
    async def think(self, context: Dict[str, Any]) -> StepResult:
        """Collect thoughts from all sub-agents."""
        thoughts = []
        for agent in self.sub_agents:
            result = await agent.think(context)
            if result.success:
                thoughts.append(result.output)
        
        return StepResult(
            success=True,
            output={"combined_thoughts": thoughts}
        )
```

---

### **Stateful Agents**

Stateful agents maintain state across executions, allowing them to remember previous actions and results.

#### **Example**

```python
from robotape.agents import BaseAgent
from robotape.models.steps import StepResult

class StatefulAgent(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name)
        self.state = {}
    
    async def think(self, context: Dict[str, Any]) -> StepResult:
        """Access and update state."""
        previous_results = self.state.get("results", [])
        self.state["last_context"] = context
        
        return StepResult(
            success=True,
            output=f"Processed {len(previous_results)} previous results"
        )
```

---

## **Next Steps**

Now that you’ve learned about the **Agent System**, here are some next steps:
- Explore **LLM Integration** to add advanced decision-making capabilities to your agents.
- Learn about the **Tool System** to extend your agents with reusable functions.
- Dive into the **Tape System** to record and analyze agent execution history.
