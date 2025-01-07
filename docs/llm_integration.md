# LLM Integration

The Lightweight Agent Framework provides built-in support for **Large Language Models (LLMs)**, enabling agents to leverage advanced natural language processing capabilities. This section covers:

1. **LLMConfig**: Configuration for LLM providers.
2. **create_llm**: Factory function for creating LLM clients.
3. **LLMAwareAgent**: An agent that integrates with LLMs.
4. **Supported LLM Providers**: OpenAI, Anthropic, and HuggingFace.
5. **Custom LLM Providers**: How to add support for new LLM providers.

---

## **LLMConfig**

The `LLMConfig` class is used to configure the LLM provider, model, and other parameters.

### **Parameters**

| Parameter           | Description                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| `model`             | The model to use (e.g., `gpt-4`, `claude-3-sonnet-20240229`).               |
| `api_key`           | The API key for the LLM provider.                                           |
| `temperature`       | Controls the creativity of the model (default: `0.7`).                      |
| `max_tokens`        | The maximum number of tokens to generate (optional).                        |
| `additional_params` | Provider-specific parameters (e.g., `presence_penalty` for OpenAI).         |
| `provider_name`     | The name of the LLM provider (e.g., `openai`, `anthropic`, `huggingface`).  |

### **Example**

```python
from robotape.llm import LLMConfig

# Configure the LLM
llm_config = LLMConfig(
    model="gpt-4",
    api_key="your-api-key",
    provider_name="openai",
    temperature=0.5,
    max_tokens=100,
    additional_params={"presence_penalty": 0.5}
)
```

---

## **create_llm**

The `create_llm` factory function is used to instantiate LLM clients for different providers. It supports OpenAI, Anthropic, and HuggingFace out of the box.

### **Example**

```python
from robotape.llm import LLMConfig, create_llm

# Configure the LLM
llm_config = LLMConfig(
    model="gpt-4",
    api_key="your-api-key",
    provider_name="openai"
)

# Create an LLM client
llm = create_llm(llm_config)
```

---

## **LLMAwareAgent**

The `LLMAwareAgent` is a specialized agent that integrates with LLMs. It uses the `LLMConfig` class to configure the LLM and provides methods for generating text and processing responses.

### **Example Usage**

```python
from robotape.agents.llm import LLMAwareAgent
from robotape.llm import LLMConfig

# Configure the LLM
llm_config = LLMConfig(
    model="gpt-4",
    api_key="your-api-key",
    provider_name="openai"
)

# Create an LLMAwareAgent
agent = LLMAwareAgent("llm_agent", llm_config)

# Execute the agent
async def run_llm_agent():
    context = {"task": "Write a summary of the meeting"}
    result = await agent.think(context)
    print(f"LLM Response: {result.output}")

# Run the agent
import asyncio
asyncio.run(run_llm_agent())
```

---

## **Supported LLM Providers**

The framework supports the following LLM providers:

1. **OpenAI**:
   - Provider Name: `openai`
   - Example Model: `gpt-4`
   - Additional Parameters: `presence_penalty`, `frequency_penalty`, etc.

2. **Anthropic**:
   - Provider Name: `anthropic`
   - Example Model: `claude-3-sonnet-20240229`
   - Additional Parameters: `max_tokens`, `temperature`, etc.

3. **HuggingFace**:
   - Provider Name: `huggingface`
   - Example Model: `meta-llama/Llama-2-70b-chat-hf`
   - Additional Parameters: `base_url`, `temperature`, etc.

---

## **Custom LLM Providers**

You can add support for new LLM providers by extending the `BaseLLM` class and registering the provider with the `create_llm` factory function.

### **Example: Adding a Custom LLM Provider**

```python
from robotape.llm import BaseLLM, LLMConfig, LLMResponse

class CustomLLM(BaseLLM):
    def __init__(self, config: LLMConfig):
        super().__init__(config)
        # Initialize the custom LLM client here
    
    async def generate(self, prompt: str) -> LLMResponse:
        """Generate text using the custom LLM."""
        # Implement the logic to call the custom LLM
        response = await self._call_custom_llm(prompt)
        return LLMResponse(
            text=response.text,
            raw_response=response.raw_data,
            usage=response.usage,
            model=self.config.model
        )
    
    async def close(self):
        """Clean up resources."""
        pass

# Register the custom provider
from robotape.llm import create_llm

def register_custom_provider():
    create_llm.register_provider("custom", CustomLLM)

# Now you can use the custom provider
llm_config = LLMConfig(
    model="custom-model",
    api_key="your-api-key",
    provider_name="custom"
)
llm = create_llm(llm_config)
```

---

## **Next Steps**

Now that you’ve learned about **LLM Integration**, here are some next steps:
- Explore the **Tool System** to extend your agents with reusable functions.
- Dive into the **Tape System** to record and analyze agent execution history.
- Learn about **MCP (Multi-Component Processing)** for building complex workflows.
