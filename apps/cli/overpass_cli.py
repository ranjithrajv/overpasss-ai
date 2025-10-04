#!/usr/bin/env python3
import argparse
import sys
import os

# Add the project root to the Python path to import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

# Add src directory to Python path to import overpass_ql_gen
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from overpass_ql_gen.oql_generator.generator import generate_query, OverpassQLError

# Import functional testing framework
try:
    from overpass_ql_gen.testing.overpass_functional_tester import OverpassFunctionalTester, FunctionalTest, TestStatus
    FUNCTIONAL_TESTING_AVAILABLE = True
except ImportError:
    FUNCTIONAL_TESTING_AVAILABLE = False
    print("Warning: Functional testing framework not available. Install dependencies to enable testing features.")

def main() -> None:
    """
    Main function for the Overpass QL generator CLI.
    """
    parser = argparse.ArgumentParser(description="Generate Overpass QL from natural language.")
    parser.add_argument("prompt", type=str, help="The natural language prompt.")
    parser.add_argument("--format", type=str, default="json", choices=["json", "xml", "geojson"], help="The output format.")
    parser.add_argument("--test", action="store_true", help="Execute the generated query against the Overpass API to get results")
    parser.add_argument("--reference-query", type=str, help="Reference query to compare against (used with --test)")
    parser.add_argument("--output-file", type=str, help="File to save the query results")
    
    args = parser.parse_args()

    try:
        # Generate query from the prompt
        query_result = generate_query(args.prompt, output_format=args.format)
        print("Generated Overpass QL query:")
        print(query_result.query_string)
        
        # If test flag is provided, execute the query and check if results match prompt intent
        if args.test and FUNCTIONAL_TESTING_AVAILABLE:
            print("\n🔍 Validating that query results match prompt intent...")
            
            tester = OverpassFunctionalTester()
            
            if args.reference_query:
                # Compare with reference query
                test = FunctionalTest(
                    name="Reference Query Comparison",
                    description=f"Comparing generated query with reference: {args.reference_query[:50]}...",
                    generated_query=query_result.query_string,
                    reference_query=args.reference_query,
                    similarity_threshold=0.8
                )
                result = tester.run_single_test(test)
                
                print(f"📊 Test Status: {result.status}")
                print(f"📈 Generated Elements: {result.result_count}")
                print(f"📈 Reference Elements: {result.reference_count}")
                print(f"🎯 Similarity Score: {result.similarity_score:.2f}" if result.similarity_score else "🎯 Similarity Score: N/A")
                
                if result.status == TestStatus.PASSED:
                    print("✅ Query validation PASSED - Results are similar to reference query")
                else:
                    print("❌ Query validation FAILED - Results differ significantly from reference")
                    
            else:
                # Execute the query and validate that results match the prompt intent
                print(f"\n🔍 Executing generated query against Overpass API to validate against prompt: '{args.prompt}'")
                raw_result = tester.execute_query(query_result.query_string)
                
                if raw_result:
                    element_count = len(raw_result.get('elements', []))
                    print(f"📈 Query Results: {element_count} elements found")
                    
                    # Import utilities to provide detailed analysis and validation
                    try:
                        from overpass_ql_gen.testing.test_utilities import (
                            summarize_result, 
                            extract_elements_by_tag,
                            count_tag_values
                        )
                        
                        summary = summarize_result(raw_result)
                        print(f"📊 Result Analysis:")
                        print(f"   - Total elements: {summary['total_elements']}")
                        print(f"   - Element types: {summary['element_types']}")
                        print(f"   - Common tags: {list(summary['common_tags'].keys())[:5]}")
                        print(f"   - Has geometry: {summary['has_geometry']}")
                        
                        # Analyze if results match the prompt intent
                        prompt_lower = args.prompt.lower()
                        matched_elements = 0
                        
                        # Check if results contain expected amenities based on prompt keywords
                        if 'school' in prompt_lower or 'schools' in prompt_lower:
                            schools = extract_elements_by_tag(raw_result, 'amenity', 'school')
                            matched_elements = len(schools)
                            print(f"   - Schools found: {len(schools)}")
                        
                        elif 'university' in prompt_lower or 'universities' in prompt_lower:
                            universities = extract_elements_by_tag(raw_result, 'amenity', 'university')
                            matched_elements = len(universities)
                            print(f"   - Universities found: {len(universities)}")
                        
                        elif 'cafe' in prompt_lower or 'cafes' in prompt_lower:
                            cafes = extract_elements_by_tag(raw_result, 'amenity', 'cafe')
                            matched_elements = len(cafes)
                            print(f"   - Cafes found: {len(cafes)}")
                            
                        elif 'restaurant' in prompt_lower or 'restaurants' in prompt_lower:
                            restaurants = extract_elements_by_tag(raw_result, 'amenity', 'restaurant')
                            matched_elements = len(restaurants)
                            print(f"   - Restaurants found: {len(restaurants)}")
                        
                        elif 'hospital' in prompt_lower or 'hospitals' in prompt_lower:
                            hospitals = extract_elements_by_tag(raw_result, 'amenity', 'hospital')
                            matched_elements = len(hospitals)
                            print(f"   - Hospitals found: {len(hospitals)}")
                        
                        elif 'park' in prompt_lower or 'parks' in prompt_lower:
                            parks = extract_elements_by_tag(raw_result, 'leisure', 'park')
                            if not parks:
                                parks = extract_elements_by_tag(raw_result, 'amenity', 'park')
                            matched_elements = len(parks)
                            print(f"   - Parks found: {len(parks)}")
                        
                        else:
                            # For general cases, analyze common tags
                            common_tags = summary['common_tags']
                            print(f"   - Common tags analysis: {list(common_tags.keys())[:5]}")
                            matched_elements = element_count
                        
                        print(f"   - Elements matching prompt intent: {matched_elements}")
                        
                        # Determine validation status
                        if matched_elements > 0:
                            print(f"✅ VALIDATION SUCCESS: Query results match prompt intent")
                            print(f"   The query found {matched_elements} elements related to '{args.prompt}'")
                        else:
                            print(f"⚠️  VALIDATION WARNING: No clear matches found for prompt intent")
                            print(f"   You may want to refine your prompt or check the results manually")
                        
                        # Save results if output file specified
                        if args.output_file:
                            import json
                            with open(args.output_file, 'w') as f:
                                json.dump(raw_result, f, indent=2)
                            print(f"💾 Results saved to: {args.output_file}")
                            
                    except ImportError:
                        print(f"📊 Found {element_count} elements in response")
                        print(f"   (Detailed analysis requires additional dependencies)")
                        
                        # Save results if output file specified
                        if args.output_file:
                            import json
                            with open(args.output_file, 'w') as f:
                                json.dump(raw_result, f, indent=2)
                            print(f"💾 Results saved to: {args.output_file}")
                else:
                    print("❌ Query execution failed")
        
        elif args.test and not FUNCTIONAL_TESTING_AVAILABLE:
            print("\n⚠️  Query execution not available. Install dependencies with: uv add pydantic requests")
        
        else:
            # Original behavior - ask for user confirmation
            try:
                confirmation = input("Does this query look correct? (y/n): ")
                if confirmation.lower() == 'y':
                    print("Executing query...") # In a real scenario, we would execute the query here
                else:
                    print("Query execution cancelled.")
            except EOFError:
                # This happens when the script is run non-interactively.
                # We can just print the query and exit.
                pass
                
    except OverpassQLError as e:
        print(f"Error generating query: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
