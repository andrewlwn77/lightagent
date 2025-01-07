# Getting Started with the Lightweight Agent Framework

Welcome to the **Lightweight Agent Framework (LAF)**! This guide will help you get started with building autonomous agents that can think, act, and observe within a structured environment. Whether you're building simple agents or complex workflows, LAF provides the tools you need to create, manage, and extend agents with ease.

---

## **Installation**

### **Basic Installation**

To install the Lightweight Agent Framework, use `pip`:

```bash
pip install robotape
```

This will install the core framework and its dependencies.

---

### **Development Installation**

If you're planning to contribute to the framework or need additional development tools (e.g., testing utilities), install the `dev` extras:

```bash
pip install robotape[dev]
```

---

## **Core Concepts**

Before diving into code, let's understand the key concepts of the framework:

1. **Agents**: Autonomous entities that can think, act, and observe.
2. **Tapes**: A record of an agent's execution history, consisting of steps.
3. **Steps**: Individual actions or thoughts within a tape (e.g., THOUGHT, ACTION, OBSERVATION).
4. **Tools**: Reusable functions that agents can use to extend their capabilities.
5. **LLM Integration**: Built-in support for Large Language Models (LLMs) like OpenAI, Anthropic, and HuggingFace.

---

## **Quickstart Example**

Let’s create a simple agent that processes some text. This example will demonstrate how to:
- Create an agent.
- Record its actions using a tape.
- Execute the agent asynchronously.

### **Step 1: Create an Agent**

```python
from robotape.agents import SimpleAgent
from robotape.tape import Tape, Step, StepMetadata, StepType

# Create an agent
agent = SimpleAgent("text_processor")
```

### **Step 2: Create a Tape**

```python
# Create a tape to record the agent's actions
tape = Tape()
```

### **Step 3: Add an Initial Thought**

```python
# Add an initial thought step
initial_thought = Step(
    type=StepType.THOUGHT,
    content="I should process the input text",
    metadata=StepMetadata(
        agent="text_processor",
        node="planning"
    )
)
tape.append(initial_thought)
```

### **Step 4: Execute the Agent**

```python
# Execute the agent asynchronously
async def process_text():
    result = await agent.execute_step(tape.get_last_step())
    print(f"Agent result: {result.output}")

# Run in an async context
import asyncio
asyncio.run(process_text())
```

---

### **Expected Output**

When you run the above code, the agent will process the initial thought and produce an output. The result will be printed to the console:

```
Agent result: I should process the input text
```

---

## **Next Steps**

Now that you’ve created your first agent, here are some next steps to explore:

1. **Explore Built-in Agents**:
   - Learn about `SimpleAgent` and `LLMAwareAgent`.
   - Experiment with extending these agents to add custom behavior.

2. **Work with Tapes**:
   - Learn how to record, replay, and analyze agent execution history using tapes.

3. **Integrate Tools**:
   - Extend your agent’s capabilities by adding tools.

4. **Use LLMs**:
   - Explore how to integrate Large Language Models (LLMs) into your agents.

---

## **Common Issues and Solutions**

1. **Async/Await Usage**:
   - Always use `async/await` with agent methods.
   - Run async code in an event loop (e.g., `asyncio.run()`).

2. **Tool Development**:
   - Validate input parameters in tools.
   - Handle errors gracefully and use retry mechanisms for unreliable operations.

3. **Storage Management**:
   - Regularly clean up old tapes to avoid storage bloat.
   - Use tags to organize tapes for better management.

---

## **Available Documentation**

The framework provides comprehensive documentation covering various aspects:

1. **[API Reference](api_reference.md)**: Complete reference of all public APIs, classes, and methods.

2. **[Advanced Patterns](advanced_patterns.md)**: Learn about advanced usage patterns and best practices.

3. **[Agent System](agents.md)**: Detailed guide on creating and managing different types of agents.

4. **[LLM Integration](llm_integration.md)**: Guide on integrating and using Large Language Models.

5. **[MCP (Master Control Program)](mcp.md)**: Understanding the Master Control Program component.

6. **[MCP Tools](mcp_tools.md)**: Tools and utilities available in the MCP system.

7. **[Tape System](tape_system.md)**: Deep dive into the tape system for recording and analyzing agent execution.

8. **[Tools](tools.md)**: Comprehensive guide on using and creating tools for agents.