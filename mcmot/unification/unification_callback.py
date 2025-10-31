import logging
import threading

from collections import defaultdict

from framework import MessageProducer
from datetime import datetime
import base64
import copy
import json
import os
import time
import cv2
import numpy as np

FILE_PATTERN = "%Y%m%d_%H%M%S%f"
TIME_PATTERN = "%Y/%m/%d %H:%M:%S.%f"

logger = logging.getLogger("application")

def prepare_message(message):
    """
    Prepare and annotate a video frame by decoding and overlaying metadata.

    This function processes a given message containing frame data, timestamp, detections,
    and camera metadata. It decodes the frame, overlays detection annotations and other
    metadata, and prepares the image for further use.

    Parameters:
        message (dict): A dictionary containing the frame information. Mandatory keys:
            - 'frame_number' (str or int): Identifier for the current frame.
            - 'frame' (str): The base64-encoded frame image data.
            - 'frame_timestamp' (str or float): Timestamp of the frame in seconds since epoch.
            - 'camera_metadata' (dict): A dictionary with camera metadata. It must contain:
                - 'camera_id' (str): Identifier for the camera source.
            - 'detections' (optional, dict): An optional dictionary of detection annotations.

    Returns:
        numpy.ndarray: Decoded and annotated video frame.

    Raises:
        Exception: If any required data is missing or processing fails during execution.
    """
    try:
        frame_number = message['frame_number']
        frame = message['frame']
        frame_timestamp = message['frame_timestamp']
        time_in_millis = datetime.fromtimestamp(float(frame_timestamp)).strftime('%H:%M:%S.%f')[:-3]
        detections = message.get("detections")
        camera_metadata = message['camera_metadata']
        camera_id = camera_metadata['camera_id']

        # Calculate current actual FPS
        current_elapsed_time = int(time.time())

        # Decode base64 string to bytes
        frame_data = base64.b64decode(frame)
        # Convert bytes to numpy array
        frame_np = np.frombuffer(frame_data, dtype=np.uint8)
        # Decode image
        decoded_frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)

        decoded_frame = annotate_frame(decoded_frame, detections)
        font_scale = 0.4
        color = (0, 255, 255)  # Yellow color

        cv2.putText(decoded_frame, f"Camera: {camera_id}", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                    color, 1)

        cv2.putText(decoded_frame, f"Frame: {frame_number}", (decoded_frame.shape[1] - 130, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 1)
        cv2.putText(decoded_frame, f"Timestamp: {time_in_millis} ({current_elapsed_time} sec)",
                    (10, decoded_frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 1)

    except Exception as e:
        print("Exception in consume_callback:", str(e))
        raise e
    return decoded_frame

def annotate_frame(frame, detections):
    """
    Annotates a video frame with bounding boxes and IDs based on provided detections.

    This function takes a video frame and a list of detection data. Each detection contains
    the bounding box coordinates, unique identifier, and color. The function overlays these
    annotations onto the video frame for visual representation.

    Args:
        frame: numpy.ndarray
            The video frame to annotate.
        detections: list[dict]
            A list of dictionaries containing detection information. Each dictionary must
            include the following keys:
            - 'bbox': tuple[int, int, int, int]
                The bounding box coordinates as (x1, y1, x2, y2).
            - 'id': int
                The unique identifier for the detected object.
            - 'color': tuple[int, int, int]
                The color for the bounding box and text annotation as a BGR tuple.

    Returns:
        numpy.ndarray
            The annotated frame with bounding boxes and object IDs overlayed.
    """
    if detections:
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']

            color = detection['color']
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 1)
            cv2.putText(frame, f"{"id"}: {detection['id']}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

    return frame

def recursive_replace_frame(data):
    """
    Recursively replaces 'frame' keys in a nested dictionary or list with the value 'null'.

    This function navigates through all levels of a given data structure, replacing any
    occurrence of the key 'frame' in dictionaries with the string value 'null'. Supports nested
    structures containing dictionaries, lists, or other types.

    Args:
        data (dict or list or any): The input data structure that may contain nested dictionaries
        or lists.

    Returns:
        dict or list or any: The updated data structure with 'frame' keys in dictionaries replaced
        by 'null'. Other data types are returned unchanged.
    """
    # logger.debug("data1 %s", data1)
    if isinstance(data, dict):
        # If the data is a dictionary, iterate through its items
        return {
            key: "null" if key == "frame" else recursive_replace_frame(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        # If the data is a list, iterate through its elements
        return [recursive_replace_frame(item) for item in data]
    else:
        # For other data types, return as is
        return data

def combine_frames(frames_store):
    """
    Combine a list of decoded video frames into a single image.

    This function takes a list of dictionaries containing decoded video frames and their associated metadata,
    sorts them based on camera ID and frame number, and combines the frames into a single image.
    It ensures proper ordering of frames and validates that the frames are not empty or invalid before combination.
    The frames are arranged row-wise, with each row containing a pair of frames stacked horizontally.
    Rows are stacked vertically to form the final combined image.

    Parameters:
    frames_store (list[dict]): A list of dictionaries where each dictionary represents a frame's metadata. Each
        dictionary must include the keys:
        - "camera_id" (any type): An identifier for the camera source of the frame.
        - "frame_number" (any type): The sequence number of the frame.
        - "decoded_frame" (numpy.ndarray or None): The actual frame data as a decoded image (can be None to indicate an
          invalid or missing frame).

    Raises:
    ValueError: If the input list is empty or contains invalid or empty frames.

    Returns:
    numpy.ndarray: The combined image formed by arranging all decoded frames into a single image. The frames are
        horizontally and vertically stacked based on their sorted order.
    """
    if not frames_store:  # Check if the list is empty
        raise ValueError("No decoded frames were provided for combination.")

    # Sort frames_store by camera_id and then by frame_number (optional for proper ordering)
    sorted_frames_store = sorted(frames_store, key=lambda fr: (fr["camera_id"], fr["frame_number"]))

    decoded_frames = [frame_data["decoded_frame"] for frame_data in sorted_frames_store if
                      frame_data["decoded_frame"] is not None]

    if not decoded_frames:
        raise ValueError("Decoded frames list is empty or contains invalid entries.")

    # Arrange frames according to their sorted order
    num_frames = len(decoded_frames)
    rows = []
    for i in range(0, num_frames, 2):
        frame1 = decoded_frames[i]
        frame2 = decoded_frames[i + 1] if i + 1 < num_frames else np.zeros_like(frame1)
        if frame1 is None or frame1.size == 0 or frame2 is None or frame2.size == 0:  # Validate frames
            raise ValueError(f"Invalid or empty frames encountered at indices {i} and {i + 1} during combination.")

        # Stack two frames horizontally
        row = cv2.hconcat([frame1, frame2])
        rows.append(row)

    # Stack all rows vertically
    combined_image = rows[0]
    for row in rows[1:]:
        combined_image = cv2.vconcat([combined_image, row])
    return combined_image

def save_metadata(group_dir, message):
    """
    Save a cleaned JSON message into a specified group directory.

    The function saves a JSON representation of a processed message into
    a fixed file named 'metadata.json' within the specified directory.

    Parameters:
        group_dir (str): The path to the directory where the JSON metadata
            file will be created or overwritten. It must be a valid path to
            an existing directory.
        message (dict): The original message, which will be recursively
            processed and cleaned before being serialized into the JSON file.

    Raises:
        OSError: If there is an error writing to the specified directory.
        TypeError: If the message provided is not serializable to JSON.
    """
    # Save the cleaned JSON message in the group directory
    json_file_name = "metadata.json"  # Single metadata JSON file per group
    json_file_path = os.path.join(group_dir, json_file_name)
    with open(json_file_path, "w") as json_file:
        json_file.write(json.dumps(copy.deepcopy(recursive_replace_frame(message)), indent=4))

def save_grouped_frames(frames_store, group_dir):
    """
        Save all decoded frames from the frames_store dictionary into files.

        This function iterates over a collection of decoded frame data, extracts
        each frame along with associated metadata, constructs unique file names
        for each frame, and saves them in the specified directory.

        Parameters:
            frames_store (list): A list of dictionaries containing decoded frame
            data. Each dictionary must have the keys:
                - 'decoded_frame': numpy.ndarray - The actual frame to be saved
                - 'camera_id': str - The identifier of the camera
                - 'frame_number': int - The frame sequence number
                - 'frame_timestamp': int - The timestamp of the frame

            group_dir (str): The directory path where the decoded frames will be
            saved.

        Raises:
            OSError: If there is an issue creating the directories or writing the
            files.
            FileNotFoundError: If the specified directory path does not exist.
    """
    # Save all decoded frames from frames_store
    for frame_data in frames_store:
        decoded_frame = frame_data["decoded_frame"]
        camera_id = frame_data["camera_id"]
        frame_number = frame_data["frame_number"]
        frame_timestamp = frame_data["frame_timestamp"]
        file_name = f"{camera_id}-{frame_number}-{frame_timestamp}.jpg"
        file_path = os.path.join(group_dir, file_name)
        cv2.imwrite(file_path, decoded_frame)

def create_grouped_frame_data(message):
    """
    Creates grouped frame data from a given message, decoding and validating
    frame data for further processing.

    This function processes a structured message containing camera data and
    extracts specific frame information. It decodes base64-encoded frame data,
    validates the decoded image, and organizes the data into a structured format
    for use in subsequent operations.

    Args:
        message (list[dict]): A list of dictionaries where each dictionary represents
            a group containing camera data and associated information.

    Returns:
        list[dict]: A list of dictionaries. Each dictionary contains the following keys:
            - 'decoded_frame': The validated and decoded frame data.
            - 'camera_id': The identifier of the camera that recorded the frame.
            - 'frame_timestamp': The timestamp associated with the frame.
            - 'frame_number': The sequence number of the frame.

    Raises:
        KeyError: Raised if any required key is missing from the structured message.
        ValueError: Raised if the decoded image is empty or invalid.
    """
    grouped_frame_data = []
    for group in message:
        camera_data = group.get("camera_data", {})
        additional_info = camera_data.get("additional_info", {})
        frame_message = additional_info.get("message", {})
        frame_number = camera_data.get("frame_number")
        frame_timestamp = camera_data.get("frame_timestamp")
        encoded_frame = frame_message.get("frame")  # The base64-encoded frame data
        camera_id = group.get("camera_id")
        # logger.debug("Frame in detection: %s", encoded_frame)
        if encoded_frame is not None:
            decoded_image = prepare_message(frame_message)
            # logger.debug("Decoded Image: %s", decoded_image)
            # Check if the decoded image is valid
            if decoded_image is not None and not decoded_image.size == 0:

                grouped_frame_data.append(
                    {"decoded_frame": decoded_image, "camera_id": camera_id,
                     "frame_timestamp": frame_timestamp, "frame_number": frame_number})
            else:
                print(
                    f"Warning: Decoded image is empty or invalid for frame {frame_number} from camera {camera_id}")
    return  grouped_frame_data

def create_grouped_frame_metadata(grouped_frame_data):
    """
    Constructs a list of metadata dictionaries from grouped frame data.

    This function processes a list of dictionaries where each dictionary contains
    the metadata of a frame. It extracts specific fields including 'frame_number',
    'frame_timestamp', and 'camera_id' from the input and organizes them into a new
    list of dictionaries, each containing these specific keys. This allows for
    structured and standardized storage of frame metadata.

    Arguments:
        grouped_frame_data (list[dict]): A list of dictionaries where each
            dictionary contains metadata of a frame including keys like
            'frame_number', 'frame_timestamp', and 'camera_id'.

    Returns:
        list[dict]: A list of dictionaries, where each dictionary includes
        'camera_id', 'frame_timestamp', and 'frame_number' as keys.
    """
    frames_store = []
    for frame_data in grouped_frame_data:
        frame_number = frame_data.get("frame_number")
        frame_timestamp = frame_data.get("frame_timestamp")
        camera_id = frame_data.get("camera_id")

        frames_store.append(
            {"camera_id": camera_id,
             "frame_timestamp": frame_timestamp, "frame_number": frame_number})
    return frames_store


def _save_group_outputs(grouped_frame_data, group_dir, message):
    """
        Save the outputs of a grouped frame data operation to a specified directory.

        This function saves individual frames provided as grouped frame data into a given directory
        and pulls additional information (metadata) to store alongside the frames in that directory.

        Args:
            grouped_frame_data: The data structure containing frame information grouped by some criteria.
            group_dir: str. The directory where the grouped frame outputs and metadata will be saved.
            message: str. A message or metadata information related to the grouped frame data for saving
            alongside the frames.

        Raises:
            None
    """
    # Save individual frames
    save_grouped_frames(grouped_frame_data, group_dir)

    # Save metadata
    save_metadata(group_dir, message)


def _combine_frames(grouped_frame_data, group_dir):
    """
    Combine multiple frames into a single image and save the result.

    The function takes grouped frame data, combines the frames into a
    single image, saves the resulting image in the specified group
    directory, and returns the combined frame.

    Args:
        grouped_frame_data: Iterable of frames to be combined.
        group_dir: str. Path to the directory where the combined image
            will be saved.

    Returns:
        The combined frame as an image.
    """
    combined_frame = combine_frames(grouped_frame_data)

    # Save the combined frame as an image
    combined_frame_path = os.path.join(group_dir, "combined.jpg")
    cv2.imwrite(combined_frame_path, combined_frame)

    return combined_frame

class UnificationCallback:
    """UnificationCallback class is responsible for managing the processing of video frames,
    storing metadata, creating a combined video, and producing messages with encoded data for a specified outbound topic.

    This class is designed to handle frame processing, grouping, combining frames into videos,
    and managing the lifecycle of the video writer, ensuring resources are released appropriately.
    It also supports message production with processed data to a specified message topic.

    Attributes:
        outbound_topic (str): Topic to which processed messages will be sent.
        video_path (str): Directory path where the combined video, logs, and metadata will be stored.
        producer (MessageProducer): Message producer instance to handle message production.
        fourcc: Codec information used for video writer initialization.
        video_writer: Instance of cv2.VideoWriter used for writing frames to video.
        _callback_time_lock: A threading lock to synchronize callback time updates.
        _first_callback_time: Last time the callback was invoked, used for video writer inactivity detection.
        _stop_watcher: Flag indicating whether the watcher thread for video writer should stop.
        _watcher_thread: Thread instance for monitoring video writer activity.
        contexts: A dictionary to store thread-specific context.
        frame_count: Counter for the number of processed frames.
        executor: ThreadPoolExecutor instance managing concurrent execution.
        log_file_path (str): Path to the log file for storing logs related to frame unification.
        excel_file_path (str): Path to the Excel file for storing grouped metadata.
    """
    def __init__(self, producer: MessageProducer, outbound_topic: str, output_path: str):
        """
        Initialize the VideoProcessor with necessary configurations for video processing
        and message production. This constructor sets up the video writer, directories for
        output, thread pool for concurrent tasks, and required locks for thread safety.



        Parameters:
            producer: The message producer responsible for creating and sending
                outbound messages.
            outbound_topic: The topic to which messages are sent.
            output_path: The directory path where outputs such as video, logs, and
                Excel files will be saved.

        Raises:
            IOError: If the video writer fails to initialize, possibly due to an invalid
                codec, resolution mismatch, or an incorrect output path.
        """
        self._stop_watcher = None
        self._watcher_thread = None
        self.outbound_topic = outbound_topic
        self.video_path = output_path
        self.producer = producer
        self._callback_time_lock = threading.Lock()
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        os.makedirs(self.video_path, exist_ok=True)

        self.video_writer = cv2.VideoWriter(
            os.path.join(self.video_path, "combined_video.mp4"),
            self.fourcc, 30, (1280, 720)
        )
        if not self.video_writer.isOpened():
            raise IOError("Failed to initialize video writer. Check the codec, resolution, and output path.")

        self._first_callback_time = time.time()
        self.contexts = defaultdict(list)  # Store thread-specific context
        self.frame_count = 0

        from concurrent.futures import ThreadPoolExecutor
        self.executor = ThreadPoolExecutor(max_workers=4)

        self.log_file_path = os.path.join(self.video_path, "unified.log")
        self.excel_file_path = os.path.join(self.video_path, "unified.xlsx")

    def callback(self, message):
        """
        Handle a callback triggered by incoming messages.

        This method manages the process of grouping incoming data, saving frames
        and metadata, processing video frames, and producing an output message
        with encoded data.

        Parameters:
            message (Any): The incoming message containing data needed to create
            grouped frame data.

        Raises:
            ValueError: If no valid frames are stored for combination.
        """
        # Update the time of the last callback each time it's called
        self._first_callback_time = time.time()

        # Step 1: Create grouped frame data
        grouped_frame_data = create_grouped_frame_data(message)
        if not grouped_frame_data:
            raise ValueError("No valid frames were stored for combination.")

        # Step 2: Create directory for this group
        group_dir = self._create_group_directory()

        # Step 3: Combine frames into a single image
        combined_frame = _combine_frames(grouped_frame_data, group_dir)

        # Step 4: Save frames and metadata
        _save_group_outputs(grouped_frame_data, group_dir, message)

        # Step 5: Process combined frame into video
        self._process_combined_frame_for_video(combined_frame)

        # Step 6: Produce message with encoded data
        self._produce_output_message(grouped_frame_data, combined_frame)

    # Helper to create grouped frame data

    # Create unique group directory
    def _create_group_directory(self):
        """
        Creates a directory for grouping videos based on the current timestamp.

        This method generates a directory path formatted using the current timestamp and
        a predefined pattern. It ensures the directory is created if it does not already
        exist and returns the path of the directory.

        Returns:
            str: A string representing the path of the created directory.
        """
        group_dir = os.path.join(self.video_path, datetime.now().strftime(FILE_PATTERN))
        os.makedirs(group_dir, exist_ok=True)
        return group_dir


    # Process the combined frame into the video output
    def _process_combined_frame_for_video(self, combined_frame):
        """
        Processes a combined frame for video output.

        The method resizes the given combined video frame to a fixed resolution
        of 1280x720 pixels and writes it to the video using the video writer.
        If the provided frame is invalid or empty, a ValueError is raised.

        Parameters
        ----------
        combined_frame : Any
            The combined video frame to process. It must not be None.

        Raises
        ------
        ValueError
            If the combined frame is invalid or empty.
        """
        if combined_frame is not None:
            # Resize to match required resolution and write to video
            video_frame = cv2.resize(combined_frame, (1280, 720))
            self.video_writer.write(video_frame)
        else:
            raise ValueError("Combined frame is invalid or empty.")

        # Start a watcher to close the video writer if inactive for >60 seconds
        self._start_video_writer_watcher()

    # Start a background watcher for the video writer
    def _start_video_writer_watcher(self):
        """
        Initializes and starts a background thread that monitors the video writer's
        activity and ensures it is closed if inactive for more than 60 seconds.

        Raises:
            AttributeError: Raised if necessary attributes for the watcher thread are
            not accessible.
        """
        import threading

        # Ensure a graceful stopping flag exists
        if not hasattr(self, "_stop_watcher"):
            self._stop_watcher = False

        # Define the watcher thread logic
        def watcher():
            while not self._stop_watcher:
                # Check if it's been more than 60 seconds since the last callback
                if time.time() - self._first_callback_time > 300:
                    self.close_video_writer()
                    self._stop_watcher = True  # Stop the thread after closing the writer
                time.sleep(1)  # Prevent CPU overuse

        # Safely check and initialize the thread
        if not hasattr(self, "_watcher_thread") or self._watcher_thread is None or \
                (isinstance(self._watcher_thread, threading.Thread) and not self._watcher_thread.is_alive()):
            # Initialize and start the watcher thread
            self._watcher_thread = threading.Thread(target=watcher, daemon=True)
            self._watcher_thread.start()

    # Produce the final output message after encoding
    def _produce_output_message(self, grouped_frame_data, combined_frame):
        """
        Produces an output message by encoding the provided frame data and generating metadata.

        The method processes the input combined frame and groups frame data to create an output
        message. The combined frame is encoded as a base64 string, and metadata is generated
        based on grouped frame data. The message is published to the specified outbound topic.

        Args:
            grouped_frame_data: dict
                A dictionary containing metadata and other information related to grouped
                frames.
            combined_frame: numpy.ndarray
                The image frame to be processed and encoded.

        Raises:
            Any exceptions that may occur during the process of encoding, metadata generation,
            or message production are raised.
        """
        # Encode combined frame as base64
        _, buffer = cv2.imencode('.jpg', combined_frame)
        processed_frame_data = buffer.tobytes()
        encoded_frame = base64.b64encode(processed_frame_data).decode('utf-8')

        # Make grouped frame metadata
        grouped_frame_metadata = create_grouped_frame_metadata(grouped_frame_data)

        # Create the message
        message = {
            'frame': encoded_frame,
            'grouped_frame_metadata': grouped_frame_metadata,
            'grouped_time': datetime.now().strftime(TIME_PATTERN)
        }

        # Produce the message to the outbound topic
        self.producer.produce_message(self.outbound_topic, message)

    # Close video writer
    def close_video_writer(self):
        """
        Closes the video writer and stops the associated watcher thread.

        This method ensures the video writer is properly released if it has been
        initialized and stops any associated watcher thread to prevent resource
        leaks or unintended behaviors.

        Raises
        ------
        This method does not raise any explicit errors.

        """
        if self.video_writer is not None:
            self.video_writer.release()  # Release the video writer
            logger.info("Closed the video writer due to inactivity.")
        self.stop_watcher()  # Stop the watcher thread

    def stop_watcher(self):
        """
        Stops the background watcher thread if it is active. Ensures that any watching
        operations complete gracefully before stopping the thread.

        Raises
        ------
        AttributeError
            If attributes `_stop_watcher` or `_watcher_thread` do not exist.
        TypeError
            If `_watcher_thread` is not an instance of `threading.Thread`.

        """
        if hasattr(self, "_stop_watcher"):
            self._stop_watcher = True
        if hasattr(self, "_watcher_thread") and isinstance(self._watcher_thread,
                                                           threading.Thread) and self._watcher_thread.is_alive():
            self._watcher_thread.join()  # Wait for thread to finish
