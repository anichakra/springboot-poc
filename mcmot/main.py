import logging

from framework import MessageProducer
from framework.utils.config_utils import read_config
from framework.utils.logging_utils import setup_logging


def main():
    """
    Main function for setting up, processing configurations, and sending a message to a Kafka topic.
    This function initializes logging, reads configuration, constructs a message from the provided
    configuration, and sends it to a specified Kafka topic. Handles various exceptions that may occur
    during execution and ensures proper cleanup before exiting.

    Functions:
        main(): Entry point for executing the application logic.

    Raises:
        ValueError: If invalid JSON input is encountered during configuration reading.
        KeyboardInterrupt: If the program is interrupted by the user.
        Exception: Captures any unexpected runtime errors.
    """
    # Set up logging for the application environment
    setup_logging("dev")
    logger = logging.getLogger("application")
    try:
        arguments = read_config()
        pipeline = arguments.get('pipeline')

        message = {
            'signal': arguments.get('signal'),
            'loop_count': arguments.get('loop-count', 1)
        }
        topic = f"camera-{pipeline}-topic"
        producer = MessageProducer(bootstrap_servers=arguments.get("bootstrap-servers", ["localhost:9092"]))
        producer.produce_message(topic, message, key=None)
        logger.info(f"Message {message} sent successfully to topic '{topic}'")

    except ValueError:
        logger.error("Invalid JSON input. Please provide a valid JSON-formatted string.")
    except KeyboardInterrupt:
        logger.error("Program interrupted by user. Cleaning up...")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info("Exiting program.")


if __name__ == "__main__":
    main()
