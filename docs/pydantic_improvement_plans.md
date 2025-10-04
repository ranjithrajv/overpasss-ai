# Pydantic and Mypy Integration Plans for Overpass QL Generator

## Overview
Pydantic and mypy can work together to significantly enhance the Overpass QL generator by providing both runtime data validation and static type checking, ensuring robust data handling and type safety throughout the application.

## Synergies Between Pydantic and Mypy

1. **Complementary Validation**: Pydantic provides runtime validation while mypy provides compile-time type checking
2. **Enhanced Type Safety**: Pydantic models can be annotated with mypy types for maximum safety
3. **Better Error Detection**: Combined approach catches both type errors and validation errors
4. **Improved Developer Experience**: IDEs can provide better autocomplete, error detection and refactoring support

## Specific Combined Use Cases

### 1. Input Validation with Natural Language Prompts
```python
from pydantic import BaseModel, field_validator
from typing import Literal, Optional

OutputFormat = Literal["json", "xml", "geojson"]

class UserPrompt(BaseModel):
    text: str
    location: Optional[str] = None
    output_format: OutputFormat = "json"
    
    @field_validator('text')
    def validate_prompt_length(cls, v: str) -> str:
        if len(v) < 5:
            raise ValueError('Prompt must be at least 5 characters long')
        return v
    
    @field_validator('output_format')
    def validate_output_format(cls, v: str) -> OutputFormat:
        allowed_formats: list[OutputFormat] = ['json', 'xml', 'geojson']
        format_lower = v.lower()
        if format_lower not in allowed_formats:
            raise ValueError(f'Output format must be one of {allowed_formats}')
        return format_lower  # type: ignore[return-value]
```

### 2. Enhanced OSM Tag Validation with TypedDict
```python
from pydantic import BaseModel, field_validator
from typing import TypedDict, Protocol
import requests

# Define the basic OSM element types
ElementType = Literal["node", "way", "relation"]

class OsmElement(TypedDict):
    type: ElementType
    id: int
    tags: dict[str, str]
    lat: Optional[float]
    lon: Optional[float]

class OsmTag(BaseModel):
    key: str
    value: str
    
    @field_validator('key')
    def validate_osm_key(cls, v: str) -> str:
        # Could integrate with taginfo API to validate against OSM schema
        # This is a simplified example
        if not v or len(v) > 255:
            raise ValueError('OSM key must not be empty and less than 256 chars')
        return v
    
    @field_validator('value')
    def validate_osm_value(cls, v: str) -> str:
        if len(v) > 255:
            raise ValueError('OSM value must be less than 256 chars')
        return v

class OsmTagValidator(Protocol):
    def validate_tag(self, key: str, value: str) -> bool: ...
    def get_valid_values(self, key: str) -> list[str]: ...

@dataclass
class QueryConstraint:
    tags: list[OsmTag]
    element_types: list[ElementType]  # e.g., ["node", "way"]
```

### 3. Query Structure Validation with Type Safety
```python
from pydantic import BaseModel, field_validator
from typing import List, Optional

class OverpassQuery(BaseModel):
    output_format: OutputFormat = "json"
    search_area: Optional[str] = None
    bounding_box: Optional[tuple[float, float, float, float]] = None  # (south, west, north, east)
    tags: list[OsmTag]
    elements: list[ElementType] = ["node", "way", "relation"]
    
    @field_validator('elements')
    def validate_elements(cls, v: list[str]) -> list[ElementType]:
        allowed_elements: list[ElementType] = ['node', 'way', 'relation']
        for element in v:
            if element not in allowed_elements:
                raise ValueError(f'Element must be one of {allowed_elements}')
        return v  # type: ignore[return-value]
```

### 4. Geographic Filter Validation with Strong Typing
```python
from pydantic import BaseModel, model_validator
from typing import Optional, NamedTuple

class BoundingBox(NamedTuple):
    south: float
    west: float
    north: float
    east: float
    
    def __post_init__(self) -> None:
        # mypy won't catch runtime validation, but we can document expected constraints
        assert self.south <= self.north, "South must be less than or equal to north"
        assert self.west <= self.east, "West must be less than or equal to east"

class GeographicFilter(BaseModel):
    area_name: Optional[str] = None
    bounding_box: Optional[BoundingBox] = None
    polygon: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_geographic_filter(self) -> 'GeographicFilter':
        # Ensure only one type of geographic filter is provided
        provided_filters = sum([
            self.area_name is not None,
            self.bounding_box is not None,
            self.polygon is not None
        ])
        
        if provided_filters == 0:
            raise ValueError("At least one geographic filter must be provided")
        if provided_filters > 1:
            raise ValueError("Only one geographic filter can be used at a time")
        
        if self.bounding_box:
            self.validate_bounding_box()
        
        return self
    
    def validate_bounding_box(self) -> None:
        if self.bounding_box:
            south, west, north, east = self.bounding_box
            if south >= north:
                raise ValueError("South latitude must be less than north latitude")
            if west >= east:
                raise ValueError("West longitude must be less than east longitude")
            # Additional validation for valid lat/lng ranges
            if not (-90 <= south <= 90 and -90 <= north <= 90):
                raise ValueError("Latitude must be between -90 and 90")
            if not (-180 <= west <= 180 and -180 <= east <= 180):
                raise ValueError("Longitude must be between -180 and 180")
```

### 5. API Response Types with TypedDict and Pydantic
```python
from pydantic import BaseModel
from typing import TypedDict, Any

class OverpassApiResponse(TypedDict):
    version: float
    generator: str
    osm3s: dict[str, str]  # timestamp info
    elements: list[OsmElement]

class OverpassResult(BaseModel):
    version: float
    generator: str
    elements: list[OsmElement]
    
    def get_elements_by_tag(self, key: str, value: str) -> list[OsmElement]:
        return [elem for elem in self.elements 
                if elem.get('tags', {}).get(key) == value]
```

### 6. Configuration and Settings with Type Safety
```python
from pydantic import BaseModel, Field
from typing import Optional

class OverpassApiConfig(BaseModel):
    base_url: str = Field(default="https://overpass-api.de/api/interpreter")
    timeout: int = Field(default=60, ge=1, le=300)
    max_size: int = Field(default=1000000, ge=1000)  # Max response size in bytes
    
    # Additional settings for query optimization
    query_timeout: int = Field(default=25, ge=5, le=120)
    bbox_threshold: float = Field(default=1.0, ge=0.01)  # Threshold to warn about large bbox queries

class GeneratorConfig(BaseModel):
    api_config: OverpassApiConfig
    output_format: OutputFormat = "json"
    validation_enabled: bool = True
    optimization_enabled: bool = True
```

### 7. Error Handling Types for Better Validation
```python
class OverpassQLError(Exception):
    """Base exception for Overpass QL related errors"""
    pass

class QuerySyntaxError(OverpassQLError):
    """Raised when generated query has syntax errors"""
    def __init__(self, query: str, error_position: int, message: str) -> None:
        self.query = query
        self.error_position = error_position
        self.message = message

class TagValidationError(OverpassQLError):
    """Raised when OSM tag validation fails"""
    def __init__(self, tag: OsmTag, reason: str) -> None:
        self.tag = tag
        self.reason = reason

class AreaResolutionError(OverpassQLError):
    """Raised when geographic area cannot be resolved"""
    def __init__(self, area_name: str) -> None:
        self.area_name = area_name
```

## Benefits of Combined Pydantic and Mypy Integration

1. **Enhanced Type Safety**: Both runtime validation (Pydantic) and compile-time checking (mypy)
2. **Early Error Detection**: Catch type errors during development and validation errors at runtime
3. **Code Documentation**: Type annotations and Pydantic models serve as comprehensive documentation
4. **Refactoring Safety**: Both tools ensure refactoring doesn't break contracts
5. **Developer Experience**: Better IDE support, autocomplete and error detection
6. **Maintainability**: Clean, self-documenting code with explicit data contracts and types
7. **Performance**: Fast validation with pydantic-core and early error catching with mypy
8. **Schema Compliance**: Ensures all generated queries comply with OSM schemas through combined validation

## Implementation Plan

1. **Phase 1**: Set up both Pydantic and mypy in the project with appropriate configuration files
2. **Phase 2**: Implement basic Pydantic models with mypy type annotations for input validation
3. **Phase 3**: Create typed models for OSM data structures and query components
4. **Phase 4**: Integrate validation layers into the query generation pipeline with strong typing
5. **Phase 5**: Add external validation (e.g., API calls to taginfo) within validators with mypy support
6. **Phase 6**: Implement configuration and settings validation with type safety
7. **Phase 7**: Add result validation for API responses with TypedDict structures
8. **Phase 8**: Integrate both tools into CI/CD pipeline and set up pre-commit hooks

## Example Combined Integration in the Generator

```python
from pydantic import ValidationError
from typing import Callable

def generate_overpass_ql(user_input: str) -> str:
    try:
        # Parse user input into validated model (with mypy type checking)
        parsed_input: UserPrompt = UserPrompt(text=user_input)
        
        # Process the validated input to create query components
        query_components: dict[str, Any] = extract_query_components(parsed_input.text)
        
        # Validate geographic filter
        geo_filter: GeographicFilter
        if 'location' in query_components:
            geo_filter = GeographicFilter(area_name=query_components.get('location'))
        else:
            geo_filter = GeographicFilter()
        
        # Validate OSM tags
        tags: list[OsmTag] = [
            OsmTag(key=k, value=v) 
            for k, v in query_components.get('tags', {}).items()
        ]
        
        # Construct and validate the final query
        query: OverpassQuery = OverpassQuery(
            search_area=geo_filter.area_name,
            tags=tags,
            output_format=parsed_input.output_format
        )
        
        # Generate the actual Overpass QL string
        ql_query: str = construct_query_string(query)
        
        # Validate the final query string syntax
        validate_query_syntax(ql_query)
        
        return ql_query
        
    except ValidationError as e:
        raise ValueError(f"Invalid input: {e}")
```

## Mypy Configuration for This Project

The project should use strict typing settings to catch as many errors as possible, while allowing pragmatic exceptions where needed:

```ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
warn_redundant_casts = True
warn_unused_ignores = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
namespace_packages = True
explicit_package_bases = True

# For third-party libraries that don't have stubs
[mypy-generator.*]
# Add specific ignores for third-party imports if needed

[mypy-tests.*]
# Tests can be less strict
disallow_untyped_defs = False
```