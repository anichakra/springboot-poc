import json
import sys

MODULE_CONFIG = "module-config"

def read_config():
    """
    Parses a JSON configuration from command-line arguments.

    This function reads a JSON input from the first command-line argument. The input can either
    be a file path pointing to a JSON file or a JSON-formatted string. In case of a JSON file path,
    it validates the file's existence and checks if the content is properly formatted. If a JSON
    string is provided, it attempts to parse it into a Python dictionary.

    Raises:
        ValueError: If no JSON input is provided as a command-line argument.
        ValueError: If the provided JSON file does not exist or cannot be found.
        ValueError: If the JSON file contains invalid JSON.
        ValueError: If the given JSON string is invalid.

    Returns:
        dict: A parsed JSON configuration dictionary.
    """
    if len(sys.argv) < 2:
        raise ValueError(
            "Missing JSON input. Please provide a JSON string or a JSON file path as the first command-line argument.")
    # Check if input is a valid JSON file path
    arg = sys.argv[1]
    if arg.endswith(".json"):
        try:
            with open(arg, "r") as f:
                config = json.load(f)
        except FileNotFoundError:
            raise ValueError(f"JSON file not found: {arg}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format in file {arg}: {e}")
    else:
        config = json.loads(arg)  # Assume it's a JSON string
    return config