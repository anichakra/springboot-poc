import logging
import logging.config
import os
from pathlib import Path

import yaml

def setup_logging(environment):
    """
    Retrieve and setup logging configuration based on the environment.

    This function obtains the environment-specific logging configuration based on
    the provided environment parameter. It looks for a YAML configuration file in
    the specified log configuration path. If the configuration file is found,
    it is loaded and applied to configure logging. If the configuration file is
    not found or fails to load, the function falls back to a basic logging setup
    with an INFO level.

    Parameters:
        environment (str): The name of the environment to configure logging for
        (e.g., "development", "production").

    Raises:
        FileNotFoundError: If the configuration file does not exist for the given
        environment.
        YAMLError: If there is an error parsing the YAML configuration file.
    """

    print(f"Getting environment specific log configuration for {environment}")
    log_config_path = os.getenv("LOG_CONFIG_PATH", "config/log")
    config_file = f"{log_config_path}/logging.{environment}.yaml"
    logging_config_path = Path(config_file)

    try:
        if logging_config_path.is_file():
            with open(logging_config_path, "r") as file:
                config = yaml.safe_load(file)

                logging.config.dictConfig(config)  # Apply the loaded configuration
                print(f"Loading Configuration for Logging from {config_file}!")
        else:
            raise FileNotFoundError(f"Configuration file {config_file} not found.")
    except (yaml.YAMLError, FileNotFoundError) as e:
        print(f"Failed to load logging configuration from {config_file}. Using default logging config. Error: {e}")
        logging.basicConfig(level=logging.INFO)
