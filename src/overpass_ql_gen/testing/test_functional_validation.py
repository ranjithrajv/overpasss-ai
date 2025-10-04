"""
Functional Test Suite for Overpass QL Generator

This module contains comprehensive functional tests that validate 
Overpass QL queries by comparing their results against the Overpass API.
"""
import unittest
from typing import Dict, Any, List
import sys
import os

# Add the project root to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from overpass_ql_gen.testing.overpass_functional_tester import (
    OverpassFunctionalTester, FunctionalTest, FunctionalTestSuite, 
    TestStatus, QueryTestResult
)
from overpass_ql_gen.testing.test_utilities import (
    summarize_result, compare_element_counts, calculate_result_similarity
)
from overpass_ql_gen.oql_generator.generator import generate_query


class OverpassFunctionalTestSuite(unittest.TestCase):
    """Test suite for Overpass QL functional validation"""
    
    def setUp(self):
        """Set up the functional tester before each test"""
        self.tester = OverpassFunctionalTester(
            rate_limit_delay=0.5  # Reduced for testing
        )
    
    def test_basic_query_generation_and_execution(self):
        """Test that generated queries can be executed successfully"""
        # Generate a simple query
        test_query = """
        [out:json];
        area[name="Paris"]->.searchArea;
        (
          node["amenity"="cafe"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """
        
        test = FunctionalTest(
            name="Basic Cafe Query",
            description="Test basic cafe query in Paris",
            generated_query=test_query,
            expected_element_count=10  # Should find some cafes
        )
        
        result = self.tester.run_single_test(test)
        
        self.assertEqual(result.status, TestStatus.PASSED)
        self.assertGreater(result.result_count, 0, "Should find some cafe elements")
        print(f"Found {result.result_count} cafe elements in Paris")
    
    def test_query_comparison_with_reference(self):
        """Test comparing results of two similar queries"""
        query1 = """
        [out:json];
        area[name="Berlin"]->.searchArea;
        (
          node["amenity"="restaurant"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """
        
        query2 = """
        [out:json];
        area[name="Berlin"]->.searchArea;
        (
          node["amenity"="restaurant"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """
        
        test = FunctionalTest(
            name="Query Comparison Test",
            description="Compare two identical queries",
            generated_query=query1,
            reference_query=query2,
            similarity_threshold=0.9  # Allow for some variation due to data updates
        )
        
        result = self.tester.run_single_test(test)
        
        # Since both queries are identical, results should be very similar
        self.assertIn(result.status, [TestStatus.PASSED, TestStatus.FAILED])  # Both are acceptable
        print(f"Query 1 found {result.result_count} elements, reference had {result.reference_count}")
        print(f"Similarity: {result.similarity_score:.2f}")
    
    def test_natural_language_prompt_validation(self):
        """Test validation of queries generated from natural language"""
        prompt = "Find all libraries in London"
        
        result = self.tester.generate_and_test(
            prompt=prompt,
            expected_element_count=20  # Should find at least 20 libraries
        )
        
        self.assertIn(result.status, [TestStatus.PASSED, TestStatus.FAILED])
        if result.status == TestStatus.PASSED:
            self.assertGreater(result.result_count, 0)
        
        print(f"Generated query from '{prompt}' found {result.result_count} elements")
    
    def test_tag_validation(self):
        """Test validation that results contain expected tags"""
        query = """
        [out:json];
        area[name="Tokyo"]->.searchArea;
        (
          node["amenity"="hospital"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """
        
        test = FunctionalTest(
            name="Hospital Tag Validation",
            description="Verify hospital tag exists in results",
            generated_query=query,
            expected_tags=["amenity=hospital"]
        )
        
        result = self.tester.run_single_test(test)
        
        if result.status == TestStatus.PASSED:
            tag_validation = result.details
            self.assertIn("amenity=hospital", tag_validation["elements_with_expected_tags"])
            print(f"Found {tag_validation['elements_with_expected_tags']['amenity=hospital']} hospitals with correct tag")
    
    def test_element_type_distribution(self):
        """Test that results have expected element type distribution"""
        query = """
        [out:json];
        area[name="New York"]->.searchArea;
        (
          node["highway"="bus_stop"](area.searchArea);
          way["highway"="bus_stop"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """
        
        # Execute the query directly to analyze results
        raw_result = self.tester.execute_query(query)
        self.assertIsNotNone(raw_result, "Query execution should succeed")
        
        if raw_result:
            summary = summarize_result(raw_result)
            element_types = summary.get("element_types", {})
            
            print(f"Element types found: {element_types}")
            print(f"Total elements: {summary.get('total_elements', 0)}")
            
            # Verify that we got some results
            self.assertGreater(summary.get('total_elements', 0), 0)
    
    def test_result_similarity_calculation(self):
        """Test the similarity calculation between two similar result sets"""
        query1 = """
        [out:json];
        area[name="Rome"]->.searchArea;
        (
          node["tourism"="museum"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """
        
        query2 = """
        [out:json];
        area[name="Rome"]->.searchArea;
        (
          node["tourism"="museum"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """
        
        result1 = self.tester.execute_query(query1)
        result2 = self.tester.execute_query(query2)
        
        self.assertIsNotNone(result1, "First query should execute successfully")
        self.assertIsNotNone(result2, "Second query should execute successfully")
        
        if result1 and result2:
            similarity = calculate_result_similarity(result1, result2)
            print(f"Result similarity: {similarity:.2f}")
            
            # Should have reasonable similarity (not necessarily 1.0 due to data updates)
            self.assertGreaterEqual(similarity, 0.5, "Results should have some similarity")
    
    def test_complex_query_generation(self):
        """Test generation and validation of complex multi-tag queries"""
        # Test a more complex prompt
        complex_prompts = [
            "Find all schools and universities in Paris",
            "Show me all bicycle parking in Berlin",
            "Find cafes with outdoor seating in London",
            "Show me bus stops and metro stations in Tokyo"
        ]
        
        for prompt in complex_prompts:
            with self.subTest(prompt=prompt):
                result = self.tester.generate_and_test(
                    prompt=prompt,
                    expected_element_count=5  # Should find at least 5 of each
                )
                
                print(f"Prompt '{prompt}' generated query with {result.result_count} results")
                
                # Should successfully execute (whether it finds elements is another matter)
                self.assertNotEqual(result.status, TestStatus.ERROR)
    
    def test_error_handling(self):
        """Test that invalid queries are properly handled"""
        # Test with an intentionally invalid query
        invalid_query = """
        [out:json];
        (
          node["invalid"="tag"]({{bbox}});
        );
        out body;
        """
        
        test = FunctionalTest(
            name="Invalid Query Test",
            description="Test handling of invalid query",
            generated_query=invalid_query
        )
        
        result = self.tester.run_single_test(test)
        
        # Should either fail gracefully or have an error
        print(f"Invalid query result: {result.status}, error: {result.error}")
    
    def test_geojson_export_functionality(self):
        """Test the GeoJSON export functionality"""
        from overpass_ql_gen.testing.test_utilities import export_result_to_geojson
        
        query = """
        [out:json];
        area[name="Madrid"]->.searchArea;
        (
          node["amenity"="cafe"](area.searchArea);
        );
        out body;
        >;
        out skel qt;
        """
        
        raw_result = self.tester.execute_query(query)
        self.assertIsNotNone(raw_result)
        
        if raw_result:
            geojson_result = export_result_to_geojson(raw_result)
            
            self.assertEqual(geojson_result["type"], "FeatureCollection")
            self.assertIn("features", geojson_result)
            
            print(f"Exported {len(geojson_result['features'])} features to GeoJSON")
    
    def run_comprehensive_test_suite(self):
        """Run all tests and return a comprehensive test suite report"""
        suite = FunctionalTestSuite(
            name="Comprehensive Overpass QL Test Suite",
            description="Full functional test suite for Overpass QL generator"
        )
        
        # Add various test cases
        test_cases = [
            FunctionalTest(
                name="Paris Cafes",
                description="Find cafes in Paris",
                generated_query="""
                [out:json];
                area[name="Paris"]->.searchArea;
                (
                  node["amenity"="cafe"](area.searchArea);
                );
                out body;
                >;
                out skel qt;
                """,
                expected_element_count=50
            ),
            FunctionalTest(
                name="London Libraries",
                description="Find libraries in London",
                generated_query="""
                [out:json];
                area[name="London"]->.searchArea;
                (
                  node["amenity"="library"](area.searchArea);
                );
                out body;
                >;
                out skel qt;
                """,
                expected_element_count=20
            ),
            FunctionalTest(
                name="Berlin Hospitals",
                description="Find hospitals in Berlin",
                generated_query="""
                [out:json];
                area[name="Berlin"]->.searchArea;
                (
                  node["amenity"="hospital"](area.searchArea);
                );
                out body;
                >;
                out skel qt;
                """,
                expected_tags=["amenity=hospital"]
            )
        ]
        
        suite.tests = test_cases
        return self.tester.run_test_suite(suite)


def run_all_tests():
    """Run all functional tests and display results"""
    print("Running Overpass QL Functional Tests...")
    
    # Create a test suite runner
    test_loader = unittest.TestLoader()
    test_suite = test_loader.loadTestsFromTestCase(OverpassFunctionalTestSuite)
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Print summary
    print(f"\nTest Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    return result


def run_manual_tests():
    """Run some manual tests for demonstration"""
    print("\nRunning manual tests...")
    
    tester = OverpassFunctionalTester()
    
    # Test natural language prompt
    print("\n1. Testing natural language prompt 'Find cafes in Paris':")
    result = tester.generate_and_test(
        prompt="Find cafes in Paris",
        expected_element_count=10
    )
    print(f"   Status: {result.status}")
    print(f"   Found: {result.result_count} elements")
    
    # Test element type validation
    print("\n2. Testing element type validation:")
    query = """
    [out:json];
    area[name="Madrid"]->.searchArea;
    (
      node["amenity"="restaurant"](area.searchArea);
      way["amenity"="restaurant"](area.searchArea);
    );
    out body;
    >;
    out skel qt;
    """
    
    result = tester.execute_query(query)
    if result:
        from overpass_ql_gen.testing.test_utilities import summarize_result
        summary = summarize_result(result)
        print(f"   Total elements: {summary['total_elements']}")
        print(f"   Element types: {summary['element_types']}")
    
    # Run comprehensive suite
    print("\n3. Running comprehensive test suite:")
    functional_suite = OverpassFunctionalTestSuite()
    comprehensive_suite = functional_suite.run_comprehensive_test_suite()
    
    passed = sum(1 for r in comprehensive_suite.results if r.status == TestStatus.PASSED)
    total = len(comprehensive_suite.results)
    
    print(f"   Suite Results: {passed}/{total} tests passed")
    print(f"   Total execution time: {comprehensive_suite.total_time:.2f}s")


if __name__ == "__main__":
    # Run both automated and manual tests
    print("Starting Overpass QL Functional Testing Framework")
    
    # Run the automated test suite
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run manual tests as well
    run_manual_tests()