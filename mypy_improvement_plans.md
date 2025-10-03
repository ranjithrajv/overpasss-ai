# Mypy Integration Plans for Overpass QL Generator

## Overview
Mypy can significantly improve the Overpass QL generator by providing static type checking, ensuring type safety throughout the application, and catching potential runtime errors during development.

## Specific Mypy Use Cases

### 1. OSM Data Model Types
Define precise types for the OSM data hierarchy to ensure type safety when processing OSM elements:

```python
from typing import TypedDict, Union, List, Literal, Optional
from dataclasses import dataclass

# Define the basic OSM element types
ElementType = Literal["node", "way", "relation"]

class OsmElement(TypedDict):
    type: ElementType
    id: int
    tags: dict[str, str]
    lat: Optional[float]
    lon: Optional[float]

class OsmNode(OsmElement):
    type: Literal["node"]
    lat: float
    lon: float

class OsmWay(OsmElement):
    type: Literal["way"]
    nodes: List[int]  # List of node IDs

class OsmRelation(OsmElement):
    type: Literal["relation"]
    members: List[dict[str, Union[int, str]]]  # List of member dicts

OsmElementUnion = Union[OsmNode, OsmWay, OsmRelation]
```

### 2. Tag Validation Types
Create types for handling OSM tag validation and schema compliance:

```python
from typing import Protocol

class OsmTagValidator(Protocol):
    def validate_tag(self, key: str, value: str) -> bool: ...
    def get_valid_values(self, key: str) -> List[str]: ...

@dataclass
class OsmTag:
    key: str
    value: str
    
    def is_valid(self, validator: OsmTagValidator) -> bool:
        return validator.validate_tag(self.key, self.value)

@dataclass
class QueryConstraint:
    tags: List[OsmTag]
    element_types: List[ElementType]  # e.g., ["node", "way"]
```

### 3. Geographic Filtering Types
Define types for various geographic filters and bounding boxes:

```python
from typing import NamedTuple

class BoundingBox(NamedTuple):
    south: float
    west: float
    north: float
    east: float
    
    def __post_init__(self) -> None:
        # mypy won't catch runtime validation, but we can document expected constraints
        assert self.south <= self.north, "South must be less than or equal to north"
        assert self.west <= self.east, "West must be less than or equal to east"

class GeographicFilter:
    area_name: Optional[str]
    bounding_box: Optional[BoundingBox]
    polygon_coords: Optional[List[Tuple[float, float]]]
    
    def get_filter_expression(self) -> str:
        # Implementation here
        ...
```

### 4. Query Generation Pipeline Types
Type the entire query generation pipeline to ensure data flows correctly:

```python
from typing import Callable, Awaitable

class ParsedPrompt:
    """Result of NLP processing"""
    elements: List[str]  # e.g., ["node", "way", "relation"]
    tags: List[OsmTag]
    location: Optional[str]
    area_filter: Optional[GeographicFilter]
    
class OverpassQuery:
    query_string: str
    constraints: QueryConstraint
    
    def execute(self) -> List[OsmElementUnion]:
        # Execute query against Overpass API
        ...

# Type for prompt parsing function
PromptParser = Callable[[str], ParsedPrompt]

# Type for query construction function
QueryConstructor = Callable[[ParsedPrompt], OverpassQuery]

# Type for validation function
Validator = Callable[[OverpassQuery], bool]
```

### 5. API Response Types
Define types for Overpass API responses to ensure safe data access:

```python
class OverpassApiResponse(TypedDict):
    version: float
    generator: str
    osm3s: dict[str, str]  # timestamp info
    elements: List[OsmElementUnion]

class TaginfoApiResponse(TypedDict):
    data: List[dict[str, Union[str, int, float]]]
    count: int
    key: str
```

### 6. Configuration and Settings Types
Type-safe configuration management:

```python
@dataclass
class OverpassApiConfig:
    base_url: str = "https://overpass-api.de/api/interpreter"
    timeout: int = 60
    max_size: int = 1000000
    
@dataclass
class GeneratorConfig:
    api_config: OverpassApiConfig
    output_format: Literal["json", "xml", "geojson"] = "json"
    validation_enabled: bool = True
    optimization_enabled: bool = True
```

### 7. Error Handling Types
Create specific exception types to improve error handling:

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

## Integration Plan

### Phase 1: Setup and Basic Configuration
1. Add mypy to the project dependencies in `pyproject.toml`
2. Create a `mypy.ini` or `pyproject.toml` configuration with appropriate settings
3. Start with basic type annotations in core modules

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
```

### Phase 2: Core Model Typing
1. Define types for OSM data models (nodes, ways, relations)
2. Create types for tags, constraints, and geographic filters
3. Add types to the query generation pipeline

### Phase 3: API Integration Typing
1. Add types for API responses
2. Type the API client functions
3. Add types for validation functions

### Phase 4: Advanced Typing
1. Use generics where appropriate
2. Add protocol types for interfaces
3. Apply type narrowing techniques
4. Add overload signatures for functions with different return types

### Phase 5: Testing Integration
1. Update test files with type annotations
2. Use mypy in CI/CD pipeline
3. Set up pre-commit hooks for type checking

## Benefits of Mypy Integration

1. **Early Error Detection**: Catch type-related errors during development
2. **Code Documentation**: Type annotations serve as documentation
3. **Refactoring Safety**: Type checker ensures refactoring doesn't break contracts
4. **Developer Experience**: IDEs can provide better autocomplete and error detection
5. **Code Quality**: Enforces consistent data structures and interfaces
6. **API Reliability**: Ensures correct handling of API responses

## Example Typed Function

```python
from typing import List, Optional

def generate_overpass_query(
    prompt: str,
    location: Optional[str] = None,
    tags: Optional[List[OsmTag]] = None,
    element_types: List[ElementType] = ["node", "way", "relation"],
    output_format: Literal["json", "xml", "geojson"] = "json"
) -> OverpassQuery:
    """
    Generate an Overpass QL query based on the natural language prompt.
    
    Args:
        prompt: Natural language description of what to query
        location: Optional location constraint
        tags: Optional list of tag constraints
        element_types: Types of OSM elements to include
        output_format: Desired output format
    
    Returns:
        A valid OverpassQuery object
    
    Raises:
        QuerySyntaxError: If the generated query has syntax errors
        TagValidationError: If provided tags are invalid
    """
    if not prompt or len(prompt.strip()) < 5:
        raise ValueError("Prompt must be at least 5 characters long")
    
    # Implementation here
    ...
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

# For third-party libraries that don't have stubs
[mypy-generator.*]
# Add specific ignores for third-party imports if needed

[mypy-tests.*]
# Tests can be less strict
disallow_untyped_defs = False
```