# Tape System

The **Tape System** is a powerful mechanism for recording and analyzing agent execution history. A **tape** is a sequential record of **steps** that captures an agent's thoughts, actions, and observations. This section covers:

1. **Tape**: The primary container for steps.
2. **Steps**: Individual records within a tape (e.g., THOUGHT, ACTION, OBSERVATION).
3. **Step Types**: The different types of steps and their purposes.
4. **Working with Tapes**: Creating, querying, and branching tapes.
5. **Storage and Persistence**: Saving and loading tapes using `TapeStore`.

---

## **Tape**

The `Tape` class is the primary container for steps. It provides methods for appending, querying, and managing steps.

### **Example**

```python
from robotape.tape import Tape, Step, StepMetadata, StepType

# Create a new tape
tape = Tape()

# Add steps
tape.append(Step(
    type=StepType.THOUGHT,
    content="I should search for information",
    metadata=StepMetadata(agent="my_agent", node="planning")
))

tape.append(Step(
    type=StepType.ACTION,
    content={"tool": "search", "query": "python"},
    metadata=StepMetadata(agent="my_agent", node="executor")
))

tape.append(Step(
    type=StepType.OBSERVATION,
    content={"results": ["result1", "result2"]},
    metadata=StepMetadata(agent="my_agent", node="observer")
))
```

---

## **Steps**

Steps are individual records within a tape. Each step has:
- A **type** (e.g., THOUGHT, ACTION, OBSERVATION).
- **Content**: The data associated with the step.
- **Metadata**: Additional information about the step (e.g., agent, node).

### **Step Types**

There are three primary step types:

1. **THOUGHT**: Planning and reasoning steps.
   ```python
   thought_step = Step(
       type=StepType.THOUGHT,
       content="I should search for information",
       metadata=StepMetadata(agent="agent", node="planner")
   )
   ```

2. **ACTION**: Execution and tool usage steps.
   ```python
   action_step = Step(
       type=StepType.ACTION,
       content={"tool": "search", "query": "python"},
       metadata=StepMetadata(agent="agent", node="executor")
   )
   ```

3. **OBSERVATION**: Results and feedback steps.
   ```python
   observation_step = Step(
       type=StepType.OBSERVATION,
       content={"results": ["result1", "result2"]},
       metadata=StepMetadata(agent="agent", node="observer")
   )
   ```

---

## **Working with Tapes**

### **Creating and Appending Steps**

```python
# Create a new tape
tape = Tape()

# Add steps
tape.append(thought_step)
tape.append(action_step)
tape.append(observation_step)
```

### **Querying Steps**

```python
# Get all thoughts
thoughts = tape.get_steps_by_type(StepType.THOUGHT)

# Get steps by agent
agent_steps = tape.get_steps_by_agent("my_agent")

# Get the last step
last_step = tape.get_last_step()
```

### **Branching and Cloning**

You can create new tapes from existing ones, preserving the parent-child relationship.

```python
# Clone a tape
new_tape = tape.clone()

# Verify lineage
print(new_tape.metadata.parent_id)  # Shows original tape's ID
```

---

## **Storage and Persistence**

The framework includes a built-in storage system (`TapeStore`) for persisting tapes.

### **Example**

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

---

## **Best Practices**

1. **Step Content**:
   - Use structured data for step content.
   - Include relevant context in metadata.
   - Keep content serializable.

2. **Tape Organization**:
   - Use meaningful agent and node names.
   - Add tags for categorization.
   - Maintain clear tape lineage.

3. **Storage Management**:
   - Implement retention policies.
   - Use tags for organization.
   - Clean up old tapes regularly.

4. **Branching Strategy**:
   - Branch for experimental paths.
   - Maintain clear parent-child relationships.
   - Document branch purposes.

---

## **Advanced Usage**

### **Custom Step Types**

You can extend the system with custom step types.

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

### **Tape Analysis**

You can implement utilities to analyze tape execution patterns.

```python
from datetime import datetime

def analyze_tape(tape: Tape) -> Dict[str, Any]:
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

---

## **Next Steps**

Now that you’ve learned about the **Tape System**, here are some next steps:
- Explore **MCP (Multi-Component Processing)** for building complex workflows.
- Learn about **Advanced Patterns** for error handling, concurrency, and performance optimization.
- Dive into **Testing and Debugging** to ensure your agents and tapes work as expected.
