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
from lightagent.agents import BaseAgent
from lightagent.models.steps import StepResult

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
from lightagent.agents import SimpleAgent

agent = SimpleAgent("my_agent")
```

Key features:
- Basic think-act-observe cycle
- Error handling
- Tape integration
- Tool support

## Creating Custom Agents

### Basic Custom Agent

```python
from lightagent.agents import BaseAgent
from lightagent.models.steps import StepResult

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

### Agent with Tools

```python
from lightagent.agents import BaseAgent
from lightagent.tools import Tool, RunContext

class ToolEnabledAgent(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name)
        self.search_tool = Tool(self._search_function)
    
    async def _search_function(self, ctx: RunContext[str], query: str):
        # Implement search logic
        return {"results": [f"Result for {query}"]}
    
    async def act(self, thought):
        # Use tool in action
        context = RunContext(
            deps="tool_deps",
            usage=0,
            prompt=thought.content,
            tape=self.current_tape
        )
        
        result = await self.search_tool.execute(
            {"query": thought.content},
            context
        )
        return StepResult(success=True, output=result)
```

## Error Handling

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

## Advanced Patterns

### Composable Agents

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

### Stateful Agents

Maintain state across executions:

```python
class StatefulAgent(BaseAgent):
    def __init__(self, name: str):
        super().__init__(name)
        self.state = {}
    
    async def think(self, context):
        # Access previous state
        previous_results = self.state.get("results", [])
        
        # Update state
        self.state["last_context"] = context
        
        return StepResult(
            success=True,
            output=f"Processed {len(previous_results)} previous results"
        )
```

## Best Practices

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

## Performance Considerations

1. **Async Operations**
   - Use async/await consistently
   - Avoid blocking operations
   - Handle concurrent execution properly

2. **Memory Management**
   - Clean up large objects
   - Limit state size
   - Use proper data structures

3. **Tool Optimization**
   - Implement caching where appropriate
   - Use connection pooling
   - Handle rate limiting

## Debugging Agents

```python
from lightagent.utils.logging import setup_logging

# Enable debug logging
setup_logging(debug=True)

class DebuggableAgent(BaseAgent):
    async def think(self, context):
        logger.debug(f"Thinking with context: {context}")
        result = await super().think(context)
        logger.debug(f"Thought result: {result}")
        return result
```

## Security Considerations

1. **Input Validation**
   - Validate all inputs
   - Sanitize data appropriately
   - Handle sensitive information properly

2. **Tool Security**
   - Implement proper authentication
   - Use secure connections
   - Handle credentials safely

3. **Access Control**
   - Implement agent permissions
   - Control tool access
   - Audit agent actions