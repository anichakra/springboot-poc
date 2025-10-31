import json
import logging
import time

import numpy as np
from kafka import KafkaProducer, KafkaAdminClient, KafkaConsumer
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
from kafka.partitioner import murmur2

logger = logging.getLogger("event")

class NumpyEncoder(json.JSONEncoder):
    """
    A JSON encoder extension for handling numpy data types.

    This class is designed to extend the default JSONEncoder to process and serialize
    numpy-specific data types. Its primary purpose is to provide compatibility when 
    attempting to serialize numpy objects such as arrays, integers, or floating-point 
    numbers into JSON format. It achieves this by converting these numpy objects into 
    native Python representations that can be serialized by the standard JSON encoding.

    Attributes
    ----------
    No specific attributes are defined for this class.
    """

    def default(self, obj):
        """
        Custom JSON encoder extending the default JSON encoder to handle
        NumPy data types and convert them into native Python data types
        suitable for JSON serialization.

        Methods:
            default(obj)
                Overrides the default JSON encoding behavior to provide
                custom serialization for NumPy arrays, floats, and integers.

        Raises:
            TypeError: If the object cannot be serialized by the encoder.

        Args:
            obj: The Python object to serialize. Supports NumPy arrays,
                 NumPy floating-point numbers, NumPy integers, and
                 objects supported by the parent class.

        Returns:
            The JSON-serializable representation of the given object.
        """
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.int32, np.int64)):
            return int(obj)
        return super(NumpyEncoder, self).default(obj)


def json_serializer(x):
    """
        Serializes a Python object to a JSON-formatted byte string using a custom encoder.

        This function takes a Python object and serializes it into a JSON-formatted
        byte string. The `NumpyEncoder` is used as a custom JSON encoder to handle
        data types that are not natively serializable by the default JSON encoder.

        Args:
            x: Any
                The Python object to be serialized into JSON format.

        Returns:
            bytes
                The JSON-encoded data serialized as a UTF-8 encoded byte string.
    """
    return json.dumps(x, cls=NumpyEncoder).encode('utf-8')

class MessageProducer:
    """
    Provides functionality to produce messages to Kafka topics and manage topic operations.

    This class represents a Kafka producer and admin client implementation designed to
    facilitate interaction with Apache Kafka. It allows producing messages to specified
    topics with optional partitioning based on keys, managing Kafka topics (creation and
    deletion), and retrieving metadata such as partition counts. It also supports
    customizable key serialization and logging delivery reports.

    Attributes:
        producer: An instance of KafkaProducer for sending messages to Kafka.
        bootstrap_servers: The Kafka bootstrap servers used by the producer and admin client.
        admin_client: An instance of KafkaAdminClient for managing Kafka topics.
    """
    def __init__(self, bootstrap_servers):

        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            key_serializer=self.key_serializer,
            value_serializer=json_serializer
        )
        self.bootstrap_servers = bootstrap_servers
        self.admin_client = KafkaAdminClient(bootstrap_servers=bootstrap_servers)

    @staticmethod
    def key_serializer(k):
        """
        Encodes a key into a standardized byte format. This method ensures that
        the provided key is serialized into bytes for use in systems requiring
        binary key formats. It supports None, string, and byte types and raises
        an error for unsupported key types.

        Parameters:
            k (None | str | bytes):
                The input key to serialize. It can be None, a string, or bytes.

        Returns:
            bytes | None:
                Returns the serialized key in bytes format. If the input key
                is None, it returns None.

        Raises:
            ValueError:
                If the input key is of an unsupported type, this method raises
                a ValueError with a descriptive message.
        """
        if k is None:
            return None  # Handle None key
        elif isinstance(k, bytes):
            return k  # Already bytes, no encoding required
        elif isinstance(k, str):
            return k.encode('utf-8')  # Encode string to bytes
        else:
            raise ValueError(f"Unsupported key type: {type(k)}. Must be None, str, or bytes.")

    @staticmethod
    def murmur2(key):
        """Simple substitute for the murmur2 hash used in Kafka."""
        return int(murmur2(str(key).encode('utf-8')))

    def create_topic(self, topic_name: str, delete: bool = True, partitions: int = 1, replication_factor: int = 1):
        """
        Creates a new topic with the specified configuration or deletes and re-creates it if the `delete` 
        flag is set to True.

        In case the topic already exists and the `delete` flag is False, no action is taken. If the topic
        is to be deleted first, the function ensures its removal before creating a new topic with the 
        given specification.

        Args:
            topic_name: The name of the topic to be created.
            delete: A flag to indicate whether to delete the topic first if it already exists. Defaults to True.
            partitions: The number of partitions to be assigned to the topic. Defaults to 1.
            replication_factor: The replication factor for the new topic. Defaults to 1.

        Raises:
            TopicAlreadyExistsError: If the topic being created already exists and the `delete` flag is False.
            Exception: For any other errors encountered during topic creation or deletion.
        """
        try:
            # Delete the topic if `delete` flag is true and the topic exists
            if delete:
                existing_topics = self.admin_client.list_topics()
                if topic_name in existing_topics:
                    self.admin_client.delete_topics([topic_name])
                    logger.info(f"Deleted topic: {topic_name}")

                    self.wait_for_topic_deletion(topic_name)

            else:
                # Check if the topic already exists
                existing_topics = self.admin_client.list_topics()
                if topic_name in existing_topics:
                    logger.info(f"Topic '{topic_name}' already exists. Skipping creation.")
                    return

            # Create the topic
            topic = NewTopic(name=topic_name, num_partitions=partitions, replication_factor=replication_factor)

            self.admin_client.create_topics([topic])

            # Wait for the topic to be created
            self.wait_for_topic_creation(topic_name)

            logger.info(f"Topic '{topic_name}' created successfully")
        except TopicAlreadyExistsError:
            logger.info(f"Topic '{topic_name}' already exists")
        except Exception as e:
            logger.error(f"Failed to create topic '{topic_name}': {e}")

    def wait_for_topic_deletion(self,topic_name):
        """
        Waits for the given topic to be deleted from the Kafka broker.

        This function continuously checks the Kafka server to verify if the specified
        topic has been successfully deleted by polling the list of available topics.
        It waits and retries at regular intervals until the topic is deleted or a
        timeout condition is met.

        Args:
            topic_name (str): The name of the topic to be checked for deletion.
        """
        while True:
            time.sleep(1)  # Wait and retry
            consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers)

            if topic_name not in consumer.topics():
                print(f"Topic '{topic_name}' is successfully deleted.")
                break

        print(f"Timeout: Topic '{topic_name}' was not deleted")


    def wait_for_topic_creation(self, topic_name):
        """
        Waits for the creation of a specified Kafka topic by continuously checking 
        if the topic is available in the Kafka broker and logging status updates.

        Parameters:
            topic_name (str): The name of the topic to wait for.

        Raises:
            No exceptions are explicitly raised within this function.

        """
        while True:
            time.sleep(1)  # Wait and retry
            consumer = KafkaConsumer(bootstrap_servers=self.bootstrap_servers)

            if topic_name in consumer.topics():
                print(f"Topic '{topic_name}' is successfully created.")
                break

        logger.debug(f"Timeout: Topic '{topic_name}' was not created ")

    def get_partition_count(self, topic_name):
        """
        Gets the partition count for a specified topic from Kafka using an admin client. The method fetches the topic metadata, 
        examines it for errors, and determines the number of partitions. In the event of encountered errors, it attempts 
        retry logic or raises exceptions for processing failures.

        Args:
            topic_name (str): The name of the Kafka topic for which the partition count is requested. 

        Returns:
            int: The number of partitions associated with the specified topic. Returns 0 if no metadata is found 
            for the topic or an error is encountered during the metadata retrieval.

        Raises:
            Exception: Raised when the partition count cannot be determined due to unexpected errors during 
            metadata retrieval or other failures.
        """
        try:
            # Fetch topic metadata
            metadata = self.admin_client.describe_topics([topic_name])

            # Extract metadata for the given topic
            topic_metadata = next((topic for topic in metadata if topic['topic'] == topic_name), None)

            if topic_metadata is None:
                logger.warning(f"No metadata found for topic '{topic_name}'.")
                return 0

            # Check for errors in the topic metadata
            if topic_metadata['error_code'] != 0:
                logger.error(f"Error in topic metadata for '{topic_name}': {topic_metadata['error_code']}")
                return self.get_partition_count(topic_name)
            # Extract partition count
            partitions = topic_metadata['partitions']
            partition_count = len(partitions)
            return partition_count

        except Exception as e:
            logger.error(f"Could not get partition count for topic '{topic_name}': {e}")
            raise e

    @staticmethod
    def delivery_report(err, record_metadata):
        """
        Provides a static method to handle delivery reports for message
        delivery attempts. Logs error messages if delivery fails or 
        logs metadata about the delivery if successful.

        Args:
            err (Exception or None): The error object if a delivery error occurred. 
            record_metadata (object): Metadata about the delivered message 
                including topic, partition, and offset.

        Returns:
            None
        """
        if err:
            print(f"Error occurred: {err}")
        else:
            logger.debug(f"Message delivered to {record_metadata}")

    def produce_message(self, topic: str, message, key: str=None, partitionable: bool = False):
        """
        Produces a message to a specified Kafka topic.

        This method handles the process of sending a message to a Kafka topic. It supports
        partitioning if specified, allowing messages to be sent to a specific partition based
        on a key. Without partitioning, the message is sent to Kafka using the producer
        without specifying a partition. The method also supports synchronous delivery for
        non-partitionable sends.

        Parameters
        ----------
        topic : str
            The name of the Kafka topic where the message will be sent.
        message
            The content of the message to be sent. Its type and structure are determined 
            by the producer's serialization configuration.
        key : str, optional
            The key used for partitioning messages when partitionable is True. Defaults to None.
        partitionable : bool, optional
            A flag indicating if the message should be partitioned, based on the provided key.
            Defaults to False.

        Raises
        ------
        Exception
            If there is an error during the message production process, the exception is logged
            and then re-raised to propagate the error to the caller.
        """
        try:
            if partitionable:
                # Get the partition count for the specified topic
                partition_count = self.get_partition_count(topic)

                # Check if partition count is valid and greater than 0
                if partition_count is not None and partition_count > 0:
                    # Compute the partition index using murmur2 hash of the key
                    partition = self.murmur2(key) % partition_count
                    logger.debug(f"Producing to partition {partition} for key {key}")
                    # Send the message to the specific partition using the computed partition index
                    self.producer.send(
                        topic,
                        key=str(key) if key is not None else None,  # Serialize the key if provided
                        value=message,  # The message to be sent
                        partition=partition  # Explicit partition
                    )
            else:
                # If partitioning is not required and a key is provided
                if key is not None:
                    # Send the message with the key
                    future = self.producer.send(
                        topic,
                        key=str(key),  # Serialize the key
                        value=message  # The message to be sent
                    )
                else:
                    # Send the message without a key
                    future = self.producer.send(
                        topic,
                        value=message  # The message to be sent
                    )
                # Wait for the message delivery to complete and get metadata (blocking call)
                record_metadata = future.get()
                # Log the delivery report for the produced message
                self.delivery_report(None, record_metadata)
        except Exception as e:
            # Log the error and re-raise the exception if message production fails
            logger.error(f"Failed to produce message: {e}")
            raise e
