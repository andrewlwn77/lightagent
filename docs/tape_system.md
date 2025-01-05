# Tape System Documentation

The tape system is a core component of the Lightweight Agent Framework, providing a mechanism to record, analyze, and replay agent operations.

## Overview

A tape is a sequential record of steps that captures an agent's:
- Thoughts (planning and reasoning)
- Actions (operations and tool usage)
- Observations (results and feedback)

## Core Components

### Tape

The `Tape` class is the primary container for steps:

```python
from robotape.tape import Tape, TapeMetadata

tape = Tape(
    metadata=TapeMetadata(
        author="my_agent",
        parent_id=None  # Set for branched tapes
    )
)
```

### Steps

Steps are individual records within a tape:

```python
from robotape.tape import Step, StepMetadata, StepType

step = Step(
    type=StepType.THOUGHT,
    content="I should process this data",
    metadata=StepMetadata(
        agent="my_agent",
        node="planning"
    )
)
```

### Step Types

There are three primary step types:

1. **THOUGHT**: Planning and reasoning steps
   ```python
   thought_step = Step(
       type=StepType.THOUGHT,
       content="I should search for information",
       metadata=StepMetadata(agent="agent", node="planner")
   )
   ```

2. **ACTION**: Execution and tool usage steps
   ```python
   action_step = Step(
       type=StepType.ACTION,
       content={"tool": "search", "query": "python"},
       metadata=StepMetadata(agent="agent", node="executor")
   )
   ```

3. **OBSERVATION**: Results and feedback steps
   ```python
   observation_step = Step(
       type=StepType.OBSERVATION,
       content={"results": ["result1", "result2"]},
       metadata=StepMetadata(agent="agent", node="observer")
   )
   ```

## Working with Tapes

### Creating and Appending Steps

```python
# Create a new tape
tape = Tape()

# Add steps
tape.append(thought_step)
tape.append(action_step)
tape.append(observation_step)
```

### Querying Steps

```python
# Get all thoughts
thoughts = tape.get_steps_by_type(StepType.THOUGHT)

# Get steps by agent
agent_steps = tape.get_steps_by_agent("my_agent")

# Get the last step
last_step = tape.get_last_step()
```

### Branching and Cloning

Create new tapes from existing ones:

```python
# Clone a tape
new_tape = tape.clone()  # Creates new tape with reference to parent

# Verify lineage
print(new_tape.metadata.parent_id)  # Shows original tape's ID
```

## Storage System

The framework includes a built-in storage system:

```python
from robotape.storage import TapeStore

# Initialize storage
store = TapeStore("sqlite:///tapes.db")

# Save a tape
tape_id = store.save_tape(tape)

# Load a tape
loaded_tape = store.load_tape(tape_id)

# Get tape history
history = store.get_tape_history(tape_id)

# Search tapes
results = store.search_tapes(
    agent="my_agent",
    node="planning",
    tags=["experiment1"]
)
```

## Best Practices

1. **Step Content**
   - Use structured data for step content
   - Include relevant context in metadata
   - Keep content serializable

2. **Tape Organization**
   - Use meaningful agent and node names
   - Add tags for categorization
   - Maintain clear tape lineage

3. **Storage Management**
   - Implement retention policies
   - Use tags for organization
   - Clean up old tapes regularly

4. **Branching Strategy**
   - Branch for experimental paths
   - Maintain clear parent-child relationships
   - Document branch purposes

## Advanced Usage

### Custom Step Types

Extend the system with custom step types:

```python
from enum import Enum
from robotape.tape import Step

class CustomStepType(str, Enum):
    ANALYSIS = "analysis"
    VALIDATION = "validation"

# Use custom step type
analysis_step = Step(
    type=CustomStepType.ANALYSIS,
    content={"analysis": "data"},
    metadata=StepMetadata(agent="analyst", node="data_analysis")
)
```

### Tape Analysis

Implement tape analysis utilities:

```python
def analyze_tape(tape: Tape):
    """Analyze tape execution patterns."""
    step_counts = {}
    for step in tape.steps:
        step_counts[step.type] = step_counts.get(step.type, 0) + 1
    
    timing_data = []
    for i in range(1, len(tape.steps)):
        prev_time = datetime.fromisoformat(tape.steps[i-1].metadata.timestamp)
        curr_time = datetime.fromisoformat(tape.steps[i].metadata.timestamp)
        timing_data.append((curr_time - prev_time).total_seconds())
    
    return {
        "step_counts": step_counts,
        "avg_step_time": sum(timing_data) / len(timing_data) if timing_data else 0,
        "total_steps": len(tape.steps)
    }
```

## Error Handling

Implement robust error handling:

```python
try:
    # Attempt to add step
    tape.append(step)
except Exception as e:
    # Create error step
    error_step = Step(
        type=StepType.ERROR,
        content={"error": str(e)},
        metadata=StepMetadata(agent="error_handler", node="error")
    )
    tape.append(error_step)
```