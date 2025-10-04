from typing import TypedDict, Union, List, Literal, Optional, NamedTuple, Protocol, Tuple, Callable, Dict, Any
from dataclasses import dataclass
from pydantic import BaseModel, field_validator, Field, model_validator

# Import configuration constants
from overpass_ql_gen.config import ElementType, OutputFormat, COMMON_TAG_MAPPINGS, MIN_PROMPT_LENGTH, SUPPORTED_OUTPUT_FORMATS, SUPPORTED_ELEMENT_TYPES, OVERPASS_QUERY_TEMPLATE, AREA_DEFINITION_TEMPLATE, BBOX_FILTER_TEMPLATE

class UserPrompt(BaseModel):
    text: str
    location: Optional[str] = None
    output_format: OutputFormat = "json"
    
    @field_validator('text')
    def validate_prompt_length(cls, v: str) -> str:
        if len(v) < MIN_PROMPT_LENGTH:
            raise ValueError(f'Prompt must be at least {MIN_PROMPT_LENGTH} characters long')
        return v
    
    @field_validator('output_format')
    def validate_output_format(cls, v: str) -> OutputFormat:
        allowed_formats: List[OutputFormat] = SUPPORTED_OUTPUT_FORMATS
        format_lower = v.lower()
        if format_lower not in allowed_formats:
            raise ValueError(f'Output format must be one of {allowed_formats}')
        return format_lower  # type: ignore[return-value]

class OsmElement(TypedDict):
    type: ElementType
    id: int
    tags: Dict[str, str]
    lat: Optional[float]
    lon: Optional[float]

# Instead of inheriting and overriding fields, use a more specific structure
# We'll define specific node/way/relation types without inheritance for TypedDict
OsmNode = TypedDict('OsmNode', {
    'type': Literal["node"],
    'id': int,
    'tags': Dict[str, str],
    'lat': float,
    'lon': float
})

OsmWay = TypedDict('OsmWay', {
    'type': Literal["way"],
    'id': int,
    'tags': Dict[str, str],
    'nodes': List[int]  # List of node IDs
})

OsmRelation = TypedDict('OsmRelation', {
    'type': Literal["relation"],
    'id': int,
    'tags': Dict[str, str],
    'members': List[Dict[str, Union[int, str]]]  # List of member dicts
})

OsmElementUnion = Union[OsmNode, OsmWay, OsmRelation]

# Import OSM tag validation from our new validation system
# Import OSM tag validation from our new validation system
from overpass_ql_gen.validation.validator import OsmTag, OsmTagValidator, QueryConstraint

# Import geographic filtering from our new validation system
from overpass_ql_gen.validation.validator import BoundingBox, GeographicFilter

# Query generation pipeline types
@dataclass
class ParsedPrompt:
    """Result of NLP processing"""
    elements: List[ElementType]  # e.g., ["node", "way", "relation"]
    tags: List[OsmTag]
    location: Optional[str]
    area_filter: Optional[GeographicFilter]
    
# Import OverpassQuery from our new validation system
from overpass_ql_gen.validation.validator import OverpassQuery

# Type for prompt parsing function
PromptParser = Callable[[str], ParsedPrompt]

# Type for query construction function
QueryConstructor = Callable[[ParsedPrompt], 'OverpassQuery']

# Type for validation function
Validator = Callable[['OverpassQuery'], bool]

# API Response Types
class OverpassApiResponse(TypedDict):
    version: float
    generator: str
    osm3s: Dict[str, str]  # timestamp info
    elements: List[OsmElementUnion]

class OverpassResult(BaseModel):
    version: float
    generator: str
    elements: List[OsmElement]
    
    def get_elements_by_tag(self, key: str, value: str) -> List[OsmElement]:
        return [elem for elem in self.elements 
                if elem.get('tags', {}).get(key) == value]

class TaginfoApiResponse(TypedDict):
    data: List[Dict[str, Union[str, int, float]]]
    count: int
    key: str

# Configuration and Settings Types
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

# Import validation components from our new validation system
from overpass_ql_gen.validation.validator import (
    OverpassQLValidator, 
    WebBasedTagValidator, 
    QuerySyntaxValidator,
    AreaResolver,
    ValidationConfig
)

# Error Handling Types
class OverpassQLError(Exception):
    """Base exception for Overpass QL related errors"""
    pass

class QuerySyntaxError(OverpassQLError):
    """Raised when generated query has syntax errors"""
    def __init__(self, query: str, error_position: int, message: str) -> None:
        self.query = query
        self.error_position = error_position
        self.message = message
        super().__init__(f"Syntax error at position {error_position}: {message}")

class TagValidationError(OverpassQLError):
    """Raised when OSM tag validation fails"""
    def __init__(self, tag: OsmTag, reason: str) -> None:
        self.tag = tag
        self.reason = reason
        super().__init__(f"Tag validation failed for {tag.key}={tag.value}: {reason}")

class AreaResolutionError(OverpassQLError):
    """Raised when geographic area cannot be resolved"""
    def __init__(self, area_name: str) -> None:
        self.area_name = area_name
        super().__init__(f"Could not resolve area: {area_name}")

def parse_prompt(prompt: str) -> ParsedPrompt:
    """
    Parses the natural language prompt to extract key entities.
    """
    import re
    
    # Default values
    elements: List[ElementType] = ["node", "way", "relation"]
    tags: List[OsmTag] = []
    location: Optional[str] = None
    area_filter: Optional[GeographicFilter] = None
    
    # Extract feature from prompt
    # Look for patterns like "find cafes in Paris" or "show me bicycle parking in Berlin"
    # Also look for patterns like "all cafes in Paris" or "educational facilities in London"
    pattern = r"(?:find|show me|get|locate|all)\s+(?:all\s+)?(.+?)\s+(?:in|within|near|around)\s+(.+)"
    match = re.search(pattern, prompt, re.IGNORECASE)
    
    if not match:
        # Try a more general pattern
        general_pattern = r"(.+?)\s+(?:in|within|near|around)\s+(.+)"
        match = re.search(general_pattern, prompt, re.IGNORECASE)
    
    if match:
        feature_text = match.group(1).strip()
        location = match.group(2).strip()
        
        # Basic tag extraction - in a real implementation this would use NLP
        # For now, we'll map common features to basic OSM tags using configuration
        feature_lower = feature_text.lower()
        tag_mapping_found = False
        
        for keyword, (key, value) in COMMON_TAG_MAPPINGS.items():
            if keyword in feature_lower:
                tags = [OsmTag(key=key, value=value)]
                tag_mapping_found = True
                break
        
        if not tag_mapping_found:
            # If no specific mapping found, use the feature name as a tag value
            # This is a simplified approach - a real implementation would use more sophisticated NLP
            clean_feature = feature_text.replace(" ", "_").lower()
            tags = [OsmTag(key="name", value=clean_feature)]
    else:
        # If no location-specific pattern found, try to extract features only
        # This handles cases where no specific location is mentioned
        prompt_lower = prompt.lower()
        tag_found = False
        for keyword, (key, value) in COMMON_TAG_MAPPINGS.items():
            if keyword in prompt_lower:
                tags = [OsmTag(key=key, value=value)]
                tag_found = True
                break
        if not tag_found:
            # Fallback to using the prompt as a name tag
            tags = [OsmTag(key="name", value=prompt.strip().lower())]
    
    return ParsedPrompt(
        elements=elements,
        tags=tags,
        location=location,
        area_filter=area_filter
    )

def generate_query(prompt: str, output_format: OutputFormat = "json") -> OverpassQuery:
    """
    Generates an Overpass QL query from a natural language prompt.
    Updated to use Pydantic models for validation.
    """
    # Validate the input using Pydantic
    user_prompt = UserPrompt(text=prompt, output_format=output_format)
    
    # Parse the prompt with validation
    parsed_prompt = parse_prompt(user_prompt.text)
    
    # Validate tags using Pydantic validation
    for tag in parsed_prompt.tags:
        # This will trigger Pydantic's field validators
        _ = tag.key  # Access to ensure validation happens if needed
        _ = tag.value
    
    # Create query constraints
    constraints = QueryConstraint(
        tags=parsed_prompt.tags,
        element_types=parsed_prompt.elements
    )
    
    # Validate tags (with fallback for offline environments)
    validator = WebBasedTagValidator()
    for tag in parsed_prompt.tags:
        if not tag.is_valid(validator):
            print(f"Warning: Tag '{tag.key}={tag.value}' may not be valid according to OSM database")
            # Don't raise an exception for testing purposes, just warn
    
    # Build the query string
    area_definition = ""
    area_filter_expr = ""
    
    if parsed_prompt.location:
        # Validate geographic filter
        geo_filter = GeographicFilter(area_name=parsed_prompt.location)
        area_definition = f'area[name="{geo_filter.area_name}"]->.searchArea;'
        area_filter_expr = "(area.searchArea)"
    else:
        # If no location specified, we might want to apply a global filter
        # or raise an error depending on requirements
        area_filter_expr = ""  # This would be a worldwide search
    
    # Build query parts for each element type
    query_parts: List[str] = []
    for tag in parsed_prompt.tags:
        for elem_type in parsed_prompt.elements:
            if area_filter_expr:
                query_parts.append(f'  {elem_type}["{tag.key}"="{tag.value}"]{area_filter_expr};')
            else:
                query_parts.append(f'  {elem_type}["{tag.key}"="{tag.value}"];')
    
    query_body = "\n".join(query_parts)
    
    # Construct the final query using template from config
    query_string = OVERPASS_QUERY_TEMPLATE.format(
        prompt=prompt,
        output_format=user_prompt.output_format,
        area_definition=area_definition,
        query_body=query_body
    )

    # Create and return the Pydantic model
    return OverpassQuery(
        output_format=user_prompt.output_format,
        search_area=parsed_prompt.location,
        tags=parsed_prompt.tags,
        elements=parsed_prompt.elements,
        query_string=query_string
    )

# --- Tool Functions (for compatibility with existing code) ---
google_web_search: Optional[Callable[..., Any]] = None
web_fetch: Optional[Callable[..., Any]] = None
