# Model Control Protocol (MCP)

The **Model Control Protocol (MCP)** is a protocol that allows agents to interact with external tools and services through a standardized interface. In the Lightweight Agent Framework, MCP is used to extend the capabilities of agents by enabling them to execute external commands, manage resources, and integrate with various tools. This section covers:

1. **What is MCP?**: An overview of MCP and its role in the framework.
2. **Using MCP with Agents**: How to integrate MCP into agents using the `MCPLLMAgent` class.
3. **Creating an MCP Client**: How to create and manage an MCP client session.
4. **Error Handling in MCP**: Best practices for handling errors in MCP workflows.

---

## **What is MCP?**

The **Model Control Protocol (MCP)** is a protocol designed to standardize the way agents interact with external tools and services. It provides a structured way to:
- **Execute external commands**: Run commands and tools in a controlled environment.
- **Manage resources**: Handle connections, sessions, and resource cleanup.
- **Integrate with tools**: Use predefined tools like `get_data` and `process_data` to interact with external systems.

In the Lightweight Agent Framework, MCP is integrated into agents through the `MCPLLMAgent` class, which combines the capabilities of LLMs (Large Language Models) with MCP to enable complex workflows.

---

## **Using MCP with Agents**

The `MCPLLMAgent` class is a specialized agent that combines LLM and MCP capabilities. It allows agents to generate thoughts using an LLM and execute actions using MCP tools.

### **Example: Creating an MCPLLMAgent**

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

### **Available Tools**

The `MCPLLMAgent` comes with a set of predefined tools that can be extended:

- **get_data**: Retrieves data from the system based on a query.
- **process_data**: Processes data using predefined logic.

You can extend the available tools by modifying the `available_tools` dictionary in the `MCPLLMAgent` class.

---

## **Creating an MCP Client**

The `create_mcp_client` function is used to create an MCP client session. This client session is used to interact with an MCP server, which manages connections to external systems and tools.

### **Example**

```python
from robotape.utils.mcp import create_mcp_client, StdioServerParameters

# Define MCP server parameters
mcp_params = StdioServerParameters(
    command="python",
    args=["path/to/mcp_server.py"],
    env={"ENV_VAR": "value"}
)

# Create an MCP client
mcp_client = await create_mcp_client(mcp_params)
```

### **MCP Client Session**

The `MCPClientSession` class represents a session with an MCP server. It provides methods to initialize and close the session.

```python
from robotape.utils.mcp import MCPClientSession

# Example of using MCPClientSession
session = MCPClientSession(
    name="mcp-client",
    config={
        "command": "python",
        "args": ["path/to/mcp_server.py"],
        "env": {"ENV_VAR": "value"}
    }
)

await session.initialize()  # Initialize the session
await session.close()       # Close the session
```

---

## **Error Handling in MCP**

### **Handling Connection Errors**

When connecting to an MCP server, handle connection errors gracefully.

#### **Example**

```python
try:
    mcp_client = await create_mcp_client(mcp_params)
except Exception as e:
    print(f"Failed to connect to MCP server: {e}")
```

### **Handling Tool Execution Errors**

When executing tools, handle errors and retries as needed.

#### **Example**

```python
try:
    result = await agent.act(thought)
    if not result.success:
        print(f"Tool failed: {result.error}")
except Exception as e:
    print(f"Error executing tool: {e}")
```

---

## **Next Steps**

Now that you’ve learned about **Model Control Protocol (MCP)**, here are some next steps:
- Explore **Testing and Debugging** to ensure your MCP workflows work as expected.
- Dive into **Advanced Patterns** for performance optimization and security considerations.
- Review the **API Reference** for detailed documentation on MCP-related classes and functions.

---

This **Model Control Protocol (MCP)** section provides a detailed overview of how to use MCP to connect agents to external tools and services. Let me know if you’d like to adjust anything or add more details! Once you’re happy with this section, we can move on to the next part of the documentation.