import unittest
from unittest.mock import patch, MagicMock
from overpass_ql_gen.oql_generator.generator import (
    parse_prompt,
    generate_query,
    OsmTag,
    ParsedPrompt,
    GeographicFilter,
    BoundingBox,
    ElementType,
    OutputFormat
)

class TestGenerator(unittest.TestCase):
    def test_parse_prompt_cafe_paris(self) -> None:
        """
        Tests the parse_prompt function with a cafe in Paris example.
        """
        prompt = "Find all cafes in Paris"
        result = parse_prompt(prompt)
        
        self.assertEqual(result.location, "Paris")
        self.assertEqual(len(result.tags), 1)
        self.assertEqual(result.tags[0].key, "amenity")
        self.assertEqual(result.tags[0].value, "cafe")

    def test_parse_prompt_parking_berlin(self) -> None:
        """
        Tests the parse_prompt function with parking in Berlin.
        """
        prompt = "Show me all bicycle parking in Berlin"
        result = parse_prompt(prompt)
        
        self.assertEqual(result.location, "Berlin")
        self.assertEqual(len(result.tags), 1)
        self.assertEqual(result.tags[0].key, "amenity")
        self.assertEqual(result.tags[0].value, "parking")  # Simplified for this example

    def test_generate_query_basic(self) -> None:
        """
        Tests the generate_query function basic functionality.
        """
        prompt = "Find all cafes in Paris"
        result = generate_query(prompt, output_format="json")
        
        # Check that the result has the right structure
        self.assertIn("amenity", result.query_string)
        self.assertIn("cafe", result.query_string)
        self.assertIn("Paris", result.query_string)
        self.assertIn("json", result.query_string)

    def test_generate_query_with_xml_format(self) -> None:
        """
        Tests the generate_query function with XML output format.
        """
        prompt = "Find all cafes in London"
        result = generate_query(prompt, output_format="xml")
        
        self.assertIn("amenity", result.query_string)
        self.assertIn("cafe", result.query_string)
        self.assertIn("London", result.query_string)
        self.assertIn("xml", result.query_string)

    def test_parsed_prompt_structure(self) -> None:
        """
        Tests the structure of the ParsedPrompt dataclass.
        """
        tags = [OsmTag(key="amenity", value="cafe")]
        geo_filter = GeographicFilter(area_name="Paris")
        
        parsed = ParsedPrompt(
            elements=["node", "way", "relation"],
            tags=tags,
            location="Paris", 
            area_filter=geo_filter
        )
        
        self.assertEqual(parsed.location, "Paris")
        self.assertEqual(len(parsed.tags), 1)
        self.assertEqual(parsed.tags[0].key, "amenity")

if __name__ == '__main__':
    unittest.main()