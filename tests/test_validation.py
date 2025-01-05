from robotape.utils.validation import validate_model, validate_step_content, Cache
from pydantic import BaseModel
from typing import Optional

class TestModel(BaseModel):
    name: str
    value: Optional[int] = None

def test_validate_model():
    """Test model validation."""
    # Valid data
    data = {"name": "test", "value": 42}
    instance, errors = validate_model(data, TestModel)
    assert instance is not None
    assert errors is None
    assert instance.name == "test"
    
    # Invalid data
    data = {"value": "not an int"}
    instance, errors = validate_model(data, TestModel)
    assert instance is None
    assert errors is not None
    assert "name" in str(errors)

def test_validate_step_content():
    """Test step content validation."""
    validators = {
        "test": TestModel
    }
    
    # Valid content
    content = {
        "type": "test",
        "name": "test",
        "value": 42
    }
    result = validate_step_content(content, validators)
    assert "error" not in result
    assert result["name"] == "test"
    
    # Invalid content
    content = {
        "type": "unknown"
    }
    result = validate_step_content(content, validators)
    assert "error" in result

def test_cache():
    """Test cache functionality."""
    cache = Cache(max_size=2)
    
    # Add items
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"
    
    # Test max size
    cache.set("key3", "value3")  # Should evict key1
    assert cache.get("key1") is None
    assert cache.get("key3") == "value3"