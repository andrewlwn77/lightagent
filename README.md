# Lightweight Agent Framework

A minimalist, extensible framework for building autonomous agents.

## Features

- Simple and flexible tape-based execution system
- Modular tool integration
- Built-in storage capabilities
- Easy-to-extend agent implementations

## Installation

```bash
pip install lightagent
```

## Quick Start

```python
from lightagent.agents import SimpleAgent
from lightagent.tape import Tape

agent = SimpleAgent()
tape = Tape()

# Add steps to the tape
tape.add_step("search", {"query": "python programming"})
tape.add_step("process", {"data": "search_results"})

# Run the agent
agent.run(tape)
```

## Documentation

For more detailed information, check out:

- [Getting Started](docs/getting_started.md)
- [Tape System](docs/tape_system.md)
- [Agents](docs/agents.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
