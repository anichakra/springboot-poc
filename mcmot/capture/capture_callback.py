import base64
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from enum import Enum

import cv2
import numpy as np

from framework import MessageProducer
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration
from framework.frame_synchronization.frame_sync_service import FrameSyncService

logger = logging.getLogger("application")


class Status(Enum):
    """
    Represents the various states that an entity or process can be in.

    The enumeration defines a set of permissible states to represent the status
    of an entity or system during its lifecycle or operation. It provides a
    structured way to convey the current operational condition or context-specific
    state. This is commonly used in functionality where finite state management
    is required, ensuring consistency and clarity.

    Attributes:
        INITIALIZED: Signifies that the entity has been initialized but is not
        yet active or in motion.
        RUNNING: Indicates the entity is currently active or operational.
        STOPPED: Represents that the entity has ceased operation or activity.
        ON_HOLD: Denotes a paused state where the entity is temporarily not
        progressing.
        ERROR: Represents that the entity has encountered an issue or malfunction.
    """
    INITIALIZED = "INITIALIZED"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    ON_HOLD = "ON_HOLD"
    ERROR = "ERROR"

class Signal(Enum):
    """Representation of control signals as enumeration.

    This class defines a set of control signals that can be used to regulate
    the behavior of a process or system. It leverages the Enum base class for
    creating user-friendly and readable symbolic names for specific constant
    values. These control signals are intended to standardize communication
    and state management within the application domain.
    """
    START = "START"
    STOP = "STOP"
    HOLD = "HOLD"
    RESUME = "RESUME"
    TERMINATE = "TERMINATE"

def handle_exception(exception: Exception, context_message: str = "An error occurred"):
    """
    Logs an exception with a provided context message.

    This function is used to log the details of an exception with an error message.
    It includes the exception information in the logs for better traceability.

    Args:
        exception (Exception): The exception instance to be logged.
        context_message (str, optional): A message providing context for the exception.
            Defaults to "An error occurred".
    """
    logger.error(f"{context_message}: {str(exception)}", exc_info=True)


def connect(video_path, retries=5, start_frame=0):
    """
    Connects to a video stream or file at the specified path, making multiple
    connection attempts if necessary, and seeks to a predefined starting frame.

    Parameters:
        video_path (str): The file path or URL of the video source to connect to.
        retries (int): The maximum number of connection attempts. Default is 5.
        start_frame (int): The frame index to seek to after connecting. Default
            is 0.

    Returns:
        cv2.VideoCapture: A VideoCapture object representing the connected video
            stream.

    Raises:
        None explicitly raised in this function, but may raise exceptions depending
        on usage of cv2.VideoCapture or other internal calls.
    """

    logger.debug("link to video: %s", video_path)
    for i in range(retries):
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            print(f"Connected! Seeking to frame {start_frame}...")
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame - 1)
            return cap
        logging.debug(f"Retry {i + 1}/{retries} - Reconnecting...")
        time.sleep(2)
    return None


class CaptureCallback:
    """
    Represents a callback handler for video frame processing with threading,
    status management, and message production capabilities for integration
    with other systems.

    This class is designed to manage the lifecycle of a video frame processing
    operation. It supports multiple control signals such as starting, stopping,
    holding, and resuming the processing workflow. The class processes video
    frames, applies frame skip or synchronization logic, and publishes metadata
    to a specified outbound topic.

    Attributes:
    video_path: Indicates the file path, URL, or stream source for video input.
    frame_sync_configuration: Defines the frame synchronization settings or logic for processing.
    outbound_topic: Specifies the topic where processed frame messages will be published.
    camera_metadata: Holds metadata related to the camera, e.g., camera ID, and other identifiers.
    producer: Reference to a message producer used to publish processed frames and associated metadata.
    loop_count: Integer representing the number of times the video should be looped, defaults to 1.
    simulated_frame_number: Integer that tracks processed frame numbers across loops.
    status: Keeps track of the current operational state using predefined enumeration Status.
    shutdown_event: Thread-safe event instance used for orderly stopping.
    executor: Thread pool executor for asynchronous task submission (maximum workers set to 5).
    _lock: Threading lock to ensure thread safety for concurrent operations.
    """
    def __init__(self, producer: MessageProducer, outbound_topic: str, video_path: str,
                 camera_metadata: dict, frame_sync_configuration: FrameSyncConfiguration):
        self.video_path = video_path
        self.frame_sync_configuration = frame_sync_configuration
        self.outbound_topic = outbound_topic
        self.camera_metadata = camera_metadata

        self.producer = producer
        self.loop_count = 1
        self.simulated_frame_number = 0
        self.status = Status.INITIALIZED
        self.shutdown_event = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=5)  # Limit
        self._lock = threading.Lock()  # Thread-safety lock

    def callback(self, message):
        # Handle message values using Status enumeration
        signal = message["signal"]
        self.loop_count = message["loop_count"]
        if signal == Signal.START.value:
            if self.get_status() in [Status.INITIALIZED, Status.STOPPED, Status.ERROR]:
                self.executor.submit(self.handle_start)
            else:
                logger.warning(f"Received illegal message value: {message}. Current Status is {self.status.value}.")

        elif signal == Signal.STOP.value:
            if self.get_status() == Status.RUNNING or self.get_status() == Status.ON_HOLD:
                self.executor.submit(self.handle_stop)
            else:
                logger.warning(f"Received illegal message value: {message}. Current Status is {self.status.value}.")

        elif signal == Signal.HOLD.value:
            if self.get_status() == Status.RUNNING:
                self.executor.submit(self.handle_hold)
            else:
                logger.warning(f"Received illegal message value: {message}. Current Status is {self.status.value}.")

        elif signal == Signal.RESUME.value:
            if self.get_status() in [Status.ON_HOLD, Status.ERROR]:
                self.executor.submit(self.handle_resume)
            else:
                logger.warning(f"Received illegal message value: {message}. Current Status is {self.status.value}.")
        else:
            logger.warning(f"Received unrecognized signal: {message}")

    def set_status(self, new_status):
        """Sets the status in a thread-safe manner."""
        with self._lock:
            self.status = new_status

    def get_status(self):
        """Gets the status in a thread-safe manner."""
        with self._lock:
            return self.status

    def increment_simulated_frame_number(self, value):
        with self._lock:
            self.simulated_frame_number += value

    def get_simulated_frame_number(self):
        with self._lock:
            return self.simulated_frame_number

    def handle_start(self):
        """
        Handles the process of reading video frames, performing operations, and sending metadata and processed frames
        to an outbound topic, while handling reconnections, frame skipping, and synchronization with other processes.
        The method manages transitions between statuses (RUNNING, STOPPED, ON_HOLD) and handles errors during the video
        processing loop.

        Raises
        ------
        Exception
            Raised if any error occurs during the video frame processing loop.
        """
        self.set_status(Status.RUNNING)
        logger.debug("frame sync config: %s", self.frame_sync_configuration)

        cap = None
        try:
            cap = connect(self.video_path, retries=5, start_frame=0)
            loop_count_counter = 0
            skip_count = 0
            fps = 0
            start_time = time.time()
            processed_message_count = 0

            camera_id = self.camera_metadata.get("camera_id")
            frame_sync = None

            while cap.isOpened():
                if self.shutdown_event.is_set():  # Check if shutdown was triggered
                    break

                status = self.get_status()
                if status == Status.STOPPED:
                    break
                if status == Status.ON_HOLD:
                    while self.get_status() == Status.ON_HOLD:
                        time.sleep(0.1)  # Wait for transition to RUNNING
                # Start iteration time
                iteration_start_time = time.time()

                # Take the total elapsed time
                total_elapsed_time = time.time() - start_time
                # Read a frame and handle reconnection
                ret, frame = cap.read()
                if not ret:
                    logger.debug(
                        f"Stream disconnected. Reconnecting from frame {int(cap.get(cv2.CAP_PROP_POS_FRAMES))}...")
                    cap.release()
                    cap = connect(self.video_path, start_frame=int(cap.get(cv2.CAP_PROP_POS_FRAMES)))
                    continue

                frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                frame_timestamp = time.time()
                if fps == 0:
                    fps = cap.get(cv2.CAP_PROP_FPS)

                # Prepare and send frame metadata
                if not frame_sync and self.frame_sync_configuration:
                    frame_sync = frame_sync or FrameSyncService(self.frame_sync_configuration)
                if frame_sync:
                    frame_sync.collect(frame_number, frame_timestamp, fps, camera_id)

                # Skip frames as needed
                if skip_count > 0:
                    for _ in range(skip_count):
                        cap.read()
                    skip_count = 0

                _, buffer = cv2.imencode('.jpg', frame)
                encoded_frame = base64.b64encode(buffer.tobytes()).decode('utf-8')
                actual_fps = int(np.ceil(
                    processed_message_count / total_elapsed_time)) if total_elapsed_time > 0 else 0  # Avoid division by zero

                frame_metadata = {
                    'height': frame.shape[0],
                    'width': frame.shape[1],
                    'codec': cap.get(cv2.CAP_PROP_FOURCC),
                    'fps': fps,
                    'actual_fps': actual_fps
                }

                message = {
                    'frame_number': frame_number + self.get_simulated_frame_number(),
                    'frame_timestamp': frame_timestamp,
                    'frame': encoded_frame,
                    'frame_metadata': frame_metadata,
                    'camera_metadata': self.camera_metadata
                }
                self.producer.produce_message(self.outbound_topic, message)

                # Handle loop logic
                if frame_number >= cap.get(cv2.CAP_PROP_FRAME_COUNT):
                    self.increment_simulated_frame_number(frame_number)
                    loop_count_counter += 1
                    if loop_count_counter >= self.loop_count:
                        break
                    cap = connect(self.video_path)

                # Frame Sync Process Logic starts
                if frame_sync:
                    if self.frame_sync_configuration.frame_sync_type == "number":
                        skip_or_wait, logic = frame_sync.sampling(camera_id)
                        logger.debug("skip or wait: %s", skip_or_wait)

                        if logic:
                            skip_count = skip_or_wait
                        else:
                            time.sleep(skip_or_wait)
                    else:
                        skip_count = 0
                # Frame Sync Process Logic ends
                iteration_elapsed_time = time.time() - iteration_start_time
                logger.debug("Iteration Elapsed Time: %s for camera: %s for frame: %s", iteration_elapsed_time,
                             camera_id,
                             frame_number)
        except Exception as e:
            self.set_status(Status.ERROR)
            handle_exception(e, "Error during capture loop")

        finally:
            if cap:
                cap.release()

        self.simulated_frame_number = 0
        self.set_status(Status.STOPPED)

    def handle_stop(self):
        self.set_status(Status.STOPPED)

    def handle_hold(self):
        self.set_status(Status.ON_HOLD)

    def handle_resume(self):
        self.set_status(Status.RUNNING)
