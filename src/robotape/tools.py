# src/robotape/tools.py
from typing import Any, Callable, Dict, Generic, Optional, TypeVar, Union, ParamSpec, Awaitable, get_type_hints, get_origin, get_args
from dataclasses import dataclass
from pydantic import BaseModel, TypeAdapter, ConfigDict, create_model
from inspect import signature, Signature
import inspect
from .llm import BaseLLM
from .utils.logging import get_logger, log_execution

logger = get_logger(__name__)

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
    
    # Process each parameter and create field definitions
    fields = {}
    for name, param in list(sig.parameters.items())[start_idx:]:
        if param.annotation == sig.empty:
            fields[name] = (Any, ... if param.default == param.empty else param.default)
        else:
            fields[name] = (param.annotation, ... if param.default == param.empty else param.default)

    # Create a dynamic model for validation
    model = create_model('ToolParameters', **fields)
    schema = model.model_json_schema()
    
    return {
        "parameters_json_schema": schema,
        "description": function.__doc__ or "",
        "name": function.__name__,
        "model": model
    }

def _is_run_context_type(type_hint: Any) -> bool:
    """Check if a type hint is a RunContext or a subclass of RunContext."""
    if type_hint == RunContext:
        return True
    origin = get_origin(type_hint)
    if origin is None:
        return False
    if origin == RunContext:
        return True
    return False

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
        self.validator = schema["model"]
        
        self.is_async = inspect.iscoroutinefunction(function)
        self.current_retry = 0

    def _infer_takes_ctx(self, function: Callable) -> bool:
        """Infer if the function takes a RunContext parameter."""
        sig = signature(function)
        if not sig.parameters:
            return False
        first_param = next(iter(sig.parameters.values()))
        if first_param.annotation == sig.empty:
            return False
        return _is_run_context_type(first_param.annotation)

    @log_execution
    async def execute(self, args: Dict[str, Any], context: RunContext[AgentDeps]) -> Any:
        """Execute the tool with validation."""
        try:
            # Validate arguments
            validated_args = self.validator(**args)
            
            # Prepare arguments
            call_args = [context] if self.takes_ctx else []
            call_args.extend([getattr(validated_args, key) for key in args.keys()])
            
            # Execute function
            if self.is_async:
                result = await self.function(*call_args)
            else:
                result = self.function(*call_args)
            
            # Record the successful execution in the tape
            context.tape.append(Step(
                type=StepType.ACTION,
                content={"args": args, "result": result},
                metadata=StepMetadata(
                    agent="agent",
                    node=self.name,
                )
            ))
            
            # Reset retry counter on success
            self.current_retry = 0
            return result
            
        except Exception as e:
            self.current_retry += 1
            
            # Only record the error if we're going to stop trying
            if self.current_retry > self.max_retries:
                context.tape.append(Step(
                    type=StepType.THOUGHT,
                    content=f"Tool execution failed: {str(e)}. Retry {self.current_retry}/{self.max_retries}",
                    metadata=StepMetadata(
                        agent="agent",
                        node=self.name,
                    )
                ))
                raise
            
            # Try again if we haven't exceeded max retries
            return await self.execute(args, context)

class LLMTool(Tool):
    """Tool for LLM text generation."""
    
    def __init__(self, llm: BaseLLM, max_retries: int = 3):
        async def _generate(ctx: RunContext[str], prompt: str) -> str:
            """Generate text using the LLM."""
            response = await llm.generate(prompt)
            return response.text
        
        super().__init__(_generate, max_retries=max_retries)
        self.llm = llm