"""
Functional Testing Framework for Overpass QL Queries

This module provides tools for testing Overpass QL queries by executing them
against the actual Overpass API and comparing results.
"""
from typing import Dict, Any, List, Optional, Union, Callable
import requests
import json
import time
import hashlib
from dataclasses import dataclass, field
from enum import Enum
from difflib import SequenceMatcher
import logging

# Add the main package to import the generator
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from overpass_ql_gen.oql_generator.generator import generate_query, OverpassQuery
from overpass_ql_gen.validation.validator import OverpassQLValidator


class TestStatus(Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    ERROR = "ERROR"
    SKIPPED = "SKIPPED"


@dataclass
class QueryTestResult:
    """Result of a single query test"""
    query: str
    status: TestStatus
    execution_time: float
    result_count: int
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    reference_count: Optional[int] = None
    similarity_score: Optional[float] = None


@dataclass
class FunctionalTestSuite:
    """A suite of functional tests for Overpass QL queries"""
    name: str
    description: str = ""
    tests: List['FunctionalTest'] = field(default_factory=list)
    results: List[QueryTestResult] = field(default_factory=list)
    total_time: float = 0.0


@dataclass
class FunctionalTest:
    """A single functional test case"""
    name: str
    description: str
    generated_query: Optional[str] = None
    reference_query: Optional[str] = None
    expected_element_count: Optional[int] = None
    similarity_threshold: float = 0.95
    timeout: int = 60
    test_function: Optional[Callable] = None  # Custom test function
    expected_tags: Optional[List[str]] = None  # Expected tag patterns in results


class OverpassFunctionalTester:
    """
    Main class for functional testing of Overpass QL queries
    """
    
    def __init__(self, 
                 api_url: str = "https://overpass-api.de/api/interpreter",
                 rate_limit_delay: float = 1.0):
        self.api_url = api_url
        self.rate_limit_delay = rate_limit_delay
        self.session = requests.Session()
        self.validator = OverpassQLValidator()
        self.logger = logging.getLogger(__name__)
        
    def execute_query(self, query: str, timeout: int = 60) -> Optional[Dict[Any, Any]]:
        """
        Execute a query against the Overpass API
        """
        try:
            # Add rate limiting
            time.sleep(self.rate_limit_delay)
            
            response = self.session.post(
                self.api_url,
                data=query,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error executing query: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing response JSON: {e}")
            return None
    
    def compare_results(self, 
                       generated_result: Dict, 
                       reference_result: Dict,
                       threshold: float = 0.95) -> Dict[str, Any]:
        """
        Compare two query results and return similarity metrics
        """
        elements_gen = generated_result.get('elements', [])
        elements_ref = reference_result.get('elements', [])
        
        gen_count = len(elements_gen)
        ref_count = len(elements_ref)
        
        result = {
            "generated_count": gen_count,
            "reference_count": ref_count,
            "count_ratio": gen_count / ref_count if ref_count > 0 else 0,
            "count_diff": abs(gen_count - ref_count),
        }
        
        # Calculate similarity based on element count
        if ref_count == 0:
            result["similarity"] = 1.0 if gen_count == 0 else 0.0
        elif gen_count == 0:
            result["similarity"] = 0.0
        else:
            min_count = min(gen_count, ref_count)
            max_count = max(gen_count, ref_count)
            result["similarity"] = min_count / max_count
        
        # Compare element IDs if available
        gen_ids = set()
        ref_ids = set()
        
        for elem in elements_gen:
            if 'id' in elem and 'type' in elem:
                gen_ids.add(f"{elem['type']}_{elem['id']}")
        
        for elem in elements_ref:
            if 'id' in elem and 'type' in elem:
                ref_ids.add(f"{elem['type']}_{elem['id']}")
        
        if gen_ids or ref_ids:
            intersection = gen_ids.intersection(ref_ids)
            union = gen_ids.union(ref_ids)
            
            if union:
                result["jaccard_similarity"] = len(intersection) / len(union)
            else:
                result["jaccard_similarity"] = 1.0  # Both sets are empty
            
            result["common_elements"] = len(intersection)
            result["unique_to_generated"] = len(gen_ids - ref_ids)
            result["unique_to_reference"] = len(ref_ids - gen_ids)
        
        # Check if results are similar enough
        result["is_similar"] = result["similarity"] >= threshold
        
        return result
    
    def validate_element_tags(self, 
                            result: Dict, 
                            expected_tags: List[str]) -> Dict[str, Any]:
        """
        Validate that result elements contain expected tags
        """
        elements = result.get('elements', [])
        tag_validation = {
            "total_elements": len(elements),
            "elements_with_expected_tags": {},
            "missing_tags": []
        }
        
        for tag in expected_tags:
            key, value = tag.split('=', 1) if '=' in tag else (tag, None)
            count = 0
            
            for elem in elements:
                elem_tags = elem.get('tags', {})
                if key in elem_tags:
                    if value is None or elem_tags[key] == value:
                        count += 1
            
            tag_validation["elements_with_expected_tags"][tag] = count
            
            if count == 0:
                tag_validation["missing_tags"].append(tag)
        
        return tag_validation
    
    def run_single_test(self, test: FunctionalTest) -> QueryTestResult:
        """
        Run a single functional test
        """
        start_time = time.time()
        
        try:
            # If a custom test function is provided, use that instead
            if test.test_function:
                result = test.test_function()
                execution_time = time.time() - start_time
                return QueryTestResult(
                    query="custom_test",
                    status=TestStatus.PASSED if result.get("passed", False) else TestStatus.FAILED,
                    execution_time=execution_time,
                    result_count=result.get("result_count", 0),
                    details=result
                )
            
            # Execute the generated query
            generated_result = self.execute_query(test.generated_query, test.timeout)
            if generated_result is None:
                execution_time = time.time() - start_time
                return QueryTestResult(
                    query=test.generated_query,
                    status=TestStatus.ERROR,
                    execution_time=execution_time,
                    result_count=0,
                    error="Generated query execution failed"
                )
            
            # Get element count from generated result
            gen_count = len(generated_result.get('elements', []))
            
            # If reference query is provided, compare results
            if test.reference_query:
                reference_result = self.execute_query(test.reference_query, test.timeout)
                if reference_result is None:
                    execution_time = time.time() - start_time
                    return QueryTestResult(
                        query=test.generated_query,
                        status=TestStatus.ERROR,
                        execution_time=execution_time,
                        result_count=gen_count,
                        error="Reference query execution failed"
                    )
                
                # Compare results
                comparison = self.compare_results(
                    generated_result, 
                    reference_result, 
                    test.similarity_threshold
                )
                
                execution_time = time.time() - start_time
                
                status = TestStatus.PASSED if comparison["is_similar"] else TestStatus.FAILED
                
                return QueryTestResult(
                    query=test.generated_query,
                    status=status,
                    execution_time=execution_time,
                    result_count=gen_count,
                    reference_count=comparison["reference_count"],
                    similarity_score=comparison["similarity"],
                    details=comparison
                )
            
            # If expected element count is provided, validate against it
            elif test.expected_element_count is not None:
                expected = test.expected_element_count
                actual = gen_count
                is_close = abs(actual - expected) <= max(1, expected * 0.1)  # 10% tolerance
                
                execution_time = time.time() - start_time
                status = TestStatus.PASSED if is_close else TestStatus.FAILED
                
                return QueryTestResult(
                    query=test.generated_query,
                    status=status,
                    execution_time=execution_time,
                    result_count=gen_count,
                    details={
                        "expected_count": expected,
                        "actual_count": actual,
                        "is_within_tolerance": is_close
                    }
                )
            
            # If expected tags are provided, validate them
            elif test.expected_tags:
                tag_validation = self.validate_element_tags(generated_result, test.expected_tags)
                
                execution_time = time.time() - start_time
                has_all_tags = len(tag_validation["missing_tags"]) == 0
                status = TestStatus.PASSED if has_all_tags else TestStatus.FAILED
                
                return QueryTestResult(
                    query=test.generated_query,
                    status=status,
                    execution_time=execution_time,
                    result_count=gen_count,
                    details=tag_validation
                )
            
            # Just check if query executed successfully with elements
            else:
                execution_time = time.time() - start_time
                status = TestStatus.PASSED if gen_count > 0 else TestStatus.FAILED
                
                return QueryTestResult(
                    query=test.generated_query,
                    status=status,
                    execution_time=execution_time,
                    result_count=gen_count,
                    details={"has_results": gen_count > 0}
                )
                
        except Exception as e:
            execution_time = time.time() - start_time
            return QueryTestResult(
                query=test.generated_query if test.generated_query else "unknown",
                status=TestStatus.ERROR,
                execution_time=execution_time,
                result_count=0,
                error=str(e)
            )
    
    def run_test_suite(self, test_suite: FunctionalTestSuite) -> FunctionalTestSuite:
        """
        Run all tests in a test suite
        """
        start_time = time.time()
        
        for test in test_suite.tests:
            result = self.run_single_test(test)
            test_suite.results.append(result)
        
        test_suite.total_time = time.time() - start_time
        return test_suite
    
    def generate_and_test(self, 
                         prompt: str, 
                         expected_query: Optional[str] = None,
                         expected_element_count: Optional[int] = None,
                         similarity_threshold: float = 0.95) -> QueryTestResult:
        """
        Generate a query from a prompt and test it
        """
        try:
            # Generate the query
            generated_query_obj = generate_query(prompt)
            generated_query = generated_query_obj.query_string
            
            # Create a test with the generated query
            test = FunctionalTest(
                name=f"Generated: {prompt}",
                description=f"Test for query generated from: {prompt}",
                generated_query=generated_query,
                reference_query=expected_query,
                expected_element_count=expected_element_count,
                similarity_threshold=similarity_threshold
            )
            
            return self.run_single_test(test)
            
        except Exception as e:
            return QueryTestResult(
                query="generation_failed",
                status=TestStatus.ERROR,
                execution_time=0,
                result_count=0,
                error=f"Query generation failed: {str(e)}"
            )
    
    def create_test_from_prompt(self, 
                               name: str, 
                               prompt: str, 
                               expected_element_count: Optional[int] = None,
                               expected_tags: Optional[List[str]] = None,
                               description: str = "") -> FunctionalTest:
        """
        Create a test from a natural language prompt
        """
        try:
            # Generate the query from the prompt
            query_obj = generate_query(prompt)
            generated_query = query_obj.query_string
            
            test = FunctionalTest(
                name=name,
                description=description or f"Test for: {prompt}",
                generated_query=generated_query,
                expected_element_count=expected_element_count,
                expected_tags=expected_tags
            )
            
            return test
        except Exception as e:
            self.logger.error(f"Failed to create test from prompt '{prompt}': {e}")
            return None