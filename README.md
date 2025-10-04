# Overpass QL Generator

A Python-based Overpass QL generator that translates user prompts in natural English into accurate, executable Overpass QL queries. This tool provides both a command-line interface and a web application for easy access.

## Features

*   **Natural Language Input:** The tool accepts prompts like "Find all cafes in Berlin".
*   **Geographic Filtering:** It supports both named areas (e.g., "in Berlin") and bounding boxes (e.g., "in bbox 48.85,2.34,48.86,2.35").
*   **OSM Tag Grounding:** It uses web search to find the appropriate OSM tag for a given feature (e.g., "cafes" -> `amenity=cafe`).
*   **Tag Validation:** It validates the found tag against the OSM taginfo database to ensure it's a valid tag.
*   **Customizable Output Format:** The user can specify the output format (JSON, XML, or GeoJSON) using the `--format` flag.
*   **Formatted Output:** The generated query is well-formatted and includes comments to explain the different parts of the query.
*   **User Confirmation:** The CLI asks the user for confirmation before proceeding, providing a basic form of semantic validation.
*   **Multiple Interfaces:** Offers both a command-line interface and a web application (Streamlit)
*   **Type Safety:** Built with Pydantic models for runtime validation and mypy for static type checking
*   **Comprehensive Validation:** Includes validation for OSM tags, geographic filters, and query syntax

## Installation

### Prerequisites
- Python 3.8 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/your-username/overpass-ql-gen.git
    cd overpass-ql-gen
    ```

2.  Install dependencies using uv (recommended):
    ```bash
    uv sync
    ```

    Or using pip:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Command Line Interface

To run the CLI tool:

```bash
uv run @apps/cli/overpass_cli.py "your prompt" [--format <format>]
```

Or with a virtual environment activated:
```bash
python apps/cli/overpass_cli.py "your prompt" [--format <format>]
```

#### Examples

**Find all cafes in Berlin:**

```bash
uv run @apps/cli/overpass_cli.py "Find all cafes in Berlin"
```

**Find all schools in London in XML format:**

```bash
uv run @apps/cli/overpass_cli.py "Find all schools in London" --format xml
```

**Find all libraries in New York in GeoJSON format:**

```bash
uv run @apps/cli/overpass_cli.py "Find all libraries in New York" --format geojson
```

### Web Application

To run the Streamlit web application:

```bash
uv run streamlit run apps/web/app.py
```

The web app will be accessible at `http://localhost:8501` (or the next available port) and provides a user-friendly interface with:

- Input field for natural language queries
- Output format selection (JSON, XML, GeoJSON)
- Syntax-highlighted query display
- Download button for generated queries
- Example queries for quick testing
- Information about Overpass QL

## Project Structure

```
overpass-ql-gen/
├── apps/                    # Application entry points
│   ├── cli/                # CLI application
│   └── web/                # Web application (Streamlit)
├── src/                    # Source code
│   └── overpass_ql_gen/    # Main package
│       ├── config.py       # Configuration constants
│       ├── __init__.py
│       ├── generator/      # Generator module
│       │   ├── generator.py # Main generator logic
│       │   └── __init__.py
│       └── validation/     # Validation module
│           ├── validator.py # Validation logic
│           └── __init__.py
├── tests/                  # Test files
├── docs/                   # Documentation
├── config.py              # Configuration constants
├── mypy.ini               # MyPy configuration
├── pyproject.toml         # Project configuration
├── README.md
└── CONTRIBUTING.md        # Contribution guidelines
```

## Configuration

The application is configured through the `config.py` file, which includes:

- Common OSM tag mappings for natural language processing
- Output format and element type definitions
- API configuration settings
- Validation configuration
- Overpass QL query templates

## Contributing

We welcome contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project, including development setup, code style, and pull request processes.

## Development

### Running Tests

```bash
uv run pytest
```

### Type Checking

```bash
uv run mypy lib/
```

### Linting

```bash
uv run ruff check .
```

### Formatting

```bash
uv run black .
```

## Limitations

*   **Syntax Validation:** Due to the lack of a suitable Python library for offline Overpass QL parsing, the tool relies on its template-based generation to produce syntactically correct queries.
*   **Execution Simulation:** The tool does not have a dry-run feature to test the query against the Overpass API, as it does not have direct access to the internet to make API calls.
*   **NLP Parsing:** The prompt parsing is based on regular expressions and is relatively simple. It might not handle more complex prompts. A more advanced NLP model would be needed for more robust parsing.

## License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

## Acknowledgments

*   [OpenStreetMap](https://www.openstreetmap.org/) - for providing the map data
*   [Overpass API](https://overpass-api.de/) - for providing the query interface to OSM data
*   [Taginfo](https://taginfo.openstreetmap.org/) - for providing tag validation data
