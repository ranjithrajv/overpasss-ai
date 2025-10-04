# Overpass QL Generator

A Python-based Overpass QL generator that translates user prompts in natural English into accurate, executable Overpass QL queries. This tool provides both a command-line interface and a web application for easy access.

## Features

### Core Functionality
*   **Natural Language to Overpass QL:** Translates plain English prompts into executable Overpass QL queries
*   **Geographic Filtering:** Supports named areas ("in Berlin") and bounding boxes ("in bbox 48.85,2.34,48.86,2.35")
*   **OSM Tag Grounding:** Automatically finds appropriate OSM tags for features (e.g., "cafes" → `amenity=cafe`)
*   **Tag Validation:** Validates tags against the OSM taginfo database
*   **Multiple Output Formats:** JSON, XML, and GeoJSON support

### Query Generation & Execution
*   **Auto-generated Queries:** Real-time query generation as you type
*   **Formatted Output:** Well-structured queries with explanatory comments
*   **Direct API Execution:** Execute queries against Overpass API directly from the web interface
*   **Response Visualization:** Preview and analyze returned OSM data
*   **Copy to Clipboard:** One-click query copying for external use
*   **Download Responses:** Save JSON responses locally

### AI-Powered Analysis
*   **Multi-Provider AI Summaries:** Support for OpenAI GPT, Google Gemini, and Anthropic Claude
*   **Basic Summary Mode:** Built-in statistical analysis without API keys
*   **Response Analysis:** Automatic analysis of OSM query results with insights
*   **Configurable Detail Levels:** Adjustable summary depth and advanced analysis options
*   **Downloadable Summaries:** Export AI-generated summaries as text files

### User Interfaces
*   **Command-Line Interface:** Lightweight CLI for terminal-based workflows
*   **Web Application:** Full-featured Streamlit interface with visual feedback
*   **Example Queries:** Pre-built examples for quick testing
*   **Interactive UI:** Real-time validation and auto-generation

### Development & Quality
*   **Type Safety:** Built with Pydantic models for runtime validation and mypy for static type checking
*   **Comprehensive Validation:** OSM tags, geographic filters, and query syntax validation
*   **Functional Testing:** Automated testing framework for query validation
*   **Test Coverage:** pytest-based test suite with coverage reporting

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
