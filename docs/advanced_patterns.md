# Advanced Patterns

This section covers advanced patterns and best practices for building agents in the Lightweight Agent Framework. These patterns will help you create robust, efficient, and secure agents.

---

## **Error Handling and Retries**

### **Robust Error Handling**

Agents should handle errors gracefully to ensure they can recover from unexpected situations. Use `try-except` blocks to catch and handle exceptions.

#### **Example**

```python
from robotape.agents import BaseAgent
from robotape.models.steps import StepResult

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

### **Retry Mechanism**

For unreliable operations (e.g., network calls), implement a retry mechanism to handle transient failures.

#### **Example**

```python
from robotape.tools import Tool, RunContext

class RetryTool(Tool):
    def __init__(self, max_retries: int = 3):
        super().__init__(self._retry_function, max_retries=max_retries)
    
    async def _retry_function(self, ctx: RunContext[str]) -> str:
        """A function that retries on failure."""
        import random
        if random.random() < 0.5:
            raise ValueError("Temporary failure!")
        return "Success"
```

---

## **Concurrency and Async Best Practices**

### **Async/Await**

The framework is built on `asyncio`, so always use `async/await` for asynchronous operations.

#### **Example**

```python
async def run_agent():
    agent = SimpleAgent("my_agent")
    result = await agent.think({"task": "process data"})
    print(result.output)
```

### **Concurrent Execution**

Use `asyncio.gather` to run multiple tasks concurrently.

#### **Example**

```python
import asyncio

async def run_concurrent_agents():
    agent1 = SimpleAgent("agent1")
    agent2 = SimpleAgent("agent2")
    
    results = await asyncio.gather(
        agent1.think({"task": "task1"}),
        agent2.think({"task": "task2"})
    )
    
    for result in results:
        print(result.output)
```

---

## **Performance Optimization**

### **Memory Management**

- Clean up large objects when they are no longer needed.
- Use generators or iterators for large datasets.

#### **Example**

```python
async def process_large_data():
    for chunk in read_large_file():
        await process_chunk(chunk)
```

### **Caching**

Implement caching for expensive operations (e.g., LLM calls, API requests).

#### **Example**

```python
from functools import lru_cache

@lru_cache(maxsize=100)
async def cached_llm_call(prompt: str) -> str:
    llm = create_llm(LLMConfig(model="gpt-4", api_key="your-api-key"))
    response = await llm.generate(prompt)
    return response.text
```

### **Connection Pooling**

Use connection pooling for database or API connections to improve performance.

#### **Example**

```python
from aiohttp import ClientSession

async def fetch_data(url: str):
    async with ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

---

## **Security Considerations**

### **Input Validation**

Always validate inputs to prevent security vulnerabilities (e.g., injection attacks).

#### **Example**

```python
from pydantic import BaseModel, ValidationError

class InputModel(BaseModel):
    query: str
    limit: int

async def safe_tool(ctx: RunContext[str], input_data: Dict[str, Any]) -> Dict[str, Any]:
    try:
        validated_input = InputModel(**input_data)
    except ValidationError as e:
        raise ValueError(f"Invalid input: {e}")
    
    return {"results": [f"Result for {validated_input.query}"]}
```

### **Tool Security**

- Use secure connections (e.g., HTTPS) for API calls.
- Handle credentials securely (e.g., environment variables, secret management).

#### **Example**

```python
import os
from robotape.tools import Tool

class SecureAPITool(Tool):
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        super().__init__(self._call_secure_api)
    
    async def _call_secure_api(self, ctx: RunContext[str], query: str) -> Dict[str, Any]:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://secure-api.example.com/search",
                params={"q": query},
                headers={"Authorization": f"Bearer {self.api_key}"}
            ) as response:
                return await response.json()
```

### **Access Control**

Implement permissions and access control for agents and tools.

#### **Example**

```python
class RestrictedAgent(BaseAgent):
    def __init__(self, name: str, allowed_actions: List[str]):
        super().__init__(name)
        self.allowed_actions = allowed_actions
    
    async def act(self, thought: Step) -> StepResult:
        if thought.content["action"] not in self.allowed_actions:
            return StepResult(
                success=False,
                error="Action not allowed",
                metadata={"action": thought.content["action"]}
            )
        return await super().act(thought)
```

---

## **Next Steps**

Now that you’ve learned about **Advanced Patterns**, here are some next steps:
- Explore **Testing and Debugging** to ensure your agents and tools work as expected.
- Dive into **MCP (Multi-Component Processing)** for building complex workflows.
- Review the **API Reference** for detailed documentation on all major classes.