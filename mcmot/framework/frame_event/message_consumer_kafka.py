import json
import logging
import threading
import time

from kafka import KafkaConsumer
from kafka.consumer.fetcher import ConsumerRecord

from framework.frame_synchronization.frame_sequencing_service import FrameSequencingService
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration
from framework.frame_synchronization.frame_sync_service import FrameSyncService

logger = logging.getLogger("event")

def single_camera_synchronization(camera_id, frame_sync):
    """
    Single camera frame synchronization.

    This function handles the synchronization of a single camera's frames
    based on the provided frame synchronization logic. Depending on the
    logic, it either skips a specified number of frames or waits for a
    certain amount of time before returning. This is primarily used to
    align frames of a given camera with an external synchronization
    mechanism.

    Args:
        camera_id: Identifier of the camera that needs synchronization.
        frame_sync: An object providing the synchronization logic and
            methods for determining the appropriate action.

    Returns:
        The number of frames skipped during synchronization as an
        integer.
    """
    skip_count=0
    skip_or_wait, logic = frame_sync.sampling(camera_id)
    if logic:
        skip_count = skip_or_wait
    else:
        time.sleep(skip_or_wait)
    logger.debug("Skip count: %s",
                 skip_count)
    return skip_count


class MessageConsumer:
    """
    This class handles consuming messages from a Kafka topic, performing frame synchronization 
    and sequencing, and invoking user-defined callback functions on properly processed messages.

    The purpose of this class is to consume messages from Kafka, process them based on the 
    provided configurations (e.g., frame synchronization, sequencing, etc.), and integrate 
    the results with external systems via callbacks. It supports configurations for backlog 
    checks, initial delay handling, and frame synchronization, making it versatile for 
    applications requiring real-time or near-real-time stream processing.

    Attributes:
        last_callback_time (float): The timestamp of the last callback invocation.
        topic (str): The Kafka topic to consume messages from.
        group_id (str): The consumer group ID for Kafka.
        callback (callable): The function to call for each processed message.
        key (str or None): A key to filter or identify specific messages.
        frame_sync_config (FrameSyncConfiguration or None): Configuration for frame synchronization.
        consumer (KafkaConsumer): Internal Kafka consumer to fetch messages.
    """
    def __init__(self, bootstrap_servers: list, topic: str, group_id: str, callback, key: str = None,
                 frame_sync_config: FrameSyncConfiguration = None):
        """
        Initializes a consumer for integrating with Kafka to consume messages from a given topic.

        The constructor allows the initialization of a Kafka Consumer with specified
        broker details, topic information, group ID, and callback handler. It includes 
        optional settings such as a key for messages and frame synchronization configuration 
        parameters. Validation is performed for input arguments such as bootstrap servers.

        Parameters:
        bootstrap_servers : list
            A non-empty list of Kafka broker addresses in the format 'host:port'. It
            specifies the servers the consumer will connect to for messages.

        topic : str
            The Kafka topic to subscribe to for retrieving messages. This is the topic
            from which the consumer will read data.

        group_id : str
            A unique identifier for the consumer group this consumer belongs to. It
            assists in coordination when multiple consumers consume from the same topic.

        callback : Callable
            A callable function that the consumer will invoke upon receiving a
            message. This function defines custom handling logic for consumed data.

        key : Optional[str], default=None
            An optional key identifier for the messages the consumer will handle. It
            helps in filtering messages for specific keys if necessary.

        frame_sync_config : Optional[FrameSyncConfiguration], default=None
            Optional configuration for frame synchronization. If provided, it determines
            message handling behavior such as ignoring initial delays.

        Raises:
        ValueError
            If the `bootstrap_servers` argument is invalid, i.e., when it's not a list,
            it's empty, or it contains non-string elements.
        """
        self.last_callback_time = time.time()
        self.topic = topic
        self.group_id = group_id
        self.callback = callback
        self.key = key
        self.frame_sync_config = frame_sync_config
        logger.debug("Frame_Sync_Config: %s", self.frame_sync_config)
        logger.debug("bootstrap-servers: %s", bootstrap_servers)

        # Validate bootstrap_servers
        if not bootstrap_servers or not isinstance(bootstrap_servers, list) or not all(
                isinstance(server, str) for server in bootstrap_servers):
            raise ValueError("Invalid bootstrap_servers: Must be a non-empty list of strings.")
        self.consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=bootstrap_servers,
            group_id=self.group_id,
            auto_offset_reset="earliest" if not self.frame_sync_config or not self.frame_sync_config.ignore_initial_delay else "latest",
            enable_auto_commit=False,
            value_deserializer=json_deserializer,  # Use global deserializer
        )


    def start(self):
        """
        Process messages sequentially, performing operations such as frame synchronization 
        and sequencing while monitoring backlog time and iteration duration.

        Raises:
            Exception: If any error occurs during the message processing or 
            interactions with external services, it is logged and re-raised.


        Returns:
            None
        """
        start_time = time.time()
        frame_synchronization = None
        frame_sequencing = None
        processed_message_count = 0
        actual_message_count = 0
        skip_count = 0
        backlog_time_prev = time.time()
        seq_check_time = time.time()
        seek_to_end = False
        try:
            while True:
                # Infinite loop to process messages sequentially with backlog checks
                for message_index, record in enumerate(self.consumer):
                    # Log the start time of the iteration
                    iteration_start_time = time.time()
                    self.log_wait_time()

                    # Create a ConsumerRecord instance for the current Kafka message
                    rec = ConsumerRecord(*record)

                    # Skip if the message key does not match the expected key
                    if check_key_condition(self.key, record=rec):
                        continue

                    # Extract the message value
                    message = get_message(record=rec)

                    # Initialize FrameSyncService if frame synchronization is enabled
                    if self.frame_sync_config and self.frame_sync_config.frame_sync_type and not frame_synchronization:
                        frame_synchronization = FrameSyncService(self.frame_sync_config)

                    # Collect frame data for synchronization if skip_count is zero
                    if frame_synchronization and skip_count == 0:
                        frame_synchronization.collect(message['frame_number'], message['frame_timestamp'],
                                                      message['frame_metadata']['fps'],
                                                      message['camera_metadata']['camera_id'], message=message)

                    # Initialize FrameSequencingService if sequencing is enabled
                    if not frame_sequencing and self.frame_sync_config and self.frame_sync_config.enable_sequencing:
                        frame_sequencing = FrameSequencingService(self.frame_sync_config.backlog_check_interval)

                    # Perform frame sequencing if enabled
                    if frame_sequencing:
                        camera_id = message['camera_metadata']['camera_id']
                        frame_metadata = message['frame_metadata']
                        frame_sequencing.collect(frame_metadata, camera_id, message=message)

                        # Trigger sequencing at regular intervals
                        if time.time() - seq_check_time >= self.frame_sync_config.backlog_check_interval > 0:
                            threading.Thread(target=lambda: [
                                frame_sequencing.sequence(),
                                [self.callback.callback(seq_message) for seq_message in
                                 iter(lambda: frame_sequencing.next(), None) if seq_message is not None]
                            ]).start()
                            seq_check_time = time.time()

                    else:
                        # If there are skipped frames, decrement skip_count and continue
                        if skip_count > 0:
                            skip_count -= 1
                            actual_message_count += 1
                            continue

                        # Process the message if synchronization is not unified or not enabled
                        if not self.frame_sync_config or (self.frame_sync_config and not self.frame_sync_config.unify):
                            actual_message_count = self.process_cv_module(message, actual_message_count,
                                                                          processed_message_count,
                                                                          start_time)

                        # Handle frame synchronization logic
                        if frame_synchronization:
                            # Perform seek-to-end action for first-time processing if initial delay is ignored
                            if self.frame_sync_config.ignore_initial_delay and not seek_to_end:
                                self.consumer.commit()
                                self.consumer.seek_to_end()
                                seek_to_end = True
                                break

                            # Perform seek-to-end action if explicitly configured
                            if self.frame_sync_config and self.frame_sync_config.seek_to_end:
                                self.consumer.commit()
                                self.consumer.seek_to_end()
                                break

                            # Process backlog and synchronization if required
                            backlog_time_prev = self.process_frame_synchronization(backlog_time_prev,
                                                                                   frame_synchronization)

                            # Perform single camera synchronization if initial delay is not ignored
                            if not self.frame_sync_config.ignore_initial_delay and self.frame_sync_config and not self.frame_sync_config.unify:
                                camera_id = message['camera_metadata']['camera_id']
                                skip_count = single_camera_synchronization(camera_id, frame_synchronization)

                    # Commit the current message after processing
                    self.consumer.commit()

                    # Log the time taken for the iteration
                    iteration_end_time = time.time()
                    logger.debug("Total time taken for this iteration: %s millis",
                                 int((iteration_end_time - iteration_start_time) * 1000))
        except Exception as e:
            # Log any exceptions that occur during message processing
            logger.error(f"Consumer encountered an error: {e}", e)
            raise e
        finally:
            # Stop the consumer in the finally block
            self.stop()

    def log_wait_time(self):
        """
        Logs the time elapsed since the last call to this function and updates the time
        tracking attribute. If the elapsed time has not been previously tracked, it
        initializes the time tracking.

        Raises:
            This function does not explicitly raise any errors but might indirectly raise
            errors related to the logger or time module if improperly configured.
        """
        if not hasattr(self, 'last_callback_time'):  # Initialize if not already set
            self.last_callback_time = time.time()
        current_time = time.time()
        time_since_last_call = current_time - self.last_callback_time
        logger.debug("Time since last callback: %s ms", int(time_since_last_call * 1000))
        self.last_callback_time = current_time

    def process_frame_synchronization(self, backlog_time_prev, frame_sync):
        """
        Processes frame synchronization based on the backlog check interval and configuration.

        This method checks whether the time since the last backlog check has exceeded the
        configured interval. If so, it calculates the backlog count and optionally initiates
        a synchronization process in a separate thread, depending on the frame synchronization
        configuration.

        Parameters:
            backlog_time_prev: float
                The timestamp of the last backlog check.
            frame_sync: Any
                The frame synchronization object that provides the synchronize method.

        Returns:
            float
                The updated timestamp of the last backlog check.
        """
        if time.time() - backlog_time_prev >= self.frame_sync_config.backlog_check_interval > 0:  # if backlog_check_interval=0 never check backlog
            backlog_count = self.calculate_backlog()
            logger.debug("Backlog: %s", backlog_count)
            backlog_time_prev = time.time()
            if self.frame_sync_config.unify:
                threading.Thread(target=frame_sync.synchronize, args=(self.callback,)).start()
                logger.debug("Synchronization Called: %s", backlog_count)
        return backlog_time_prev

    def process_cv_module(self, message, actual_message_count, processed_message_count, start_time):
        """
        Processes a message within the CV module, updates message counts, logs processing details,
        and computes both the current and processed frames per second (FPS).

        Parameters:
        message (dict): The message to be processed, potentially containing frame-specific metadata.
        actual_message_count (int): The count of total messages encountered.
        processed_message_count (int): The count of messages successfully processed.
        start_time (float): The start time of the message processing operation, used for time calculations.

        Returns:
        int: The updated actual message count after processing this message.

        Raises:
        None
        """
        processing_start_time = time.time()
        actual_message_count += 1
        self.callback.callback(message)
        processed_message_count += 1
        processing_time = time.time() - processing_start_time
        logger.debug("Processed/Actual Message: %s/%s", processed_message_count, actual_message_count)
        processed_fps = int(processed_message_count / (time.time() - start_time))
        current_fps = int(actual_message_count / (time.time() - start_time))
        frame_metadata = message.get("frame_metadata", None)
        if frame_metadata:
            fps = frame_metadata.get("fps")
            actual_fps = frame_metadata.get("actual_fps")
            logger.debug("For frame: %s the FPS: Set(%s) Actual(%s) Current(%s) Processed(%s)", message.get("frame_number"), fps, actual_fps, current_fps,
                         processed_fps)
        logger.debug("Processing Time/Total Time: %s/%s", processing_time, time.time() - start_time)
        return actual_message_count

    def stop(self):
        """
        Logs the closing of the consumer and closes the consumer connection.

        Summary:
        This method logs a message indicating the consumer is being closed and
        then calls the close method on the consumer to release its resources.

        Raises:
        RuntimeError: If the consumer fails to close properly.
        """
        logger.info("Closing Consumer")
        self.consumer.close()

    def calculate_backlog(self):
        """
        Calculate the total backlog of messages for all partitions.

        This method computes the message backlog for each partition to which the
        consumer has been assigned. The backlog is calculated as the difference
        between the latest known offset for a partition and the committed offset the
        consumer has processed for that partition. It then sums up the backlogs
        across all partitions to return the total backlog value.

        Returns:
            int: The total backlog of messages across all assigned partitions.

        Raises:
            Exception: Re-raises any exceptions encountered during the process of
            retrieving offsets or computing the backlog.
        """
        backlog = {}
        try:
            # Retrieve the latest offsets for each partition
            end_offsets = self.consumer.end_offsets(list(self.consumer.assignment()))

            # Calculate the backlog for each partition
            for partition in self.consumer.assignment():
                # Retrieve the committed offset for the specific TopicPartition
                committed_offset = self.consumer.committed(partition) or 0
                end_offset = end_offsets[partition]

                # Calculate backlog for the partition
                backlog[partition.partition] = max(end_offset - committed_offset, 0)

        except Exception as e:
            raise e

        return sum(backlog.values())

def check_key_condition(key, record: ConsumerRecord):
    """
    Checks if a given key satisfies the condition against a record's key.

    Parameters:
    key: str
        The key to check the condition against.
    record: ConsumerRecord
        The consumer record containing the key to compare.

    Returns:
    bool
        True if the key is not None and does not match the decoded key from
        the provided record, otherwise False.
    """
    return key and key != record.key.decode("utf-8")

def json_deserializer(x):
    """
        Deserialize a JSON-encoded byte string into a Python object.

        This function takes a JSON-encoded byte string as input, decodes it to a
        UTF-8 string, and then parses the string into a Python object. It is
        typically used to transform serialized data obtained from a source such
        as a file, a database, or a network connection back into its Python
        representation.

        Parameters:
        x (bytes): The JSON-encoded byte string to be deserialized.

        Returns:
        Any: The Python object represented by the JSON byte string.
    """
    return json.loads(x.decode("utf-8"))

def get_message(record: ConsumerRecord):
    """
    Gets the message payload from a given Kafka consumer record.

    Parameters:
    record (ConsumerRecord): The record object from which the message
    is extracted.

    Returns:
    Any: The payload value of the passed consumer record.
    """
    return record.value
