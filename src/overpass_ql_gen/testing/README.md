# Overpass QL Functional Testing

This module provides a comprehensive framework for functional testing of Overpass QL queries using the actual Overpass API to validate query correctness and result quality.

## Components

### OverpassFunctionalTester
The main class for executing functional tests against real OSM data:

- Executes queries against the Overpass API
- Compares query results for similarity
- Validates expected tags and element counts
- Provides detailed test results

### Functional Testing Features

1. **Query Generation & Validation**:
   - Generate queries from natural language prompts
   - Validate that queries execute successfully
   - Check result counts against expectations

2. **Result Comparison**:
   - Compare results of different queries
   - Calculate similarity scores between result sets
   - Validate element type distributions

3. **Tag Validation**:
   - Ensure results contain expected tags
   - Verify tag distributions
   - Check for specific tag-value combinations

4. **Comprehensive Test Suites**:
   - Group multiple tests together
   - Run batch validation
   - Generate detailed reports

## Usage Examples

### Basic Functional Test
```python
from overpass_ql_gen.testing import OverpassFunctionalTester, FunctionalTest, TestStatus

tester = OverpassFunctionalTester()

# Test a natural language prompt
result = tester.generate_and_test(
    prompt="Find all cafes in Paris",
    expected_element_count=10,
    similarity_threshold=0.8
)

if result.status == TestStatus.PASSED:
    print(f"Found {result.result_count} cafes in Paris")
```

### Query Comparison Test
```python
test = FunctionalTest(
    name="Cafe Comparison",
    description="Compare two cafe queries",
    generated_query=generated_query,
    reference_query=reference_query,
    similarity_threshold=0.9
)

result = tester.run_single_test(test)
print(f"Similarity: {result.similarity_score:.2f}")
```

### Comprehensive Test Suite
```python
from overpass_ql_gen.testing import FunctionalTestSuite

suite = FunctionalTestSuite(
    name="Cafe Queries Test Suite",
    description="Test various cafe queries across different cities"
)

# Add tests to suite
suite.tests = [test1, test2, test3]

# Run all tests
completed_suite = tester.run_test_suite(suite)

# Analyze results
passed = sum(1 for r in completed_suite.results if r.status == TestStatus.PASSED)
total = len(completed_suite.results)
print(f"Results: {passed}/{total} tests passed")
```

## Test Utilities

The module includes various utilities for result analysis:

- `summarize_result()`: Create a summary of query results
- `calculate_result_similarity()`: Calculate similarity between two result sets
- `export_result_to_geojson()`: Convert results to GeoJSON format
- `validate_result_structure()`: Validate basic result structure

## Best Practices

1. **Rate Limiting**: The tester includes built-in rate limiting to respect the Overpass API
2. **Error Handling**: Proper error handling for network issues and API limits
3. **Similarity Thresholds**: Use appropriate similarity thresholds for different types of tests
4. **Expected Results**: Define reasonable expectations based on typical OSM data density

## Running Tests

Execute the functional tests:

```bash
cd /path/to/overpass-ai
python -m pytest src/overpass_ql_gen/testing/test_functional_validation.py
```

Or run the example:

```bash
python src/overpass_ql_gen/testing/example_functional_testing.py
```

## Note on API Usage

- Tests execute real queries against the Overpass API
- Be mindful of rate limits and usage policies
- Queries execute in real-time, so tests may take some time to complete
- Network connectivity is required to run functional tests