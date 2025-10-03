import argparse
from generator import generate_query

def main():
    """
    Main function for the Overpass QL generator CLI.
    """
    parser = argparse.ArgumentParser(description="Generate Overpass QL from natural language.")
    parser.add_argument("prompt", type=str, help="The natural language prompt.")
    parser.add_argument("--format", type=str, default="json", choices=["json", "xml", "geojson"], help="The output format.")
    args = parser.parse_args()

    query = generate_query(args.prompt, output_format=args.format)
    print("Generated Overpass QL query:")
    print(query)

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

if __name__ == "__main__":
    main()