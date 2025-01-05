# Lightweight Agent Framework

A minimalist, extensible framework for building autonomous agents with a focus on transparency and composability.

## Overview

Lightweight Agent Framework (LAF) provides a simple yet powerful foundation for building autonomous agents that can think, act, and observe within a structured environment. With LAF, you can:

- Create agents that follow a clear think-act-observe cycle
- Record and replay agent interactions using the tape system
- Build complex workflows by composing multiple agents
- Persist and analyze agent execution history
- Extend functionality through a modular tool system

## Key Features

- 🎯 **Simple Core Concepts**: Based on three fundamental operations - think, act, and observe
- 📼 **Tape-Based History**: Record every step of your agent's execution for analysis and debugging
- 🛠 **Modular Tools**: Easily extend agent capabilities through a flexible tool system
- 💾 **Built-in Storage**: Persist agent history with built-in SQLite support (expandable to other backends)
- 🔄 **Async Support**: Built with asyncio for efficient concurrent operations
- 🧪 **Testing Ready**: Comprehensive testing utilities and fixtures included

## Quick Installation

```bash
pip install lightagent
```

For development installation:

```bash
pip install lightagent[dev]
```

## Basic Usage

Here's a simple example of creating and running an agent:

```python
from lightagent.agents import SimpleAgent
from lightagent.tape import Tape, StepType

# Create an agent and a tape
agent = SimpleAgent("my_agent")
tape = Tape()

# Add an initial thought
tape.append(Step(
    type=StepType.THOUGHT,
    content="I should search for information",
    metadata=StepMetadata(agent="my_agent", node="planning")
))

# Execute the agent
await agent.execute_step(tape.get_last_step())
```

## Advanced Features

- **Custom Agents**: Extend `BaseAgent` to create specialized agents
- **Tool Integration**: Add new capabilities through the tool system
- **Storage Backends**: Built-in SQLite support, extensible to other databases
- **Tape Management**: Clone, branch, and analyze execution history
- **Validation**: Built-in parameter validation and error handling

## Documentation

For detailed information, check out:

- [Getting Started Guide](docs/getting_started.md)
- [Tape System Documentation](docs/tape_system.md)
- [Agent System Guide](docs/agents.md)

## Development

Clone and set up the development environment:

```bash
git clone https://github.com/yourusername/lightagent.git
cd lightagent
pip install -e ".[dev]"
```

Run tests:

```bash
pytest tests/ --cov=lightagent
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.