# Streamlit Web Application Tutorial

This tutorial provides step-by-step instructions for using the Overpass QL Generator web application.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Basic Query Generation](#basic-query-generation)
3. [Using Example Queries](#using-example-queries)
4. [Executing Queries](#executing-queries)
5. [AI-Powered Analysis](#ai-powered-analysis)
6. [Advanced Configuration](#advanced-configuration)
7. [Downloading Results](#downloading-results)

---

## Getting Started

### Step 1: Launch the Application

Open your terminal and navigate to the project directory:

```bash
cd /path/to/overpass-ai
```

> **💡 Helper:** Replace `/path/to/overpass-ai` with the actual path where you cloned the repository.

Start the Streamlit application:

```bash
uv run streamlit run apps/web/app.py
```

> **💡 Helper:** If you don't have `uv` installed, you can use: `streamlit run apps/web/app.py` after activating your virtual environment.

The application will open in your default browser at `http://localhost:8501`.

> **💡 Helper:** If the browser doesn't open automatically, manually navigate to the URL shown in the terminal output.

### Step 2: Understand the Interface

The web interface consists of:
- **Sidebar (Left)**: AI service configuration and settings
- **Main Area (Center)**: Query input, generated query display, and results
- **Expandable Sections**: Additional information and raw data views

---

## Basic Query Generation

### Step 3: Enter a Natural Language Query

1. Locate the **"Natural language request"** input field in the main area
2. Type your query in plain English, for example:
   ```
   Find all cafes in Paris
   ```
   > **💡 Helper:** Use natural language like you're asking a person. Include the feature type (cafes, restaurants, parks) and location (city name, country, or region).

3. The query must be at least 5 characters long
   > **💡 Helper:** If you see "Please enter at least 5 characters", just type a few more words to describe what you're looking for.

4. The application will automatically generate the Overpass QL query as you type
   > **💡 Helper:** No need to click "Generate" - the query updates automatically once you stop typing for a moment.

### Step 4: Select Output Format

Below the input field, choose your preferred output format:
- **JSON** (default): JavaScript Object Notation - best for general data processing and APIs
- **XML**: Extensible Markup Language - useful for legacy systems
- **GeoJSON**: Geographic JSON for mapping applications - perfect for use with Leaflet, Mapbox, or other mapping libraries

> **💡 Helper:** If you're unsure, stick with **JSON** (the default). It's the most widely supported format and works well for most use cases.

### Step 5: View Generated Query

Once generated, the query appears in a code block with syntax highlighting. You'll also see:
- **Query details**: Output format, search area, OSM tags used, and element types
- **Action buttons**: Copy Query and Execute Query

> **💡 Helper:** The generated query is actual Overpass QL code that you can copy and run anywhere, including [Overpass Turbo](https://overpass-turbo.eu/).

**Example Generated Query:**
```overpassql
[out:json][timeout:25];
area["name"="Paris"]->.searchArea;
(
  node["amenity"="cafe"](area.searchArea);
  way["amenity"="cafe"](area.searchArea);
  relation["amenity"="cafe"](area.searchArea);
);
out body;
>;
out skel qt;
```

> **💡 Helper:** Understanding the query:
> - `[out:json]` sets the output format
> - `area["name"="Paris"]` finds the geographic area
> - `node["amenity"="cafe"]` searches for cafes (as points)
> - `way["amenity"="cafe"]` searches for cafes (as buildings/areas)
> - `out body` returns the full data for each element

---

## Using Example Queries

### Step 6: Try Pre-built Examples

If you're new or want to test the application quickly:

> **💡 Helper:** Examples are a great way to learn the query syntax without typing. They demonstrate different types of features and locations.

1. Leave the input field **empty**
2. Scroll down to see **"Or try an example:"**
3. Click any example button:
   - Find all cafes in Paris
   - Show me bicycle parking in Berlin
   - Find all libraries in New York
   - Show me bus stops in London
   - Find all restaurants in Tokyo with outdoor seating
   - Show me parks in Rome

4. The selected example will populate the input field and generate a query automatically

> **💡 Helper:** After clicking an example, you can modify the text in the input field to customize it for your needs.

---

## Executing Queries

### Step 7: Execute Against Overpass API

1. After generating a query, click the **"▶️ Execute Query"** button

> **💡 Helper:** This button sends your query to the public Overpass API server at `https://overpass-api.de/api/interpreter`. Make sure you have an internet connection.

2. Wait for the spinner: *"Executing query against Overpass API..."*

> **💡 Helper:** Query execution can take anywhere from 2 seconds to 60 seconds depending on:
> - The size of the geographic area
> - The number of features found
> - Current server load
> - Network speed

3. The application sends your query to the Overpass API and retrieves results

> **⚠️ Important:** The Overpass API has rate limits. If you get an error about "too many requests", wait 1-2 minutes before trying again.

### Step 8: View Results

Once execution completes, you'll see:

#### Response Statistics
```
Response Statistics: 156 elements returned
```

#### Element Preview Table
A table showing the first 5 elements with:
- **ID**: Element identifier (unique OSM ID)
- **Type**: Node (point), way (line/area), or relation (complex feature)
- **Tags Count**: Number of tags on the element
- **First Tag**: The first tag key in the element

> **💡 Helper:**
> - **Nodes** are single points (like a bench or a tree)
> - **Ways** are connected points forming lines or areas (like roads or buildings)
> - **Relations** are groups of elements (like a bus route or multi-part building)

#### Raw JSON Response
Click **"View Raw JSON Response"** to expand and see the complete API response.

> **💡 Helper:** The raw JSON contains all the data returned by Overpass API, including coordinates, tags, and metadata. This is useful for debugging or if you need the complete dataset.

**Example Response Structure:**
```json
{
  "version": 0.6,
  "generator": "Overpass API",
  "elements": [
    {
      "type": "node",
      "id": 123456789,
      "lat": 48.8566,
      "lon": 2.3522,
      "tags": {
        "amenity": "cafe",
        "name": "Café de Flore"
      }
    }
  ]
}
```

---

## AI-Powered Analysis

### Step 9: Configure AI Service (Optional)

In the **left sidebar**, you can configure AI analysis:

> **💡 Helper:** AI services provide intelligent summaries of your query results, identifying patterns, insights, and recommendations. The Basic Summary works without any setup!

1. **Select AI Service** from the dropdown:
   - **Basic Summary (No API Key)**: Uses built-in statistical analysis - works offline, no cost
   - **OpenAI GPT**: Requires OpenAI API key - uses GPT-3.5-turbo model
   - **Google Gemini**: Requires Google Gemini API key - uses Gemini 1.5 Flash model
   - **Anthropic Claude**: Requires Anthropic Claude API key - uses Claude 3 Haiku model

> **💡 Helper:** Need an API key?
> - **OpenAI**: Get one at https://platform.openai.com/api-keys
> - **Google Gemini**: Get one at https://aistudio.google.com/app/apikey
> - **Anthropic Claude**: Get one at https://console.anthropic.com/

2. If you selected an AI service (not Basic Summary):
   - Enter your API key in the password field that appears
   - Your key is stored in memory only during the session
   - It's never saved to disk

> **🔒 Security:** API keys are only sent to the respective AI provider (OpenAI, Google, or Anthropic). They are never stored permanently or shared with third parties.

### Step 10: Generate AI Summary

After executing a query:

1. Scroll down to the **"AI-Powered Summary"** section
2. Click the **"Generate AI Summary"** button

> **💡 Helper:** You must execute a query first (Step 7) before you can generate a summary. The summary analyzes the actual results returned by the API.

3. Wait for the analysis to complete

> **💡 Helper:** Analysis time varies:
> - Basic Summary: Instant (< 1 second)
> - AI Services: 5-15 seconds depending on the service and response size

### Step 11: Review AI Summary

The summary includes:

**For Basic Summary:**
- Query information and location
- Total elements found
- Breakdown by type (nodes, ways, relations)
- Common features and tags
- Basic analysis of the dataset

**For AI Services (GPT, Gemini, Claude):**
- High-level summary of features found
- Geographic distribution and density analysis
- Interesting patterns and insights
- Recommendations for data usage

**Example AI Summary:**
```markdown
## Summary of OSM Data Query Results

**Query**: Find all cafes in Paris
**Location**: Paris
**Total Elements Found**: 156

### Breakdown by Type:
- Nodes: 142
- Ways: 14
- Relations: 0

### Common Features:
amenity=cafe (156), name=* (145), outdoor_seating=yes (67)

### Analysis:
This OSM query returned 156 elements in Paris. The most common
features are cafes with outdoor seating capabilities...
```

---

## Advanced Configuration

### Step 12: Adjust Summary Settings

In the **sidebar under "Settings"**:

1. **Summary Detail Level** (slider 1-5):
   - Level 1: Brief overview
   - Level 3: Balanced detail (default)
   - Level 5: Comprehensive analysis

> **💡 Helper:** Currently this setting is for future use. All summaries use a balanced detail level regardless of the slider position.

2. **Enable Advanced Analysis** (checkbox):
   - Check to enable more sophisticated data analysis
   - Useful for complex datasets

> **💡 Helper:** This setting is for future use and doesn't affect current summaries. Leave it unchecked for now.

---

## Downloading Results

### Step 13: Download Query

1. Click **"📋 Copy Query"** to copy the Overpass QL query to your clipboard

> **💡 Helper:** The query is automatically copied. Look for the confirmation message "Query copied to clipboard!" Your browser might request clipboard permissions the first time.

2. Paste it into the [Overpass Turbo](https://overpass-turbo.eu/) web interface or your own application

> **💡 Helper:** Overpass Turbo is a web-based tool where you can run queries and visualize results on a map. Perfect for testing and refinement!

### Step 14: Download JSON Response

After executing a query:

1. Locate the **"Download JSON Response"** button
2. Click it to download the complete API response
3. File saved as: `overpass_response.json`

> **💡 Helper:** The downloaded JSON file can be:
> - Imported into GIS software (QGIS, ArcGIS)
> - Processed with Python, JavaScript, or other programming languages
> - Used for data analysis in tools like Excel or Google Sheets (with conversion)

### Step 15: Download AI Summary

After generating an AI summary:

1. Locate the **"Download Summary"** button
2. Click it to download the summary text
3. File saved as: `overpass_summary.txt`

> **💡 Helper:** The summary is in plain text format with markdown formatting. You can:
> - Open it in any text editor
> - View it as formatted markdown in VS Code, GitHub, or markdown viewers
> - Include it in reports or documentation

---

## Complete Workflow Example

### Example: Finding Restaurants in London

> **💡 Helper:** This example walks through the entire process from start to finish. Follow along to see how all the features work together.

**Step 1:** Launch the application
```bash
uv run streamlit run apps/web/app.py
```

**Step 2:** Enter query
```
Find all restaurants in London
```
> **💡 Helper:** Notice how the query auto-generates after you stop typing for a moment.

**Step 3:** Select format
- Choose **GeoJSON** from the dropdown

> **💡 Helper:** GeoJSON is perfect if you plan to visualize the results on a map later.

**Step 4:** Review generated query
- Check the query details showing `amenity=restaurant` and search area `London`

> **💡 Helper:** Verify that the tool correctly identified "restaurants" → `amenity=restaurant` and "London" as the search area.

**Step 5:** Execute the query
- Click **"▶️ Execute Query"**
- Wait for results (may take 10-30 seconds)

> **💡 Helper:** London has many restaurants, so this query might return 1000+ results and take up to 60 seconds.

**Step 6:** Analyze results
- View the element preview table
- Expand the raw JSON response to see all data

> **💡 Helper:** The preview shows only 5 elements. Download the full JSON to see all results.

**Step 7:** Configure AI (optional)
- Select **"OpenAI GPT"** in the sidebar
- Enter your API key

> **💡 Helper:** Skip this if you don't have an API key - the Basic Summary works great too!

**Step 8:** Generate summary
- Click **"Generate AI Summary"**
- Review the AI-generated insights

> **💡 Helper:** The AI might identify patterns like "Most restaurants are concentrated in the city center" or "Italian cuisine is most common".

**Step 9:** Download everything
- Download the query
- Download the JSON response
- Download the AI summary

> **💡 Helper:** Now you have everything saved locally for further analysis, reporting, or mapping!

---

## Troubleshooting

### Query Generation Fails
- **Issue**: "Please enter at least 5 characters"
- **Solution**: Type a longer query with more descriptive text

> **💡 Helper:** The minimum is 5 characters to ensure meaningful queries. Try "Find cafes in Paris" instead of "cafe".

### Query Execution Timeout
- **Issue**: "Request timed out"
- **Solution**: The query is too complex. Try narrowing the geographic area or using more specific tags

> **💡 Helper:** Common causes:
> - Searching entire countries (try cities instead)
> - Very generic features (try specific tags like "restaurants" not "food")
> - Server is overloaded (wait and try again)

### AI Summary Fails
- **Issue**: "Error calling [Service] API"
- **Solution**:
  - Check your API key is correct
  - Verify you have API credits
  - Try the "Basic Summary" option instead

> **💡 Helper:** Test your API key:
> - **OpenAI**: Visit https://platform.openai.com/usage to check credits
> - **Gemini**: Ensure you have quota at https://aistudio.google.com/
> - **Claude**: Check your usage at https://console.anthropic.com/

### No Elements Returned
- **Issue**: "0 elements returned"
- **Solution**:
  - The location may not exist in OSM
  - Try a different location or feature type
  - Check the generated query for accuracy

> **💡 Helper:** Common reasons for zero results:
> - Location name misspelled or doesn't exist in OSM
> - Feature doesn't exist in that area (e.g., "ski resorts in Miami")
> - OSM data is incomplete for that region
> - Try viewing the query in [Overpass Turbo](https://overpass-turbo.eu/) to verify

### App Won't Start
- **Issue**: Application fails to launch or shows errors
- **Solution**:
  - Ensure all dependencies are installed: `uv sync`
  - Check Python version is 3.12 or higher: `python --version`
  - Try clearing Streamlit cache: `streamlit cache clear`

> **💡 Helper:** If you see "ModuleNotFoundError", run `uv sync` to install missing dependencies.

---

## Tips and Best Practices

1. **Start Simple**: Begin with basic queries like "Find cafes in Paris" before attempting complex queries

> **💡 Helper:** Simple queries help you understand the tool's behavior and the structure of OSM data before tackling complex searches.

2. **Use Examples**: The pre-built examples demonstrate the query syntax and expected inputs

> **💡 Helper:** Click through all the examples to see different query styles and learn what kinds of searches work well.

3. **Check Query Details**: Always review the query details to ensure correct tags and location

> **💡 Helper:** The tool shows what OSM tags it chose. If it picked the wrong tag (e.g., `shop=bakery` when you wanted `craft=bakery`), you can manually edit the query.

4. **Experiment with Formats**: Try different output formats (JSON, XML, GeoJSON) for different use cases

> **💡 Helper:** Format recommendations:
> - **JSON**: Best for APIs, web applications, data processing
> - **XML**: Required by some legacy systems and tools
> - **GeoJSON**: Essential for web maps (Leaflet, Mapbox, OpenLayers)

5. **Save Your Work**: Download responses and summaries for offline analysis

> **💡 Helper:** Download files immediately after execution. Session state is cleared when you close the browser or refresh the page.

6. **API Key Security**: Never share your API keys or commit them to version control

> **💡 Helper:** Best practices:
> - Don't screenshot the sidebar with API keys visible
> - Don't paste API keys in chat, email, or public forums
> - Rotate keys regularly if they might be compromised

7. **Rate Limiting**: The Overpass API has rate limits. Wait between consecutive queries

> **💡 Helper:** Overpass API limits:
> - Maximum 2 concurrent queries
> - Complex queries may have cooldown periods
> - If you hit limits, wait 60-120 seconds before retrying

8. **Geographic Specificity**: More specific locations (e.g., "Berlin" vs "Germany") return faster results

> **💡 Helper:** Query performance hierarchy (fastest to slowest):
> - Neighborhoods: "Find cafes in Kreuzberg, Berlin" (fastest)
> - Cities: "Find cafes in Berlin" (fast)
> - Regions: "Find cafes in Brandenburg" (slow)
> - Countries: "Find cafes in Germany" (very slow, may timeout)

---

## Additional Resources

- **Overpass QL Documentation**: https://wiki.openstreetmap.org/wiki/Overpass_API
  > **💡 Helper:** Comprehensive guide to Overpass QL syntax, filters, and advanced features

- **Overpass Turbo**: https://overpass-turbo.eu/ (interactive query builder)
  > **💡 Helper:** Web-based IDE for writing and testing Overpass queries with live map visualization

- **OSM Taginfo**: https://taginfo.openstreetmap.org/ (explore OSM tags)
  > **💡 Helper:** Search for OSM tags to understand their usage frequency and find the right tags for your queries

- **Project Repository**: Check the README for installation and configuration details
  > **💡 Helper:** Full documentation, contribution guidelines, and source code

- **OSM Wiki**: https://wiki.openstreetmap.org/
  > **💡 Helper:** Learn about OSM tagging conventions, map features, and best practices

---

## Quick Reference Card

### Common Query Patterns
```
Find all [FEATURE] in [LOCATION]
Show me [FEATURE] in [LOCATION]
Get [FEATURE] from [LOCATION]
List all [FEATURE] in [LOCATION]
```

### Supported Features (Examples)
- Amenities: cafes, restaurants, banks, hospitals, schools, libraries
- Tourism: hotels, museums, attractions, viewpoints
- Transport: bus stops, train stations, bicycle parking, parking lots
- Natural features: parks, forests, water bodies, beaches

### Supported Locations
- Cities: "Paris", "New York", "Tokyo"
- Countries: "France", "USA", "Japan"
- Regions: "Bavaria", "California", "Île-de-France"
- Neighborhoods: "Manhattan", "Shibuya"

### Keyboard Shortcuts
- **Ctrl+Enter** (in input field): Trigger query generation
- **Ctrl+C**: Copy selected query text
- **F5**: Refresh the page (clears session state)

---

## Next Steps

After mastering the web interface:

1. **Try the CLI Tool**: Use the [command-line interface](../README.md#command-line-interface) for scripting and automation

> **💡 Helper:** The CLI is perfect for batch processing multiple queries or integrating with other tools and scripts.

2. **Explore the Codebase**: Understand the [project structure](../README.md#project-structure) and how queries are generated

> **💡 Helper:** Learn how the natural language processing works and how you can customize or extend the tool.

3. **Contribute**: Share improvements via the [contribution guidelines](../CONTRIBUTING.md)

> **💡 Helper:** Found a bug? Have an idea for a feature? Contributions are welcome! Check the guidelines to get started.

4. **Join the Community**: Connect with other OpenStreetMap and Overpass API users

> **💡 Helper:** Resources:
> - OSM Community Forum: https://community.openstreetmap.org/
> - OSM Help Site: https://help.openstreetmap.org/
> - Overpass API Mailing List: https://listes.openstreetmap.fr/wws/info/overpass

---

**Happy Mapping! 🗺️**

> **💡 Final Helper:** Remember, OpenStreetMap is built by volunteers. If you find missing or incorrect data, consider [contributing to OSM](https://www.openstreetmap.org/fixthemap) to help improve the map for everyone!
