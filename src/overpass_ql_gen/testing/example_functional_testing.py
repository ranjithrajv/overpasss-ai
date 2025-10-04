"""
Example: Using Overpass API for Functional Testing

This script demonstrates how to use the functional testing framework
to validate Overpass QL queries by comparing their results.
"""
import sys
import os
import time

# Add the project root and src to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from overpass_ql_gen.testing.overpass_functional_tester import (
    OverpassFunctionalTester, FunctionalTest, TestStatus
)
from overpass_ql_gen.testing.test_utilities import (
    summarize_result, calculate_result_similarity
)
from overpass_ql_gen.oql_generator.generator import generate_query


def example_basic_functional_test():
    """Example 1: Basic functional test using natural language prompt"""
    print("=== Example 1: Basic Functional Test ===")
    
    tester = OverpassFunctionalTester(rate_limit_delay=1.0)
    
    # Test a natural language query
    prompt = "Find all cafes in Paris"
    print(f"Testing prompt: '{prompt}'")
    
    # Generate and test the query
    result = tester.generate_and_test(
        prompt=prompt,
        expected_element_count=10,  # Expect at least 10 cafes
        similarity_threshold=0.8
    )
    
    print(f"Status: {result.status}")
    print(f"Elements found: {result.result_count}")
    print(f"Execution time: {result.execution_time:.2f}s")
    
    if result.error:
        print(f"Error: {result.error}")
    
    return result


def example_query_comparison():
    """Example 2: Compare two different queries for similarity"""
    print("\n=== Example 2: Query Result Comparison ===")
    
    tester = OverpassFunctionalTester(rate_limit_delay=1.0)
    
    # Two queries that should return similar results
    query1 = """
    [out:json];
    area[name="London"]->.searchArea;
    (
      node["amenity"="pub"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    
    query2 = """
    [out:json];
    area[name="London"]->.searchArea;
    (
      node["amenity"="pub"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    
    print("Comparing two pub queries in London...")
    
    test = FunctionalTest(
        name="London Pubs Comparison",
        description="Compare two identical pub queries",
        generated_query=query1,
        reference_query=query2,
        similarity_threshold=0.8
    )
    
    result = tester.run_single_test(test)
    
    print(f"Status: {result.status}")
    print(f"Generated query elements: {result.result_count}")
    print(f"Reference query elements: {result.reference_count}")
    print(f"Similarity score: {result.similarity_score:.2f}")
    
    return result


def example_tag_validation():
    """Example 3: Validate that results contain expected tags"""
    print("\n=== Example 3: Tag Validation ===")
    
    tester = OverpassFunctionalTester(rate_limit_delay=1.0)
    
    # Query for schools
    query = """
    [out:json];
    area[name="Berlin"]->.searchArea;
    (
      node["amenity"="school"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    
    print("Testing school query with tag validation...")
    
    test = FunctionalTest(
        name="Berlin Schools Tag Validation",
        description="Verify school tag exists in results",
        generated_query=query,
        expected_tags=["amenity=school"]
    )
    
    result = tester.run_single_test(test)
    
    print(f"Status: {result.status}")
    print(f"Elements found: {result.result_count}")
    
    if result.details:
        tag_validation = result.details
        print(f"Elements with 'amenity=school': {tag_validation.get('elements_with_expected_tags', {}).get('amenity=school', 0)}")
        if tag_validation.get('missing_tags'):
            print(f"Missing tags: {tag_validation['missing_tags']}")
    
    return result


def example_generated_vs_expected():
    """Example 4: Compare generated query with expected behavior"""
    print("\n=== Example 4: Generated vs Expected Query ===")
    
    tester = OverpassFunctionalTester(rate_limit_delay=1.0)
    
    # Natural language prompt
    prompt = "Find all bicycle parking in Amsterdam"
    
    # Generate the query from the prompt
    print(f"Generating query for: '{prompt}'")
    generated_query_obj = generate_query(prompt)
    generated_query = generated_query_obj.query_string
    print(f"Generated query:\n{generated_query}")
    
    # Expected query (hand-crafted to be correct)
    expected_query = """
    [out:json];
    area[name="Amsterdam"]->.searchArea;
    (
      node["amenity"="bicycle_parking"](area.searchArea);
      way["amenity"="bicycle_parking"](area.searchArea);
      relation["amenity"="bicycle_parking"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    
    # Compare the two queries
    test = FunctionalTest(
        name="Bicycle Parking Comparison",
        description="Compare generated vs expected bicycle parking query",
        generated_query=generated_query,
        reference_query=expected_query,
        similarity_threshold=0.7
    )
    
    result = tester.run_single_test(test)
    
    print(f"Status: {result.status}")
    print(f"Generated elements: {result.result_count}")
    print(f"Expected elements: {result.reference_count}")
    print(f"Similarity: {result.similarity_score:.2f}")
    
    return result


def example_result_analysis():
    """Example 5: Analyze query results in detail"""
    print("\n=== Example 5: Result Analysis ===")
    
    tester = OverpassFunctionalTester(rate_limit_delay=1.0)
    
    # Query for restaurants
    query = """
    [out:json];
    area[name="Tokyo"]->.searchArea;
    (
      node["amenity"="restaurant"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    
    print("Executing restaurant query in Tokyo and analyzing results...")
    
    raw_result = tester.execute_query(query)
    
    if raw_result:
        summary = summarize_result(raw_result)
        
        print(f"Total elements: {summary['total_elements']}")
        print(f"Element types: {summary['element_types']}")
        print(f"Common tags: {summary['common_tags']}")
        print(f"Has geometry: {summary['has_geometry']}")
        
        if summary['bbox']:
            bbox = summary['bbox']
            print(f"Bounding box: ({bbox['south']:.4f}, {bbox['west']:.4f}) to ({bbox['north']:.4f}, {bbox['east']:.4f})")
    else:
        print("Query execution failed")
    
    return raw_result


def main():
    """Run all examples"""
    print("Overpass QL Functional Testing Examples")
    print("=" * 50)
    
    try:
        example_basic_functional_test()
        example_query_comparison()
        example_tag_validation()
        example_generated_vs_expected()
        example_result_analysis()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()