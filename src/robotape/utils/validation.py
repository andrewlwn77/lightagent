from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

T = TypeVar('T', bound=BaseModel)

def validate_model(data: Any, model_class: Type[T]) -> tuple[Optional[T], Optional[Dict[str, str]]]:
    """Validate data against a Pydantic model."""
    try:
        instance = model_class.model_validate(data)
        return instance, None
    except ValidationError as e:
        errors = {
            f"{'.'.join(map(str, error['loc']))}": error['msg']
            for error in e.errors()
        }
        return None, errors

def validate_step_content(content: Any, validators: Dict[str, Type[BaseModel]]) -> Dict[str, Any]:
    """Validate step content using appropriate validator."""
    if not isinstance(content, dict) or 'type' not in content:
        return {'error': 'Invalid content format'}
    
    content_type = content.get('type')
    validator = validators.get(content_type)
    
    if not validator:
        return {'error': f'No validator for type: {content_type}'}
    
    try:
        validated = validator.model_validate(content)
        return validated.model_dump()
    except ValidationError as e:
        return {'error': str(e)}

class Cache:
    """Simple cache for validation results."""
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, Any] = {}
        self._max_size = max_size

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        if len(self._cache) >= self._max_size:
            # Simple FIFO eviction
            self._cache.pop(next(iter(self._cache)))
        self._cache[key] = value