# Overpass QL Generator

This project is a Python-based Overpass QL generator that translates user prompts in natural English into accurate, executable Overpass QL queries.

## Features

*   **Natural Language Input:** The tool accepts prompts like "Find all cafes in Berlin".
*   **Geographic Filtering:** It supports both named areas (e.g., "in Berlin") and bounding boxes (e.g., "in bbox 48.85,2.34,48.86,2.35").
*   **OSM Tag Grounding:** It uses web search to find the appropriate OSM tag for a given feature (e.g., "cafes" -> `amenity=cafe`).
*   **Tag Validation:** It validates the found tag against the OSM taginfo database to ensure it's a valid tag.
*   **Customizable Output Format:** The user can specify the output format (JSON, XML, or GeoJSON) using the `--format` flag.
*   **Formatted Output:** The generated query is well-formatted and includes comments to explain the different parts of the query.
*   **User Confirmation:** The CLI asks the user for confirmation before proceeding, providing a basic form of semantic validation.
*   **Unit Tests:** The project includes a suite of unit tests with mocking for external services to ensure the core logic is working correctly.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/overpass-ql-gen.git
    ```
2.  Install the dependencies (No external dependencies are required for the core functionality).

## Usage

To run the tool, use the `main.py` script:

```bash
python main.py "your prompt" [--format <format>]
```

### Examples

**Find all cafes in Berlin:**

```bash
python main.py "Find all cafes in Berlin"
```

**Find all bicycle parking in Paris in XML format:**

```bash
python main.py "Find all bicycle parking in Paris" --format xml
```

**Find all restaurants in a specific bounding box:**

```bash
python main.py "Find all restaurants in bbox 48.85,2.34,48.86,2.35"
```

## Limitations

*   **Syntax Validation:** Due to the lack of a suitable Python library for offline Overpass QL parsing, the tool relies on its template-based generation to produce syntactically correct queries.
*   **Execution Simulation:** The tool does not have a dry-run feature to test the query against the Overpass API, as it does not have direct access to the internet to make API calls.
*   **NLP Parsing:** The prompt parsing is based on regular expressions and is relatively simple. It might not handle more complex prompts. A more advanced NLP model would be needed for more robust parsing.
