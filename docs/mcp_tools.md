# Integrating MCP with Tools

The **Model Control Protocol (MCP)** allows agents to interact with external tools and services managed by an **MCP server**. The **MCP client** is used to communicate with the server, while the **tools** act as the interface for the agent to interact with the MCP server. This section covers:

1. **MCP-Enabled Tools**: How to create tools that interact with an MCP server via the MCP client.
2. **Tool Execution via MCP**: How to execute tools through the MCP client.
3. **Error Handling and Retries**: Best practices for handling errors when using MCP-enabled tools.
4. **Example: MCP Tool Integration**: A complete example of integrating MCP with tools.

---

## **MCP-Enabled Tools**

MCP-enabled tools are tools that interact with an **MCP server** via the **MCP client**. These tools can be created by extending the `Tool` class and using the `MCPClientSession` to communicate with the MCP server.

### **Example: Creating an MCP-Enabled Tool**

```python
from robotape.tools import Tool, RunContext
from robotape.utils.mcp import MCPClientSession, StdioServerParameters

class MCPTool(Tool):
    """A tool that interacts with an MCP server via the MCP client."""
    def __init__(self, mcp_client: MCPClientSession, tool_name: str, max_retries: int = 3):
        self.mcp_client = mcp_client
        self.tool_name = tool_name
        super().__init__(self._execute_mcp_tool, max_retries=max_retries)

    async def _execute_mcp_tool(self, ctx: RunContext[str], **kwargs) -> Dict[str, Any]:
        """Execute a tool via the MCP server using the MCP client."""
        # Simulate tool execution through MCP
        result = {
            "tool": self.tool_name,
            "parameters": kwargs,
            "result": f"Simulated execution of {self.tool_name} with {kwargs}"
        }
        return result
```

In this example, the `MCPTool` class extends the `Tool` class and uses an `MCPClientSession` to interact with the MCP server. The `_execute_mcp_tool` method simulates the execution of a tool via the MCP server.

---

## **Tool Execution via MCP**

To execute tools through the MCP server, you need to create an `MCPClientSession` and pass it to the `MCPTool` class. The `MCPClientSession` is responsible for managing the connection to the MCP server.

### **Example: Executing a Tool via MCP**

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

# Create an MCP-enabled tool
mcp_tool = MCPTool(mcp_client, tool_name="get_data")

# Execute the tool
context = RunContext(
    deps="test",
    usage=0,
    prompt="test tool",
    tape=Tape()
)

result = await mcp_tool.execute({"query": "test query"}, context)
print(result)  # Output: {"tool": "get_data", "parameters": {"query": "test query"}, "result": "Simulated execution of get_data with {'query': 'test query'}"}
```

In this example, the `MCPTool` is created with an `MCPClientSession`, and the tool is executed with a query parameter. The result is a simulated execution of the tool via the MCP server.

---

## **Error Handling and Retries**

When using MCP-enabled tools, it’s important to handle errors and implement retries for unreliable operations (e.g., network calls). The `Tool` class already provides a built-in retry mechanism, which can be customized.

### **Example: Handling Errors in MCP Tools**

```python
class RobustMCPTool(MCPTool):
    """A robust MCP-enabled tool with custom error handling."""
    async def _execute_mcp_tool(self, ctx: RunContext[str], **kwargs) -> Dict[str, Any]:
        try:
            # Simulate tool execution through MCP
            result = {
                "tool": self.tool_name,
                "parameters": kwargs,
                "result": f"Simulated execution of {self.tool_name} with {kwargs}"
            }
            return result
        except Exception as e:
            # Log the error and retry
            logger.error(f"Error executing tool {self.tool_name}: {e}")
            raise
```

In this example, the `RobustMCPTool` class extends `MCPTool` and adds custom error handling. If an error occurs during tool execution, it is logged, and the retry mechanism is triggered.

---

## **Example: MCP Tool Integration**

Here’s a complete example of integrating MCP with tools in an agent:

```python
from robotape.agents.mcpllm import MCPLLMAgent
from robotape.llm import LLMConfig
from robotape.tools import Tool, RunContext
from robotape.utils.mcp import create_mcp_client, StdioServerParameters

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

# Create an MCP-enabled tool
mcp_tool = MCPTool(agent.mcp_client, tool_name="get_data")

# Execute a full think-act-observe cycle
context = {"task": "Analyze test data"}
thought_result = await agent.think(context)
action_result = await mcp_tool.execute({"query": "test query"}, RunContext(
    deps="test",
    usage=0,
    prompt="test tool",
    tape=Tape()
))
observe_result = await agent.observe(action_result)
```

In this example, the `MCPLLMAgent` is used to create an agent that combines LLM and MCP capabilities. The `MCPTool` is used to execute a tool via the MCP server, and the results are observed by the agent.

---

## **Next Steps**

Now that you’ve learned how to integrate **MCP with tools**, here are some next steps:
- Explore **Testing and Debugging** to ensure your MCP-enabled tools work as expected.
- Dive into **Advanced Patterns** for performance optimization and security considerations.
- Review the **API Reference** for detailed documentation on MCP-related classes and functions.
