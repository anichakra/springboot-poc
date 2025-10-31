import logging

from concurrent.futures import ThreadPoolExecutor

from capture import CaptureService
from detection import DetectionService
from framework import MessageProducer
from framework.utils.config_utils import read_config
from framework.utils.logging_utils import setup_logging
from reid import ReidService
from tracker import TrackerService
from unification import UnificationService

logger = logging.getLogger("application")
if __name__ == "__main__":

    def create_topic_with_producer(topic_name: str, message_producer: MessageProducer, partitions: int = 1):
        """
        Creates a topic using the specified message producer with the given name and number of partitions.

        Parameters:
        topic_name : str
            The name of the topic to be created.
        message_producer : MessageProducer
            The producer responsible for creating the topic.
        partitions : int
            The number of partitions to be assigned to the topic. Defaults to 1.

        Raises:
        Exception
            If an error occurs during the topic creation process.

        """
        try:
            message_producer.create_topic(topic_name, delete=True, partitions=partitions)
            logging.debug("Topic %s is created", topic)
        except Exception as ex:
            logging.error("Error creating topic %s: %s", topic, str(ex))

    # Set up logging with the "dev" environment configuration
    setup_logging("dev")
    try:
        # Parse the JSON input from the first command-line argument
        config = read_config()  # Replace with your JSON loading function

        # Extract arguments with defaults if not provided
        pipeline = config.get("pipeline")
        topic_map = config.get("topics") # {"capture": 1, "detection": 1, "reid": 1, "tracker": 1, "unification":1}
        logger.debug("Scale_map: %s", topic_map)
        topics = [
            (f"{CaptureService.MODULE_NAME}-{pipeline}-topic",
             int(topic_map.get("capture", 1))),
            (f"{DetectionService.MODULE_NAME}-{pipeline}-topic",
             int(topic_map.get("detection", 1))),
            (f"{ReidService.MODULE_NAME}-{pipeline}-topic",
             int(topic_map.get("reid", 1))),
            (f"{TrackerService.MODULE_NAME}-{pipeline}-topic",
             int(topic_map.get("tracker", 1))),
            (f"{UnificationService.MODULE_NAME}-{pipeline}-topic",
             int(topic_map.get("unification", 1)))
        ]

        producer = MessageProducer(config.get("bootstrap-servers", ["localhost:9092"]))

        with ThreadPoolExecutor() as executor:
            for topic in topics:
                executor.submit(create_topic_with_producer, topic_name=topic[0],
                                message_producer=producer, partitions=topic[1])
            executor.submit(create_topic_with_producer, topic_name=f"{pipeline}-topic",
                                message_producer=producer, partitions=1)

    except ValueError as e:
        logger.error("Invalid JSON input. Please provide a valid JSON-formatted string.")
    except KeyboardInterrupt:
        logger.error("Program interrupted by user. Cleaning up...")
    finally:
        # Perform any necessary cleanup here
        logger.debug("Exiting program.")
