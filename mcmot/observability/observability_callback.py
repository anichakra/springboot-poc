import base64
import logging
import time
from datetime import datetime

import cv2
import numpy as np

logger = logging.getLogger("application")

class ObservabilityCallback:
    """
    Represents an observability callback for handling and processing video frames, annotations,
    and related metadata within a video processing system.

    This class is designed to process incoming frames, overlay metadata like timestamps, frame numbers,
    FPS, and detections, and then display the processed frames via OpenCV. It provides functionality
    for initializing frame dimensions, handling color configuration, and managing frame annotations.
    It is tailored for applications requiring real-time or near-real-time video analytics.

    Attributes:
        time_since_last_call: Tracks the elapsed time since the last callback was invoked.
        frame_dimensions_initialized: Stores initialized frame dimensions and related data for overlays.
        last_callback_time: Tracks the timestamp of the most recent callback execution.
        start_time: Dictionary mapping camera IDs to their respective start times for processing.
        message_count: Dictionary mapping camera IDs to the number of processed frames.
        module_name: The name of the module or system utilizing the callback.
        detection_header_parameter: Key in detection metadata that is highlighted on processed frames.
        show_timestamp: Indicates whether to display the timestamp on processed frames.
        show_frame_number: Indicates whether to display the frame number on processed frames.
        show_fps: Indicates whether to display the calculated frames-per-second (FPS).
        show_camera_id: Indicates whether to display the camera ID on processed frames.
        text_color: The color of the overlay text on frames.
        box_color: The color of the overlay boxes for annotations.
        text_thickness: The thickness of overlay text on frames.
        box_thickness: The thickness of the annotation boxes on frames.
    """
    def __init__(self, module_name: str, detection_header_parameter: str, text_color: str, text_thickness: int,
                 box_color: str, box_thickness: int,
                 show_timestamp: bool,
                 show_frame_number: bool,
                 show_fps: bool, show_camera_id: bool) :
        """
        This class is responsible for initializing and managing configurations for detecting and displaying annotations on
        frames such as text and bounding boxes. It allows customization of various components including color, thickness,
        and visibility of timestamps, frame numbers, and other metadata for visual representation. It also initializes
        internal structures for tracking timing and message counts for specific camera IDs.

        Attributes:
            module_name (str): Name of the module responsible for processing.
            detection_header_parameter (str): Header parameter for detection-related information.
            show_timestamp (bool): Flag to display a timestamp on the output frames.
            show_frame_number (bool): Flag to display the frame number on the output frames.
            show_fps (bool): Flag to display frames per second on the output frames.
            show_camera_id (bool): Flag to display the camera ID on the output frames.
            text_color (tuple): RGB color value for text annotations.
            text_thickness (int): Thickness of the text annotations.
            box_color (tuple): RGB color value for bounding boxes.
            box_thickness (int): Thickness of the bounding boxes.

        Methods:
            __init__: Initializes the object with required configurations and validates input parameters.
            get_color: Retrieves an RGB tuple representing a color based on user input.
        """
        self.time_since_last_call = 0
        self.frame_dimensions_initialized = None
        self.last_callback_time = time.time()
        self.start_time = {camera_id: time.time() for camera_id in
                              range(1, 256)}
        self.message_count = {camera_id: 0 for camera_id in
                              range(1, 256)}  # Initialize counters for camera IDs 1 to 255
        self.module_name = module_name
        self.detection_header_parameter = detection_header_parameter
        self.show_timestamp = show_timestamp
        self.show_frame_number = show_frame_number
        self.show_fps = show_fps
        self.show_camera_id = show_camera_id

        def get_color(color):
            """
                A class for managing observability callbacks in a system.

                This class is responsible for handling observability parameters such as text
                color, text thickness, box color, box thickness, as well as options regarding
                the display of timestamps, frame numbers, FPS, and camera IDs. It provides utility
                methods for managing and converting colors based on specified inputs.

                Methods:
                    __init__:
                        Initializes an instance of ObservabilityCallback with specified parameters.

                    get_color:
                        Maps a string representation of a color to its corresponding RGB tuple format.
            """
            color_map = {
                "red": (0, 0, 255),
                "yellow": (0, 255, 255),
                "green": (0, 255, 0),
                "blue": (255, 0, 0),
                "purple": (128, 0, 128),
                "black": (0, 0, 0),
                "white": (255, 255, 255)
            }
            return color_map.get(color.lower() if color else "white",
                                 (255, 255, 255))  # Default to white if not found or None

        self.text_color = get_color(text_color)
        self.box_color = get_color(box_color)
        self.text_thickness = text_thickness if isinstance(text_thickness, int) and text_thickness > 0 else 1
        self.box_thickness = box_thickness if isinstance(box_thickness, int) and box_thickness > 0 else 1

    def callback(self, message):
        """
        Processes a callback message received from a camera feed and applies various metadata-based
        annotations to the frame before displaying it. Handles per-camera FPS calculation, frame numbering,
        timestamping, and optional display of the annotated content alongside the processed frames using OpenCV.

        Args:
            message (dict): A dictionary containing the incoming message data. Must include keys such
            as 'camera_metadata', 'frame_number', 'frame_timestamp', 'frame', and 'frame_metadata'.
            Optionally, 'detections' can be included for annotating the frame with detected objects.

        Raises:
            Exception: Re-raises any exception encountered during execution to indicate a failure while
            processing the callback message or rendering the annotated frame.
        """
        try:
            camera_metadata = message['camera_metadata']
            camera_id = camera_metadata['camera_id']
            frame_number = message['frame_number']
            frame_timestamp = message['frame_timestamp']

            if camera_id not in self.start_time:
                self.start_time[camera_id] = time.time()

            if camera_id not in self.message_count:
                self.message_count[camera_id] = 0

            self.message_count[camera_id] += 1

            frame = message['frame']
            frame_metadata = message['frame_metadata']

            detections = message.get("detections")

            # Calculate current actual FPS
            current_elapsed_time = int(time.time() - self.start_time[camera_id])

            target_fps = int(np.ceil(
                frame_number / current_elapsed_time)) if current_elapsed_time > 0 else 0  # Avoid division by zero

            set_fps = int(frame_metadata['fps'])

            #wait_time = self.get_wait_time()
            logger.debug("Target FPS: %s, Camera: %s, Frame: %s, Timestamp: %s", target_fps, camera_id, frame_number, frame_timestamp)

            #if True or (target_fps >= set_fps-1 or frame_number < 500):

            # Decode base64 string to bytes
            frame_data = base64.b64decode(frame)
            # Convert bytes to numpy array
            frame_np = np.frombuffer(frame_data, dtype=np.uint8)
            # Decode image
            decoded_frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)

            if self.frame_dimensions_initialized is None:
                self.initialize_frame_dimensions(frame_metadata)
            font_scale = self.frame_dimensions_initialized['font_scale']
            w1 = self.frame_dimensions_initialized['w1']
            h1 = self.frame_dimensions_initialized['h1']
            w2 = self.frame_dimensions_initialized['w2']
            h2 = self.frame_dimensions_initialized['h2']

            if detections:
                decoded_frame = self.annotate_frame(decoded_frame, detections, font_scale)

            if self.show_camera_id:
                cv2.putText(decoded_frame, f"Camera: {camera_id}", (w1, h1),
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                            self.text_color, self.text_thickness)
            if self.show_frame_number:
                cv2.putText(decoded_frame, f"Frame: {self.message_count[camera_id]}/{frame_number}", (w2, h1),
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale, self.text_color, self.text_thickness)
            if self.show_timestamp:
                time_in_millis = datetime.fromtimestamp(float(frame_timestamp)).strftime('%H:%M:%S.%f')[:-3]
                cv2.putText(decoded_frame, f"Timestamp: {time_in_millis} ({current_elapsed_time} sec)",
                            (w1, h2),
                            cv2.FONT_HERSHEY_SIMPLEX, font_scale, self.text_color, self.text_thickness)
            if self.show_fps:
                actual_fps = int(np.ceil(
                    self.message_count[
                        camera_id] / current_elapsed_time)) if current_elapsed_time > 0 else 0  # Avoid division by zero

                cv2.putText(decoded_frame, f"FPS: {actual_fps}/{set_fps}",
                            (w2, h2), cv2.FONT_HERSHEY_SIMPLEX,
                            font_scale, self.text_color, self.text_thickness)

            cv2.imshow(f"{self.module_name}-{camera_id}", decoded_frame)
            cv2.waitKey(1)  # Display the frame for a short period

        except Exception as e:
            print("Exception in consume_callback:", str(e))
            raise e

    def initialize_frame_dimensions(self, frame_metadata):
        """
        Initializes frame dimensions based on metadata provided as input. This method calculates and assigns various
        frame metrics, including height, width, font scaling, and specific positional coordinates. These values
        are critical for frame processing and dynamic adjustments to adapt to varying frame dimensions. If any
        required metadata is missing, an error is logged, and an exception is raised.

        Args:
            frame_metadata (dict): A dictionary containing the keys 'height' and 'width' which define the dimensions
            of a frame.

        Raises:
            KeyError: If the required 'height' or 'width' keys are not found in the input metadata dictionary.
        """
        try:
            height = frame_metadata['height']
            width = frame_metadata['width']
            font_scale = height / 850  # Adjust font scale based on frame size
            w1 = int(width * 0.05)
            h1 = int(height * 0.05)
            w2 = int(width - width * 0.3)
            h2 = int(height - height * 0.05)

            # Initialize dimensions
            self.frame_dimensions_initialized = {
                'height': height, 'width': width, 'font_scale': font_scale,
                'w1': w1, 'h1': h1, 'w2': w2, 'h2': h2
            }
        except KeyError as e:
            logger.error(f"Missing required key in frame metadata: {e}")
            raise

    def annotate_frame(self, frame, detections, font_scale):
        """
        Annotates a frame with bounding boxes and text based on provided detections.

        The function draws rectangles and textual information on the given frame for each detection in
        the input list. It uses attributes of the class such as box_color, detection_header_parameter,
        box_thickness, and text_thickness to style and adjust the annotations. If a box color is not
        explicitly provided, it defaults to the color specified in the corresponding detection item.

        Args:
            frame: The image represented as a numpy array (typically an OpenCV image) on which
                annotations will be drawn.
            detections: A list of dictionaries where each dictionary represents a detection. The
                dictionary is expected to have a 'bbox' key with the bounding box coordinates tuple
                (x1, y1, x2, y2), and optionally 'id' or the key specified by detection_header_parameter.
                It may also optionally include a 'color' key for box color.
            font_scale: A float that indicates the scale of the font used for text annotations.

        Returns:
            The annotated frame as a numpy array with bounding boxes and corresponding text for
            each detection.
        """
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            detection_header = detection[self.detection_header_parameter]  # Fallback for 'id'

            color = self.box_color if self.box_color else detection['color']
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, self.box_thickness)
            cv2.putText(frame, f"{self.detection_header_parameter}: {detection_header}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, self.text_thickness)

        return frame

    def get_wait_time (self):
        """
        Calculates and returns the updated wait time since the last callback.

        This method computes the time elapsed since the last recorded callback
        and updates the wait time based on the number of messages processed.

        Returns:
            float: The updated wait time since the last callback.
        """
        if not hasattr(self, 'last_callback_time'):  # Initialize if not already set
            self.last_callback_time = time.time()
        current_time = time.time()
        l = (current_time - self.last_callback_time)
        self.time_since_last_call = self.time_since_last_call + l/ sum(self.message_count.values())
        
        self.last_callback_time = current_time
        return self.time_since_last_call