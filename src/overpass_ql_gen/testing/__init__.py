"""
Testing module for Overpass QL Generator

This module provides functional testing capabilities for validating
Overpass QL queries against the actual Overpass API.
"""
from .overpass_functional_tester import (
    OverpassFunctionalTester,
    FunctionalTest,
    FunctionalTestSuite,
    QueryTestResult,
    TestStatus
)

from .test_utilities import (
    extract_elements_by_type,
    extract_elements_by_tag,
    count_tag_values,
    get_element_ids,
    compare_element_counts,
    compare_tag_distributions,
    validate_result_structure,
    calculate_result_similarity,
    summarize_result,
    calculate_bounding_box,
    export_result_to_geojson,
    result_to_csv
)

__all__ = [
    # Main tester
    'OverpassFunctionalTester',
    
    # Test structures
    'FunctionalTest',
    'FunctionalTestSuite',
    'QueryTestResult',
    'TestStatus',
    
    # Utilities
    'extract_elements_by_type',
    'extract_elements_by_tag', 
    'count_tag_values',
    'get_element_ids',
    'compare_element_counts',
    'compare_tag_distributions',
    'validate_result_structure',
    'calculate_result_similarity',
    'summarize_result',
    'calculate_bounding_box',
    'export_result_to_geojson',
    'result_to_csv'
]