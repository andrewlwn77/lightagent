# tools.py
from typing import Any, Callable, Dict, Generic, Optional, TypeVar, Union, ParamSpec, Awaitable, get_type_hints
from dataclasses import dataclass
from pydantic import BaseModel, TypeAdapter, ConfigDict
from inspect import signature, Signature
import inspect

# Previously defined tape classes
from .tape import Tape, Step, StepMetadata, StepType

# Type variables for generic types
AgentDeps = TypeVar('AgentDeps')
ToolParams = ParamSpec('ToolParams')

@dataclass
class RunContext(Generic[AgentDeps]):
    """Information about the current call."""
    deps: AgentDeps
    usage: int  # Simplified usage tracking
    prompt: str
    tape: Tape
    tool_name: Optional[str] = None
    retry: int = 0

    def replace_with(self, **kwargs) -> 'RunContext[AgentDeps]':
        return dataclass.replace(self, **kwargs)

class ToolDefinition(BaseModel):
    """Definition of a tool passed to a model."""
    name: str
    description: str
    parameters_json_schema: Dict[str, Any]
    outer_typed_dict_key: Optional[str] = None

def function_schema(function: Callable[..., Any], takes_ctx: bool) -> Dict[str, Any]:
    """Build validation schema from a function."""
    sig = signature(function)
    type_hints = get_type_hints(function)
    
    parameters_json_schema = {}
    required = []
    properties = {}

    # Skip the first parameter if it's context
    start_idx = 1 if takes_ctx else 0
    
    # Process each parameter
    for name, param in list(sig.parameters.items())[start_idx:]:
        if param.annotation == sig.empty:
            # Default to Any if no annotation
            schema = {"type": "object"}
        else:
            # Get annotation from type hints
            annotation = type_hints[name]
            adapter = TypeAdapter(annotation)
            schema = adapter.json_schema()
        
        properties[name] = schema
        if param.default == param.empty:
            required.append(name)
    
    parameters_json_schema = {
        "type": "object",
        "properties": properties,
        "required": required
    }

    return {
        "parameters_json_schema": parameters_json_schema,
        "description": function.__doc__ or "",
        "name": function.__name__
    }

class Tool(Generic[AgentDeps]):
    """A tool function for an agent."""
    def __init__(
        self,
        function: Callable[..., Any],
        *,
        takes_ctx: bool = None,
        max_retries: int = 3,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ):
        self.function = function
        self.takes_ctx = takes_ctx if takes_ctx is not None else self._infer_takes_ctx(function)
        self.max_retries = max_retries
        
        # Get schema and other metadata
        schema = function_schema(function, self.takes_ctx)
        self.name = name or schema["name"]
        self.description = description or schema["description"]
        self.parameters_json_schema = schema["parameters_json_schema"]
        
        # Set up validation
        self.validator = TypeAdapter(
            schema["parameters_json_schema"],
            config=ConfigDict(arbitrary_types_allowed=True)
        )
        
        self.is_async = inspect.iscoroutinefunction(function)
        self.current_retry = 0

    def _infer_takes_ctx(self, function: Callable) -> bool:
        """Infer if the function takes a RunContext parameter."""
        sig = signature(function)
        if not sig.parameters:
            return False
        first_param = next(iter(sig.parameters.values()))
        return first_param.annotation != sig.empty and issubclass(first_param.annotation, RunContext)

    async def execute(self, args: Dict[str, Any], context: RunContext[AgentDeps]) -> Any:
        """Execute the tool with validation."""
        try:
            # Validate arguments
            validated_args = self.validator.validate_python(args)
            
            # Prepare arguments
            call_args = [context] if self.takes_ctx else []
            call_args.extend(validated_args.values())
            
            # Execute function
            if self.is_async:
                result = await self.function(*call_args)
            else:
                result = self.function(*call_args)
            
            # Record the execution in the tape
            context.tape.append(Step(
                type=StepType.ACTION,
                content={"args": args, "result": result},
                metadata=StepMetadata(
                    agent="agent",  # This would be more specific in practice
                    node=self.name,
                )
            ))
            
            return result
            
        except Exception as e:
            self.current_retry += 1
            if self.current_retry > self.max_retries:
                raise
            
            # Record the failure in the tape
            context.tape.append(Step(
                type=StepType.THOUGHT,
                content=f"Tool execution failed: {str(e)}. Retry {self.current_retry}/{self.max_retries}",
                metadata=StepMetadata(
                    agent="agent",
                    node=self.name,
                )
            ))
            
            # Re-raise to allow retry logic
            raise

# Example usage

async def example_search_tool(ctx: RunContext[str], query: str) -> Dict[str, Any]:
    """Search tool example."""
    # Simulate search
    return {"results": [f"Result for {query}"]}

def create_example():
    # Create tool
    tool = Tool(example_search_tool)
    
    # Create context with tape
    context = RunContext(
        deps="example_dep",
        usage=0,
        prompt="Search for something",
        tape=Tape()
    )
    
    # Tool definition for LLM
    tool_def = ToolDefinition(
        name=tool.name,
        description=tool.description,
        parameters_json_schema=tool.parameters_json_schema
    )
    
    return tool, context, tool_def