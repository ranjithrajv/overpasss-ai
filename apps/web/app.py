#!/usr/bin/env python3
import streamlit as st
import json
import pandas as pd
import requests
from typing import Dict, Any, List, Optional
from overpass_ql_gen.oql_generator.generator import generate_query, OverpassQLError, OutputFormat
from overpass_ql_gen.testing.overpass_functional_tester import OverpassFunctionalTester

# Helper functions for UI elements
def create_json_download_button(response_data: Dict, key_suffix: str = ""):
    """Create a download button for JSON response"""
    json_str = json.dumps(response_data, indent=2)
    st.download_button(
        label="Download JSON Response",
        data=json_str,
        file_name="overpass_response.json",
        mime="application/json",
        key=f"download_response_{key_suffix}"
    )

def create_summary_download_button(summary_text: str, key_suffix: str = ""):
    """Create a download button for summary"""
    st.download_button(
        label="Download Summary",
        data=summary_text,
        file_name="overpass_summary.txt",
        mime="text/plain",
        key=f"download_summary_{key_suffix}"
    )

def create_element_preview(elements: List[Dict]):
    """Create a preview table for the first few elements"""
    if elements:
        with st.expander("Preview First 5 Elements", expanded=True):
            preview_data = []
            for i, elem in enumerate(elements[:5]):  # Show first 5 elements
                preview_data.append({
                    'id': elem.get('id', 'N/A'),
                    'type': elem.get('type', 'N/A'),
                    'tags_count': len(elem.get('tags', {})),
                    'first_tag': list(elem.get('tags', {}).keys())[0] if elem.get('tags') else 'N/A'
                })
            
            df = pd.DataFrame(preview_data)
            st.dataframe(df, use_container_width=True)

# Set page configuration
st.set_page_config(
    page_title="Overpass QL Generator",
    page_icon="🗺️",
    layout="wide"
)

# Add sidebar for AI service tokens
with st.sidebar:
    st.header("AI Service Configuration")

    # Selected AI service
    selected_service = st.selectbox(
        "Select AI Service",
        ["Basic Summary (No API Key)", "OpenAI GPT", "Google Gemini", "Anthropic Claude"],
        help="Choose which AI service to use for generating summaries"
    )

    # Initialize API keys
    openai_api_key = ""
    gemini_api_key = ""
    claude_api_key = ""

    # Show API key input based on selected service
    if selected_service == "OpenAI GPT":
        openai_api_key = st.text_input("OpenAI API Key", type="password",
                                       help="Enter your OpenAI API key to use GPT models for summaries")
    elif selected_service == "Google Gemini":
        gemini_api_key = st.text_input("Google Gemini API Key", type="password",
                                       help="Enter your Google Gemini API key to use Gemini models for summaries")
    elif selected_service == "Anthropic Claude":
        claude_api_key = st.text_input("Anthropic Claude API Key", type="password",
                                       help="Enter your Anthropic Claude API key to use Claude models for summaries")

    st.divider()

    # Information about API keys (only show if an AI service is selected)
    if selected_service != "Basic Summary (No API Key)":
        st.info("API keys are stored in memory during your session and are never saved to disk or sent to any server except the AI service providers.")
    
    st.divider()
    
    # Advanced settings
    st.subheader("Settings")
    summary_detail_level = st.slider(
        "Summary Detail Level", 
        min_value=1, 
        max_value=5, 
        value=3,
        help="Higher values produce more detailed summaries"
    )
    
    enable_advanced_analysis = st.checkbox(
        "Enable Advanced Analysis", 
        value=False,
        help="Enable more sophisticated analysis of the OSM data"
    )

# Title and description
st.title("🗺️ Overpass QL Generator")
st.markdown("""
This application translates natural language prompts into Overpass QL queries.
Enter your request in plain English and get the corresponding Overpass query.
""")

# Input section
st.header("Enter your request")

# Initialize selected_example in session state if not exists
if 'selected_example' not in st.session_state:
    st.session_state['selected_example'] = None

# Use session state value if an example was selected
if st.session_state['selected_example']:
    user_input = st.text_input(
        "Natural language request:",
        value=st.session_state['selected_example'],
        placeholder="e.g., Find all cafes in Paris, Show me bicycle parking in Berlin...",
        help="Describe what OpenStreetMap features you want to query"
    )
    # Clear the selected example after displaying
    st.session_state['selected_example'] = None
else:
    user_input = st.text_input(
        "Natural language request:",
        placeholder="e.g., Find all cafes in Paris, Show me bicycle parking in Berlin...",
        help="Describe what OpenStreetMap features you want to query"
    )

# Example requests - show only if no user input
if not user_input:
    st.markdown("**Or try an example:**")
    examples = [
        "Find all cafes in Paris",
        "Show me bicycle parking in Berlin",
        "Find all libraries in New York",
        "Show me bus stops in London",
        "Find all restaurants in Tokyo with outdoor seating",
        "Show me parks in Rome"
    ]

    cols = st.columns(3)
    for idx, example in enumerate(examples):
        with cols[idx % 3]:
            if st.button(example, key=f"example_{idx}", use_container_width=True):
                st.session_state['selected_example'] = example
                st.rerun()

# Output format selection
output_format = st.selectbox(
    "Output format:",
    options=["json", "xml", "geojson"],
    index=0,
    help="Choose the output format for the Overpass API"
)

# Auto-generate query when user enters text
if user_input and len(user_input.strip()) >= 5:
    # Check if we need to regenerate (input or format changed)
    should_generate = (
        'last_user_input' not in st.session_state or
        st.session_state['last_user_input'] != user_input or
        'last_output_format' not in st.session_state or
        st.session_state['last_output_format'] != output_format
    )

    if should_generate:
        try:
            with st.spinner("Generating Overpass QL query..."):
                # Explicitly cast to the expected literal type
                from typing import cast
                from overpass_ql_gen.oql_generator.generator import OutputFormat
                format_literal = cast(OutputFormat, output_format)
                query_result = generate_query(user_input, output_format=format_literal)

                # Store query result and inputs in session state
                st.session_state['query_result'] = query_result
                st.session_state['last_user_input'] = user_input
                st.session_state['last_output_format'] = output_format

            st.success("Query generated successfully!")

        except OverpassQLError as e:
            st.error(f"Error generating query: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
elif user_input and len(user_input.strip()) < 5:
    st.warning("Please enter at least 5 characters to generate a query.")

# Display query if it exists in session state
if 'query_result' in st.session_state:
    query_result = st.session_state['query_result']

    # Display the generated query
    st.header("Generated Overpass QL Query")
    st.code(query_result.query_string, language="overpassql")

    # Action buttons in columns
    col_copy, col_execute = st.columns([1, 1])

    with col_copy:
        if st.button("📋 Copy Query", key="copy_query", use_container_width=True):
            st.write("Query copied to clipboard!")
            # Using st.code with a hidden container to enable copying
            st.components.v1.html(
                f"""
                <script>
                navigator.clipboard.writeText(`{query_result.query_string.replace('`', '\\`')}`);
                </script>
                """,
                height=0
            )

    with col_execute:
        execute_clicked = st.button("▶️ Execute Query", key="execute_query", type="secondary", use_container_width=True)

    # Additional info
    st.info(f"""
    **Query details:**
    - Output format: `{query_result.output_format if hasattr(query_result, 'output_format') else 'json'}`
    - Search area: `{query_result.search_area or 'Global (no specific area)'}`
    - Tags used: `{[f'{tag.key}={tag.value}' for tag in query_result.tags]}`
    - Elements: `{query_result.elements}`
    """)

# Add section for executing query and displaying JSON response
if 'query_result' in st.session_state and 'execute_clicked' in locals() and execute_clicked:
    with st.spinner("Executing query against Overpass API..."):
        try:
            # Get the generated query string
            query_string = st.session_state['query_result'].query_string

            # Execute the query using direct API call to avoid rate limiting issues
            response = requests.post(
                'https://overpass-api.de/api/interpreter',
                data=query_string,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            # Store the response in session state
            st.session_state['api_response'] = result

            # Display success message and response
            st.success("Query executed successfully!")

            # Show response statistics
            elements = result.get('elements', [])
            st.info(f"**Response Statistics:** {len(elements)} elements returned")

            # Display JSON response in an expander
            with st.expander("View Raw JSON Response", expanded=False):
                st.json(result)

            # Show a preview of the first few elements in a table
            create_element_preview(elements)

            # Add download button for JSON response
            create_json_download_button(result, "new")

        except requests.exceptions.HTTPError as e:
            st.error(f"HTTP Error executing query: {e}. Status code: {response.status_code}")
            st.error(f"Response text: {response.text[:500]}...")  # First 500 chars
        except requests.exceptions.Timeout:
            st.error("Request timed out. The query might be too complex for the Overpass API.")
        except requests.exceptions.RequestException as e:
            st.error(f"Network error executing query: {e}")
        except json.JSONDecodeError:
            st.error("Invalid JSON response from the Overpass API.")
            st.error(f"Response text: {response.text[:500]}...")  # First 500 chars
        except Exception as e:
            st.error(f"Unexpected error executing query: {e}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")

# Display stored response if available
if 'api_response' in st.session_state:
    st.subheader("Latest API Response")
    response = st.session_state['api_response']
    elements = response.get('elements', [])
    st.info(f"**Response Statistics:** {len(elements)} elements returned")

    with st.expander("View Raw JSON Response", expanded=False):
        st.json(response)

    # Show a preview of the first few elements in a table
    create_element_preview(elements)

    # Add download button for JSON response
    create_json_download_button(response, "existing")

# AI Summary section - only show if API response exists
if 'api_response' in st.session_state:
    st.header("AI-Powered Summary")

    # Create functions to interact with different AI services
    def call_openai_api(api_key: str, prompt: str) -> Optional[str]:
        """Call OpenAI API to generate a summary"""
        if not api_key:
            return None

        try:
            import openai
            client = openai.OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in analyzing OpenStreetMap data. Provide a clear, concise summary of the OSM elements with focus on the most interesting insights about the geographic features."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.5
            )

            return response.choices[0].message.content
        except Exception as e:
            st.error(f"Error calling OpenAI API: {e}")
            return None

    def call_gemini_api(api_key: str, prompt: str) -> Optional[str]:
        """Call Google Gemini API to generate a summary"""
        if not api_key:
            return None

        try:
            import google.generativeai as genai

            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')

            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.error(f"Error calling Gemini API: {e}")
            return None

    def call_claude_api(api_key: str, prompt: str) -> Optional[str]:
        """Call Anthropic Claude API to generate a summary"""
        if not api_key:
            return None

        try:
            import anthropic

            client = anthropic.Anthropic(api_key=api_key)

            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                temperature=0.5,
                system="You are an expert in analyzing OpenStreetMap data. Provide a clear, concise summary of the OSM elements with focus on the most interesting insights about the geographic features.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text
        except Exception as e:
            st.error(f"Error calling Claude API: {e}")
            return None

    # Create a function to generate AI summary of the JSON response
    def generate_response_summary(response_data: Dict[str, Any], query_info: str = "",
                                service_type: str = "basic", api_key: str = "") -> str:
        """
        Generate an AI summary of the Overpass API response using selected service
        """
        elements = response_data.get('elements', [])
        
        if not elements:
            return "No elements found in the response."
        
        # Prepare basic statistics for use in both basic and AI summaries
        total_elements = len(elements)
        
        # Count element types
        node_count = sum(1 for elem in elements if elem.get('type') == 'node')
        way_count = sum(1 for elem in elements if elem.get('type') == 'way')
        relation_count = sum(1 for elem in elements if elem.get('type') == 'relation')
        
        # Get common tags
        tag_counts = {}
        for elem in elements:
            tags = elem.get('tags', {})
            for key, value in tags.items():
                tag_key = f"{key}={value}"
                tag_counts[tag_key] = tag_counts.get(tag_key, 0) + 1
        
        # Get top tags
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_tags_str = ", ".join([f"{tag} ({count})" for tag, count in sorted_tags])
        
        # Get the search area
        search_area = st.session_state.get('query_result', {}).search_area or 'unknown location'
        
        # If using basic summary, return the local analysis
        if service_type == "basic":
            summary = f"""
## Summary of OSM Data Query Results

**Query**: {query_info or 'OSM Query Results'}
**Location**: {search_area}
**Total Elements Found**: {total_elements}

### Breakdown by Type:
- Nodes: {node_count}
- Ways: {way_count} 
- Relations: {relation_count}

### Common Features:
{top_tags_str}

### Analysis:
This OSM query returned {total_elements} elements in {search_area}. 
The most common features in this dataset are represented by the tags: {top_tags_str.split(',')[0] if top_tags_str else 'no specific tags'}.
The data includes {node_count} point features, {way_count} line/polygon features, and {relation_count} complex features.
"""
            return summary.strip()
        
        # For AI services, create a detailed prompt
        else:
            prompt = f"""
Analyze this OpenStreetMap query result and provide a comprehensive summary.

Query Information:
- Search Query: {query_info or 'OSM Query Results'}
- Location: {search_area}
- Total Elements: {total_elements}

Data Overview:
- Nodes (points): {node_count}
- Ways (lines/polygons): {way_count}
- Relations (complex features): {relation_count}

Common Tags: {top_tags_str}

Please provide:
1. A high-level summary of what type of features were found
2. The geographic distribution and density of features
3. Any interesting patterns or insights about the data
4. Recommendations for potential uses of this data

Keep the response concise but informative.
"""
            
            # Call the appropriate API based on service type
            if service_type == "openai" and api_key:
                result = call_openai_api(api_key, prompt)
                if result:
                    return f"## OpenAI-Generated Summary\n\n{result}"
                
            elif service_type == "gemini" and api_key:
                result = call_gemini_api(api_key, prompt)
                if result:
                    return f"## Gemini-Generated Summary\n\n{result}"
                
            elif service_type == "claude" and api_key:
                result = call_claude_api(api_key, prompt)
                if result:
                    return f"## Claude-Generated Summary\n\n{result}"
            
            # If API call failed, fall back to basic summary
            st.warning(f"AI service request failed. Using basic summary instead.")
            summary = f"""
## Summary of OSM Data Query Results

**Query**: {query_info or 'OSM Query Results'}
**Location**: {search_area}
**Total Elements Found**: {total_elements}

### Breakdown by Type:
- Nodes: {node_count}
- Ways: {way_count} 
- Relations: {relation_count}

### Common Features:
{top_tags_str}

### Analysis:
This OSM query returned {total_elements} elements in {search_area}. 
The most common features in this dataset are represented by the tags: {top_tags_str.split(',')[0] if top_tags_str else 'no specific tags'}.
The data includes {node_count} point features, {way_count} line/polygon features, and {relation_count} complex features.
"""
            return summary.strip()

    # Button to generate AI summary
    if st.button("Generate AI Summary", type="primary"):
        with st.spinner("Analyzing the response with AI..."):
            try:
                response_data = st.session_state['api_response']
                query_info = st.session_state.get('query_result', {}).query_string or ""

                # Determine which service to use based on sidebar selection
                service_map = {
                    "Basic Summary (No API Key)": "basic",
                    "OpenAI GPT": "openai",
                    "Google Gemini": "gemini",
                    "Anthropic Claude": "claude"
                }
                service_type = service_map.get(selected_service, "basic")

                # Get the appropriate API key based on the selected service
                if service_type == "openai":
                    api_key = openai_api_key
                elif service_type == "gemini":
                    api_key = gemini_api_key
                elif service_type == "claude":
                    api_key = claude_api_key
                else:
                    api_key = ""  # No API key needed for basic summary

                summary = generate_response_summary(response_data, query_info, service_type, api_key)

                # Store the summary in session state
                st.session_state['ai_summary'] = summary

                # Display the summary
                st.subheader("AI Summary")
                st.markdown(summary)

                # Add download button for the summary
                create_summary_download_button(summary, "new")

            except Exception as e:
                st.error(f"Error generating AI summary: {e}")
                import traceback
                st.error(f"Traceback: {traceback.format_exc()}")

    # Display stored summary if available
    if 'ai_summary' in st.session_state:
        st.subheader("Latest AI Summary")
        st.markdown(st.session_state['ai_summary'])

        # Add download button for the summary
        create_summary_download_button(st.session_state['ai_summary'], "existing")

# Add some information about Overpass QL
with st.expander("About Overpass QL"):
    st.markdown("""
    **Overpass QL** is a query language for the OpenStreetMap (OSM) database.
    
    - It allows you to extract specific map features based on tags, locations, and relationships
    - Queries can target specific OSM elements (nodes, ways, relations)
    - You can filter by location, tags, and other attributes
    - Results can be returned in various formats (JSON, XML, etc.)
    
    This tool translates natural language into valid Overpass QL queries.
    """)