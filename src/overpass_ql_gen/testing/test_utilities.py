"""
Test Utilities for Overpass QL Functional Testing

This module provides various utilities for comparing, analyzing, and 
validating Overpass QL query results.
"""
from typing import Dict, Any, List, Optional, Set
from collections import Counter
import json


def extract_elements_by_type(result: Dict[str, Any], element_type: str) -> List[Dict[str, Any]]:
    """Extract elements of a specific type from query results."""
    elements = result.get('elements', [])
    return [elem for elem in elements if elem.get('type') == element_type]


def extract_elements_by_tag(result: Dict[str, Any], tag_key: str, tag_value: Optional[str] = None) -> List[Dict[str, Any]]:
    """Extract elements with a specific tag from query results."""
    elements = result.get('elements', [])
    matching_elements = []
    
    for elem in elements:
        tags = elem.get('tags', {})
        if tag_key in tags:
            if tag_value is None or tags[tag_key] == tag_value:
                matching_elements.append(elem)
    
    return matching_elements


def count_tag_values(result: Dict[str, Any], tag_key: str) -> Dict[str, int]:
    """Count occurrences of different values for a specific tag."""
    elements = result.get('elements', [])
    values = []
    
    for elem in elements:
        tags = elem.get('tags', {})
        if tag_key in tags:
            values.append(tags[tag_key])
    
    return dict(Counter(values))


def get_element_ids(result: Dict[str, Any]) -> Set[str]:
    """Get a set of all element IDs in the result."""
    elements = result.get('elements', [])
    ids = set()
    
    for elem in elements:
        if 'id' in elem and 'type' in elem:
            ids.add(f"{elem['type']}_{elem['id']}")
    
    return ids


def compare_element_counts(result1: Dict[str, Any], result2: Dict[str, Any]) -> Dict[str, Any]:
    """Compare element counts between two results."""
    return {
        "nodes": {
            "result1": len(extract_elements_by_type(result1, "node")),
            "result2": len(extract_elements_by_type(result2, "node")),
        },
        "ways": {
            "result1": len(extract_elements_by_type(result1, "way")),
            "result2": len(extract_elements_by_type(result2, "way")),
        },
        "relations": {
            "result1": len(extract_elements_by_type(result1, "relation")),
            "result2": len(extract_elements_by_type(result2, "relation")),
        },
        "total": {
            "result1": len(result1.get('elements', [])),
            "result2": len(result2.get('elements', [])),
        }
    }


def compare_tag_distributions(result1: Dict[str, Any], result2: Dict[str, Any], tag_key: str) -> Dict[str, Any]:
    """Compare tag distributions between two results."""
    dist1 = count_tag_values(result1, tag_key)
    dist2 = count_tag_values(result2, tag_key)
    
    all_values = set(dist1.keys()) | set(dist2.keys())
    
    comparison = {}
    for value in all_values:
        comparison[value] = {
            "result1": dist1.get(value, 0),
            "result2": dist2.get(value, 0),
            "diff": dist1.get(value, 0) - dist2.get(value, 0)
        }
    
    return comparison


def validate_result_structure(result: Dict[str, Any]) -> List[str]:
    """Validate the basic structure of query results."""
    errors = []
    
    if 'elements' not in result:
        errors.append("Missing 'elements' key in result")
    elif not isinstance(result['elements'], list):
        errors.append("'elements' should be a list")
    else:
        for i, elem in enumerate(result['elements']):
            if not isinstance(elem, dict):
                errors.append(f"Element {i} is not a dictionary")
                continue
            
            if 'type' not in elem:
                errors.append(f"Element {i} missing 'type' field")
            if 'id' not in elem:
                errors.append(f"Element {i} missing 'id' field")
    
    return errors


def calculate_result_similarity(result1: Dict[str, Any], 
                              result2: Dict[str, Any], 
                              method: str = "intersection") -> float:
    """
    Calculate similarity between two query results.
    
    Args:
        result1, result2: Query results as dictionaries
        method: Similarity calculation method ('intersection', 'dice', 'jaccard')
    """
    ids1 = get_element_ids(result1)
    ids2 = get_element_ids(result2)
    
    intersection = len(ids1.intersection(ids2))
    union = len(ids1.union(ids2))
    len1, len2 = len(ids1), len(ids2)
    
    if method == "intersection":
        # Ratio of common elements to the smaller result
        min_len = min(len1, len2) if min(len1, len2) > 0 else 1
        return intersection / min_len
    
    elif method == "jaccard":
        # Jaccard similarity
        return intersection / union if union > 0 else 1.0  # Both empty = 100% similar
    
    elif method == "dice":
        # Dice coefficient
        return (2 * intersection) / (len1 + len2) if (len1 + len2) > 0 else 1.0
    
    else:
        raise ValueError(f"Unknown similarity method: {method}")


def summarize_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Create a summary of the query result."""
    elements = result.get('elements', [])
    
    # Count element types
    type_counts = Counter()
    tag_counts = Counter()
    
    for elem in elements:
        elem_type = elem.get('type', 'unknown')
        type_counts[elem_type] += 1
        
        for tag in elem.get('tags', {}):
            tag_counts[tag] += 1
    
    return {
        "total_elements": len(elements),
        "element_types": dict(type_counts),
        "common_tags": dict(tag_counts.most_common(10)),  # Top 10 tags
        "has_geometry": any('lat' in elem and 'lon' in elem for elem in elements),
        "bbox": calculate_bounding_box(result)
    }


def calculate_bounding_box(result: Dict[str, Any]) -> Optional[Dict[str, float]]:
    """Calculate the bounding box of elements in the result."""
    elements = result.get('elements', [])
    
    lats = []
    lons = []
    
    for elem in elements:
        if 'lat' in elem and 'lon' in elem:
            lats.append(elem['lat'])
            lons.append(elem['lon'])
    
    if not lats or not lons:
        return None
    
    return {
        "south": min(lats),
        "west": min(lons),
        "north": max(lats),
        "east": max(lons)
    }


def export_result_to_geojson(result: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Overpass result to GeoJSON format for visualization."""
    elements = result.get('elements', [])
    features = []
    
    for elem in elements:
        if 'lat' in elem and 'lon' in elem:
            # Point geometry
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [elem.get('lon'), elem.get('lat')]
                },
                "properties": {
                    "id": elem.get('id'),
                    "type": elem.get('type'),
                    "tags": elem.get('tags', {}),
                    "timestamp": elem.get('timestamp') if 'timestamp' in elem else None
                }
            }
            features.append(feature)
        elif 'center' in elem:
            # Node with center point
            center = elem['center']
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [center.get('lon'), center.get('lat')]
                },
                "properties": {
                    "id": elem.get('id'),
                    "type": elem.get('type'),
                    "tags": elem.get('tags', {}),
                    "is_center": True
                }
            }
            features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "total_elements": len(elements),
            "generator": result.get('generator', 'unknown'),
            "version": result.get('version', 'unknown')
        }
    }


def result_to_csv(result: Dict[str, Any], include_geometry: bool = True) -> List[Dict[str, Any]]:
    """Convert Overpass result to CSV-friendly rows."""
    elements = result.get('elements', [])
    rows = []
    
    for elem in elements:
        row = {
            "id": elem.get('id'),
            "type": elem.get('type'),
        }
        
        # Add coordinates if available
        if include_geometry:
            if 'lat' in elem and 'lon' in elem:
                row["latitude"] = elem['lat']
                row["longitude"] = elem['lon']
            elif 'center' in elem:
                row["latitude"] = elem['center'].get('lat')
                row["longitude"] = elem['center'].get('lon')
        
        # Add all tags as separate columns
        for tag_key, tag_value in elem.get('tags', {}).items():
            row[f"tag_{tag_key}"] = tag_value
        
        # Add other attributes
        if 'timestamp' in elem:
            row["timestamp"] = elem['timestamp']
        if 'version' in elem:
            row["version"] = elem['version']
        if 'user' in elem:
            row["user"] = elem['user']
        
        rows.append(row)
    
    return rows