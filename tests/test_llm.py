"""Tests for LLM integrations"""

import pytest
import logging
from unittest.mock import patch, AsyncMock, MagicMock
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from robotape.llm import (
    LLMConfig, 
    LLMResponse,
    AnthropicLLM,
    OpenAILLM,
    HuggingFaceLLM
)
from robotape.agents.llm import LLMAwareAgent
from robotape.models.steps import StepResult

# Configure logging for debugging
logging.basicConfig(level=logging.DEBUG)

# Define Pydantic models for the mock response
class MockMessage(BaseModel):
    content: str
    role: str
    tool_calls: Optional[List[Dict[str, Any]]] = None  # Add tool_calls attribute

class MockChoice(BaseModel):
    message: MockMessage
    finish_reason: str

class MockUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class MockCompletion(BaseModel):
    id: str
    choices: List[MockChoice]
    created: int
    model: str
    usage: MockUsage

# Mock the CompletionUsage and related classes
class CompletionTokensDetails(BaseModel):
    accepted_prediction_tokens: Optional[int] = None
    audio_tokens: Optional[int] = None
    reasoning_tokens: Optional[int] = None
    rejected_prediction_tokens: Optional[int] = None

class PromptTokensDetails(BaseModel):
    audio_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None

class CompletionUsage(BaseModel):
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int
    completion_tokens_details: Optional[CompletionTokensDetails] = None
    prompt_tokens_details: Optional[PromptTokensDetails] = None

@pytest.fixture
def anthropic_config():
    return LLMConfig(
        model="claude-3-sonnet-20240229",
        api_key="test_key",
        provider_name="anthropic"
    )

@pytest.fixture
def openai_config():
    return LLMConfig(
        model="gpt-4",
        api_key="test_key",
        provider_name="openai"
    )

@pytest.fixture
def huggingface_config():
    return LLMConfig(
        model="meta-llama/Llama-2-70b-chat-hf",
        api_key="test_key",
        provider_name="huggingface"
    )

@pytest.fixture
def mock_anthropic_client():
    client = AsyncMock()
    messages_mock = AsyncMock()
    messages_mock.create = AsyncMock()
    client.messages = messages_mock
    return client

@pytest.fixture
def mock_openai_client():
    client = AsyncMock()
    completions = AsyncMock()
    completions.create = AsyncMock()
    chat = AsyncMock()
    chat.completions = completions
    client.chat = chat
    return client

@pytest.mark.asyncio
async def test_anthropic_llm(anthropic_config, mock_anthropic_client):
    # Mock the Anthropic response
    mock_response = {
        "id": "test-id",
        "content": [{"text": "Test response", "type": "text"}],
        "model": anthropic_config.model,
        "role": "assistant",
        "usage": {"input_tokens": 1, "output_tokens": 1},
        "type": "message"  # Add this field
    }

    # Mock the Anthropic client's `messages.create` method
    mock_anthropic_client.messages.create.return_value = mock_response

    # Create the AnthropicLLM instance with the mocked client
    llm = AnthropicLLM(anthropic_config, client=mock_anthropic_client)

    # Call the generate method
    response = await llm.generate("Test prompt")

    # Assertions
    assert isinstance(response, LLMResponse)
    assert response.text == "Test response"
    assert response.model == anthropic_config.model

@pytest.mark.asyncio
async def test_openai_llm(openai_config, mock_openai_client):
    # Mock the OpenAI response using Pydantic models
    mock_usage = MockUsage(
        prompt_tokens=1,
        completion_tokens=1,
        total_tokens=2
    )

    mock_response = MockCompletion(
        id="test-id",
        choices=[MockChoice(message=MockMessage(content="Test response", role="assistant", tool_calls=[]), finish_reason="stop")],
        created=1234567890,
        model=openai_config.model,
        usage=mock_usage
    )

    # Mock the OpenAI client's `chat.completions.create` method
    mock_openai_client.chat.completions.create.return_value = mock_response

    # Create the OpenAILLM instance with the mocked client
    llm = OpenAILLM(openai_config, client=mock_openai_client)

    # Call the generate method
    response = await llm.generate("Test prompt")

    # Assertions
    assert isinstance(response, LLMResponse)
    assert response.text == "Test response"
    assert response.model == openai_config.model

@pytest.mark.asyncio
async def test_huggingface_llm(huggingface_config, mock_openai_client):
    # Mock the HuggingFace response using Pydantic models
    mock_usage = MockUsage(
        prompt_tokens=1,
        completion_tokens=1,
        total_tokens=2
    )

    mock_response = MockCompletion(
        id="test-id",
        choices=[MockChoice(message=MockMessage(content="Test response", role="assistant", tool_calls=[]), finish_reason="stop")],
        created=1234567890,
        model=huggingface_config.model,
        usage=mock_usage
    )

    # Mock the OpenAI client's `chat.completions.create` method
    mock_openai_client.chat.completions.create.return_value = mock_response

    # Create the HuggingFaceLLM instance with the mocked client
    llm = HuggingFaceLLM(huggingface_config, client=mock_openai_client)

    # Call the generate method
    response = await llm.generate("Test prompt")

    # Assertions
    assert isinstance(response, LLMResponse)
    assert response.text == "Test response"
    assert response.model == huggingface_config.model

@pytest.mark.asyncio
async def test_llm_aware_agent(mock_openai_client):
    config = LLMConfig(
        model="test-model",
        api_key="test_key",
        provider_name="openai"
    )

    # Mock the OpenAI response using Pydantic models
    mock_usage = MockUsage(
        prompt_tokens=1,
        completion_tokens=1,
        total_tokens=2
    )

    mock_response = MockCompletion(
        id="test-id",
        choices=[MockChoice(message=MockMessage(content="Test response", role="assistant", tool_calls=[]), finish_reason="stop")],
        created=1234567890,
        model=config.model,
        usage=mock_usage
    )

    # Mock the OpenAI client's `chat.completions.create` method
    mock_openai_client.chat.completions.create.return_value = mock_response

    # Create the LLMAwareAgent instance with the mocked client
    agent = LLMAwareAgent("test_agent", config)
    agent.llm.client = mock_openai_client

    # Call the think method
    result = await agent.think({"test": "data"})

    # Assertions
    assert isinstance(result, StepResult)
    assert result.success

@pytest.mark.asyncio
async def test_provider_specific_features(mock_openai_client):
    openai_config = LLMConfig(
        model="gpt-4",
        api_key="test_key",
        provider_name="openai",
        additional_params={"presence_penalty": 0.5}
    )

    # Mock the OpenAI response using Pydantic models
    mock_usage = MockUsage(
        prompt_tokens=1,
        completion_tokens=1,
        total_tokens=2
    )

    mock_response = MockCompletion(
        id="test-id",
        choices=[MockChoice(message=MockMessage(content="Test response", role="assistant", tool_calls=[]), finish_reason="stop")],
        created=1234567890,
        model=openai_config.model,
        usage=mock_usage
    )

    # Mock the OpenAI client's `chat.completions.create` method
    mock_openai_client.chat.completions.create.return_value = mock_response

    # Create the OpenAILLM instance with the mocked client
    llm = OpenAILLM(openai_config, client=mock_openai_client)

    # Call the generate method
    response = await llm.generate("Test prompt")

    # Assertions
    assert response.text == "Test response"
    assert 'presence_penalty' in openai_config.additional_params
    assert openai_config.additional_params['presence_penalty'] == 0.5