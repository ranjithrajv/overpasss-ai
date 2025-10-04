
## Prompt for Overpass QL Generator Development

### Objective
Develop a Python-based **Overpass QL generator** that translates user prompts in natural English into accurate, executable Overpass QL queries. The system must ensure **accuracy**, **validation**, and **grounding** by referencing the OpenStreetMap (OSM) data model and schema, and by validating the generated queries against OSM’s structure and syntax.

---

### Key Terms & Definitions
- **Overpass QL:** A query language for querying OpenStreetMap data, used to extract map features based on tags, locations, and relationships.
- **Grounding:** Anchoring the generated Overpass QL to the OSM data model (nodes, ways, relations, tags) to ensure validity and relevance.
- **Validation:** Verifying the generated Overpass QL for syntax errors, logical consistency, and alignment with the user’s intent and OSM’s schema.
- **Accuracy:** The degree to which the generated Overpass QL correctly reflects the user’s request and returns the expected OSM elements.

---

### Requirements

#### 1. Input Handling
- Accept user input as a natural language prompt (e.g., "Find all cafes in Berlin with outdoor seating").
- **Schema Grounding:** Use the OSM wiki and taginfo as the authoritative source for valid OSM tags, keys, and values. If the user’s prompt uses ambiguous or non-standard tags, ask for clarification or suggest standard alternatives.
- **Clarification:** If the prompt is ambiguous, ask clarifying questions (e.g., "Do you want to include restaurants that also serve coffee?").

#### 2. Output Generation
- Generate a syntactically correct Overpass QL query that matches the user’s intent.
- **Grounded Output:** Ensure all tags, keys, and values in the generated query are valid according to OSM’s taginfo and wiki.
- **Query Formatting:** Return the query in a readable, standardized format, with comments explaining each part.

#### 3. Accuracy & Validation
- **Syntax Validation:** Use an Overpass QL parser or the Overpass API’s error responses to check for syntax errors.
- **Semantic Validation:** Verify that the generated query logically matches the user’s intent (e.g., correct use of tags, filters, and area definitions).
- **Tag Validation:** Cross-reference all tags, keys, and values with OSM’s taginfo to prevent the use of deprecated or non-existent tags.
- **Execution Simulation:** Optionally, provide a dry-run feature to test the query against the Overpass API and return a summary of results (without full data).

#### 4. Features
- **OSM Schema Awareness:** Understand OSM’s data model (nodes, ways, relations) and common tagging schemes (e.g., `amenity=cafe`, `highway=residential`).
- **Error Handling:** Provide clear, actionable error messages for invalid prompts, unsupported tags, or syntax errors.
- **Query Optimization:** Generate efficient queries, avoiding overly broad searches (e.g., global queries without area filters).
- **Geographic Filtering:** Support bounding boxes, polygons, and named areas (e.g., cities, countries) in queries.
- **Output Format:** Allow users to specify the output format (e.g., JSON, XML, GeoJSON).

#### 5. Example Workflow
- **User Input:** "Show me all bicycle parking in Paris."
- **System Output:**
  ```ql
  [out:json];
  area[name="Paris"]->.searchArea;
  (
    node["amenity"="bicycle_parking"](area.searchArea);
    way["amenity"="bicycle_parking"](area.searchArea);
    relation["amenity"="bicycle_parking"](area.searchArea);
  );
  out body;
  >;
  out skel qt;
  ```
- **Validation Steps:**
  - Check that "amenity"="bicycle_parking" is a valid OSM tag.
  - Verify that the area "Paris" can be resolved by Overpass.
  - Ensure the query structure is correct and optimized.

#### 6. Deliverables
- A Python script or module with the core Overpass QL generation logic.
- A simple CLI or web interface for user interaction.
- Documentation on how to use the system, including example prompts, expected outputs, and error handling.
- Unit tests for common query types, edge cases, and tag validation.

#### 7. Testing & Grounding
- **Unit Tests:** Include tests for:
  - Valid and invalid prompts.
  - Use of standard and non-standard tags.
  - Geographic filtering and area resolution.
- **Grounding Tests:** Verify that all generated Overpass QL uses only valid OSM tags and syntax.
- **User Feedback Loop:** Allow users to flag incorrect outputs for continuous improvement.

---

### Implementation Instructions
1. **Tag Database:** Maintain a local or cached copy of OSM’s taginfo for quick validation of tags, keys, and values.
2. **Prompt Parsing:** Use NLP (e.g., spaCy, NLTK, or transformers) to extract entities (features, locations, conditions) from the user prompt.
3. **Query Construction:** Map extracted entities to OSM tags and construct the Overpass QL query step-by-step.
4. **Validation Layer:** After query generation, run it through syntax, semantic, and tag validators.
5. **User Feedback:** Provide a mechanism for users to confirm or correct the generated Overpass QL.

---

### Example Validation Output
- **Prompt:** "Find all public libraries in New York City."
- **Generated Overpass QL:**
  ```ql
  [out:json];
  area[name="New York City"]->.searchArea;
  (
    node["amenity"="library"](area.searchArea);
    way["amenity"="library"](area.searchArea);
    relation["amenity"="library"](area.searchArea);
  );
  out body;
  >;
  out skel qt;
  ```
- **Validation Result:**
  - ✅ Syntax: Valid Overpass QL.
  - ✅ Tags: "amenity"="library" is a standard OSM tag.
  - ✅ Area: "New York City" is resolvable by Overpass.


