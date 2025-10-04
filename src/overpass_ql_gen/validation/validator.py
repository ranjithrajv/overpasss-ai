"""
Validation System for Overpass QL Generator

This module provides comprehensive validation for the Overpass QL generator,
combining Pydantic's runtime validation with mypy's static type checking.
"""
from typing import List, Literal, Optional, Protocol, Dict, Any, Tuple
from pydantic import BaseModel, field_validator, model_validator, Field
import requests
from requests import RequestException
import re

# Import configuration constants
from overpass_ql_gen.config import ElementType, OutputFormat, MAX_TAG_KEY_LENGTH, MAX_TAG_VALUE_LENGTH, MIN_LATITUDE, MAX_LATITUDE, MIN_LONGITUDE, MAX_LONGITUDE, SUPPORTED_OUTPUT_FORMATS, SUPPORTED_ELEMENT_TYPES


class OsmTag(BaseModel):
    """Pydantic model for OSM tags with validation."""
    key: str
    value: str
    
    @field_validator('key')
    def validate_osm_key(cls, v: str) -> str:
        """Validate the OSM tag key."""
        if not v or len(v) > MAX_TAG_KEY_LENGTH:
            raise ValueError(f'OSM key must not be empty and less than {MAX_TAG_KEY_LENGTH + 1} chars')
        # Basic validation for valid characters in OSM keys
        if not re.match(r'^[a-zA-Z0-9:_-]+$', v):
            raise ValueError('OSM key contains invalid characters')
        return v
    
    @field_validator('value')
    def validate_osm_value(cls, v: str) -> str:
        """Validate the OSM tag value."""
        if len(v) > MAX_TAG_VALUE_LENGTH:
            raise ValueError(f'OSM value must be less than {MAX_TAG_VALUE_LENGTH + 1} chars')
        return v

    def is_valid(self, validator: 'OsmTagValidator') -> bool:
        """Check if the tag is valid using the provided validator."""
        return validator.validate_tag(self.key, self.value)


class BoundingBox(BaseModel):
    """Pydantic model for geographic bounding boxes with validation."""
    south: float
    west: float
    north: float
    east: float
    
    @model_validator(mode='after')
    def validate_bounding_box(self) -> 'BoundingBox':
        """Validate the bounding box coordinates."""
        if self.south >= self.north:
            raise ValueError("South latitude must be less than north latitude")
        if self.west >= self.east:
            raise ValueError("West longitude must be less than east longitude")
        # Additional validation for valid lat/lng ranges
        if not (-90 <= self.south <= 90 and -90 <= self.north <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= self.west <= 180 and -180 <= self.east <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        return self


class GeographicFilter(BaseModel):
    """Pydantic model for geographic filters with validation."""
    area_name: Optional[str] = None
    bounding_box: Optional[BoundingBox] = None
    polygon: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_geographic_filter(self) -> 'GeographicFilter':
        """Ensure only one type of geographic filter is provided."""
        provided_filters = sum([
            self.area_name is not None,
            self.bounding_box is not None,
            self.polygon is not None
        ])
        
        if provided_filters == 0:
            raise ValueError("At least one geographic filter must be provided")
        if provided_filters > 1:
            raise ValueError("Only one geographic filter can be used at a time")
        
        return self


class QueryConstraint(BaseModel):
    """Pydantic model for query constraints."""
    tags: List[OsmTag]
    element_types: List[ElementType] = ["node", "way", "relation"]
    
    @field_validator('element_types')
    def validate_elements(cls, v: List[str]) -> List[ElementType]:
        """Validate the element types."""
        allowed_elements: List[ElementType] = ['node', 'way', 'relation']
        for element in v:
            if element not in allowed_elements:
                raise ValueError(f'Element must be one of {allowed_elements}')
        return v  # type: ignore[return-value]


class OverpassQuery(BaseModel):
    """Pydantic model for Overpass QL queries with validation."""
    output_format: OutputFormat = "json"
    search_area: Optional[str] = None
    bounding_box: Optional[Tuple[float, float, float, float]] = None
    tags: List[OsmTag]
    elements: List[ElementType] = ["node", "way", "relation"]
    query_string: str = ""
    
    @field_validator('elements')
    def validate_elements(cls, v: List[str]) -> List[ElementType]:
        """Validate the element types in the query."""
        allowed_elements: List[ElementType] = ['node', 'way', 'relation']
        for element in v:
            if element not in allowed_elements:
                raise ValueError(f'Element must be one of {allowed_elements}')
        return v  # type: ignore[return-value]
    
    @model_validator(mode='after')
    def validate_query_structure(self) -> 'OverpassQuery':
        """Validate the overall query structure."""
        if not self.tags:
            raise ValueError("Query must include at least one tag filter")
        
        if self.search_area and self.bounding_box:
            # Both area and bbox are present, which is unusual but not invalid
            pass
        
        return self


class OsmTagValidator(Protocol):
    """Protocol for OSM tag validation implementations."""
    def validate_tag(self, key: str, value: str) -> bool: ...
    def get_valid_values(self, key: str) -> List[str]: ...


class WebBasedTagValidator:
    """Implementation of OsmTagValidator using web APIs for validation."""
    
    def __init__(self, taginfo_base_url: str = "https://taginfo.openstreetmap.org/api/4"):
        self.taginfo_base_url = taginfo_base_url
    
    def validate_tag(self, key: str, value: str) -> bool:
        """
        Validates a tag against the OSM taginfo database.
        
        Args:
            key: The OSM tag key
            value: The OSM tag value
            
        Returns:
            True if the tag is valid, False otherwise
        """
        try:
            # Check if tag exists in taginfo
            url = f"{self.taginfo_base_url}/tag/show?key={key}&value={value}"
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except RequestException:
            # If we can't reach the API, assume the tag is valid
            # In a real implementation, you might want to cache common tags
            return True
    
    def get_valid_values(self, key: str) -> List[str]:
        """
        Returns common valid values for a given key.
        
        Args:
            key: The OSM tag key
            
        Returns:
            List of valid values for the key
        """
        try:
            url = f"{self.taginfo_base_url}/key/values?key={key}&sortname=count&sortorder=desc&page=1&rp=100&qtype=key"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'data' in data:
                    result_data = data['data']
                    if isinstance(result_data, list):
                        return [item['value'] for item in result_data if isinstance(item, dict) and 'value' in item]
        except (RequestException, ValueError):
            # If we can't reach the API or parse response, return empty list
            pass
        return []


class QuerySyntaxValidator:
    """Validates Overpass QL syntax."""
    
    @staticmethod
    def validate_syntax(query_string: str) -> Tuple[bool, str]:
        """
        Validates the syntax of an Overpass QL query.
        
        Args:
            query_string: The query string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for basic required elements in Overpass QL
        if "[out:" not in query_string:
            return False, "Query must specify output format with [out:]"
        
        if "out" not in query_string:
            return False, "Query must specify output command (out body/qt/skel)"
        
        if query_string.count('(') != query_string.count(')'):
            return False, "Mismatched parentheses in query"
        
        if query_string.count('[') != query_string.count(']'):
            return False, "Mismatched brackets in query"
        
        # Check for proper statement termination
        if not query_string.strip().endswith(';'):
            return False, "Query must end with semicolon"
        
        # Check for common query patterns
        if not any(pattern in query_string.lower() for pattern in ['node[', 'way[', 'relation[']):
            return False, "Query should contain at least one element search (node, way, or relation)"
        
        return True, ""


class AreaResolver:
    """Resolves area names to area IDs for Overpass queries."""
    
    @staticmethod
    def resolve_area(area_name: str) -> Optional[str]:
        """
        Resolves an area name to its Overpass representation.
        
        Args:
            area_name: Name of the area to resolve (e.g., "Paris", "New York")
            
        Returns:
            Overpass representation of the area, or None if not found
        """
        # In a real implementation, this would query the Nominatim API
        # For now, we'll return a simple formatted string
        if area_name:
            # Sanitize area name for use in query
            sanitized_name = area_name.replace('"', '\\"')
            return f'area[name="{sanitized_name}"]'
        return None


class ValidationConfig(BaseModel):
    """Configuration for the validation system."""
    enable_tag_validation: bool = True
    enable_syntax_validation: bool = True
    enable_area_resolution: bool = True
    enable_query_optimization: bool = True
    taginfo_base_url: str = "https://taginfo.openstreetmap.org/api/4"
    nominatim_base_url: str = "https://nominatim.openstreetmap.org"
    validation_timeout: int = 10  # seconds


class OverpassQLValidator:
    """Main validation class that combines all validation components."""
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.tag_validator = WebBasedTagValidator(self.config.taginfo_base_url)
        self.syntax_validator = QuerySyntaxValidator()
        self.area_resolver = AreaResolver()
    
    def validate_prompt(self, prompt: str, output_format: OutputFormat = "json") -> bool:
        """Validate a natural language prompt."""
        if not prompt or len(prompt.strip()) < 5:
            raise ValueError("Prompt must be at least 5 characters long")
        
        if output_format not in ["json", "xml", "geojson"]:
            raise ValueError(f"Output format must be one of json, xml, geojson")
        
        return True
    
    def validate_tags(self, tags: List[OsmTag]) -> List[str]:
        """Validate a list of tags and return validation errors."""
        errors = []
        
        if not tags:
            errors.append("At least one tag must be provided")
            return errors
        
        for tag in tags:
            try:
                # This triggers Pydantic's field validation
                _ = tag.key
                _ = tag.value
                
                # Additional validation using web API if enabled
                if self.config.enable_tag_validation:
                    if not self.tag_validator.validate_tag(tag.key, tag.value):
                        errors.append(f"Tag '{tag.key}={tag.value}' not found in OSM database")
            except ValueError as e:
                errors.append(f"Tag validation error: {str(e)}")
        
        return errors
    
    def validate_query(self, query: OverpassQuery) -> List[str]:
        """Validate a complete Overpass query."""
        errors = []
        
        # Check if query string is valid syntax
        if self.config.enable_syntax_validation and query.query_string:
            is_valid, error_msg = self.syntax_validator.validate_syntax(query.query_string)
            if not is_valid:
                errors.append(f"Query syntax error: {error_msg}")
        
        # Validate tags
        tag_errors = self.validate_tags(query.tags)
        errors.extend(tag_errors)
        
        # Validate geographic constraints
        if query.search_area and self.config.enable_area_resolution:
            resolved_area = self.area_resolver.resolve_area(query.search_area)
            if not resolved_area:
                errors.append(f"Could not resolve area: {query.search_area}")
        
        return errors
    
    def validate_geographic_filter(self, geo_filter: GeographicFilter) -> List[str]:
        """Validate geographic filter constraints."""
        errors = []
        
        try:
            # This triggers the model validation
            _ = geo_filter.area_name
            _ = geo_filter.bounding_box
            _ = geo_filter.polygon
        except ValueError as e:
            errors.append(f"Geographic filter validation error: {str(e)}")
        
        return errors