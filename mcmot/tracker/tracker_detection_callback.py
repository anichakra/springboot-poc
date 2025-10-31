import base64
import logging

import cv2
import numpy as np
from deep_sort_realtime.deepsort_tracker import DeepSort

from framework.utils.prediction_utils import update_kalman_filters, predict_kalman_filters
from framework import MessageProducer
from framework.frame_synchronization.frame_cache import FrameCache

logger = logging.getLogger("application")

def _decode_frame(frame_data):
    """
        Decodes a base64-encoded frame string into an image in the form of a numpy array.

        Args:
        frame_data (str): A base64-encoded string representing image frame data.

        Returns:
        numpy.ndarray: The decoded image as a numpy array in BGR color space.

        Raises:
        ValueError: If the decoded frame is invalid or empty.
        Exception: If any other error occurs during decoding.
    """
    try:
        frame_binary = base64.b64decode(frame_data)  # Decode base64 string to bytes
        frame_np = np.frombuffer(frame_binary, dtype=np.uint8)  # Convert to numpy array
        decoded_frame = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)  # Decode image

        # Ensure frame is valid after decoding
        if decoded_frame is None or decoded_frame.size == 0:
            raise ValueError("Decoded frame is invalid or empty.")

        return decoded_frame
    except Exception as e:
        logger.error("Failed to decode frame data:", exc_info=e)
        raise e


class TrackerDetectionCallback:
    """
    Tracks and processes detected objects and frames using DeepSort tracker and Kalman Filter integration.

    Provides mechanisms to handle detected frames, process older cached frames, manage multiple
    camera streams with individual trackers, and produce tracking results. The class ensures proper
    tracking and association of detected objects using various parameters like IoU distance,
    detection score threshold, non-max suppression overlap, and more. It also supports processing
    previously captured frames for prediction enhancement.

    Attributes:
        producer: A message producer instance used to send processed tracking results.
        outbound_topic: Topic name for sending the tracking results.
        captured_frames_cache: A frame cache instance for storing and retrieving frames.
        max_iou_distance: Maximum IoU distance for object association during tracking.
        max_age: Maximum frames to keep a track active without being updated.
        detection_score_threshold: Minimum score required for a detection to be considered valid.
        nms_max_overlap: Maximum allowed overlap ratio during non-maximum suppression.
        gating_only_position: Flag to enable gating with position only during tracking.
        match_detection: Flag to enforce matching between detections and tracked objects.
        prediction_factor: Factor to determine prediction-related frame processing.
        only_confirmed_tracks: Flag to allow only confirmed tracks.
        trackers: Dictionary of DeepSort tracker instances for each camera ID.
        kf_lists: Dictionary of Kalman filter lists associated with each camera ID.
        last_frame_timestamp: Dictionary to store the last processed frame timestamp per camera ID.

    Methods:
        __init__: Initializes the tracker with required configurations and parameters.
        callback: Processes the main detected frame message and updates object tracks.
        get_tracked_detections: Filters and matches tracked objects with incoming detections.
        process_captured_frames: Processes older frames from the cache based on timestamps.
        track_captured_frames: Tracks objects in previously captured frames and updates the system.
    """

    def __init__(self, producer: MessageProducer, outbound_topic, captured_frames_cache: FrameCache
                 , max_iou_distance: float, max_age: int, detection_score_threshold: float, nms_max_overlap: float,
                 gating_only_position: bool, match_detection: bool, prediction_factor: float, only_confirmed_tracks: bool):
        """
        Initializes an object for managing and tracking detected frames while maintaining
        metadata such as Kalman filters, IOU distance, and other tracking-specific parameters.
        Provides mechanisms to configure how tracking operates, manage previously captured
        frames, and interface with external message producers for output delivery.

        Parameters
        ----------
        producer : MessageProducer
            Instance of a message producer, handles outbound communication.
        outbound_topic : str
            The designated topic for outbound messages.
        captured_frames_cache : FrameCache
            Cache system to hold information about previously captured frames.
        max_iou_distance : float
            Maximum allowed Intersection Over Union (IOU) distance for association.
        max_age : int
            Maximum allowed time steps to keep the tracker alive without updates.
        detection_score_threshold : float
            Minimum confidence score for detections to be considered.
        nms_max_overlap : float
            Maximum overlap ratio for non-maximum suppression during detection association.
        gating_only_position : bool
            Indicates whether to use only position for gating in data association.
        match_detection : bool
            Specifies if detection matching is to be performed.
        prediction_factor : float
            Factor controlling the prediction mechanism for trackers.
        only_confirmed_tracks : bool
            Whether to process only confirmed tracks or include tentative ones.

        Attributes
        ----------
        prediction_factor : float
            Factor influencing prediction span for the tracking mechanism.
        outbound_topic : str
            Defines the topic used for outbound messages.
        captured_frames_cache : FrameCache
            Cache storing metadata about frames from associated cameras.
        producer : MessageProducer
            Interface responsible for message outbound operations.
        max_iou_distance : float
            Threshold defining IOU allowed for associating objects.
        max_age : int
            Maximum allowable lifespan of inactive trackers.
        nms_max_overlap : float
            Overlap threshold used in non-maximum suppression.
        detection_score_threshold : float
            Minimum score necessary for validated detections.
        match_detection : bool
            Indicates if matching of detection entities is considered.
        gating_only_position : bool
            Determines whether gating uses position exclusively.
        only_confirmed_tracks : bool
            If true, processes only confirmed tracker entities.

        """
        self.last_frame_timestamp = {}
        self.prediction_factor = prediction_factor
        self.outbound_topic = outbound_topic
        self.captured_frames_cache = captured_frames_cache
        self.producer = producer
        self.max_iou_distance = max_iou_distance
        self.max_age = max_age
        self.nms_max_overlap = nms_max_overlap
        self.detection_score_threshold = detection_score_threshold
        self.match_detection = match_detection
        self.gating_only_position = gating_only_position
        self.only_confirmed_tracks=only_confirmed_tracks
        self.trackers = {}
        self.kf_lists = {}  # Manage Kalman filters per camera

    def callback(self, message):
        """
        Processes an incoming message containing frame data and associated metadata, handles
        object tracking using DeepSort, and updates detection and frame information for further
        processing or production to an output topic.

        Parameters:
            message (dict): The incoming message containing the following keys:
                - frame_number (int): The identifier of the current frame.
                - frame (bytes): Encoded frame data.
                - frame_metadata (dict): Metadata associated with the frame.
                - frame_timestamp (float): Timestamp of the frame in seconds.
                - detections (list[dict]): List of detected objects, where each detection contains:
                    - bbox (list[float]): Bounding box coordinates in [x1, y1, x2, y2] format.
                    - score (float): Confidence score of the detection.
                    - class (str): Class name or identifier of the detected object.
                - camera_metadata (dict): Metadata of the capturing camera, including:
                    - camera_id (str): Identifier of the camera.

        Raises:
            Exception: If any error occurs during processing, the exception is logged and re-raised.

        Note:
            This function integrates object tracking, assigns Kalman filters, and processes the
            captured frames. It also ensures minimal confidence thresholds for valid detections
            and passes processed data to an external producer for publishing. The logging statements
            within the function are intended for debugging.
        """
        try:

            # Extract frame attributes
            # logger.debug("Type of Tracker Message:: %s", type(message))
            # logger.debug("Tracker Message: %s", message)
            frame_number = message['frame_number']

            frame = message['frame']
            frame_metadata = message['frame_metadata']
            frame_timestamp = message['frame_timestamp']
            detections = message['detections']
            camera_metadata = message['camera_metadata']
            camera_id = camera_metadata['camera_id']  # Retrieve the camera ID from the message
            #logger.debug("Processing frame (detected): %s %s %s", frame_number, frame_timestamp, camera_id)
            self.captured_frames_cache.add_camera(camera_id)
            # Ensure the camera_id exists in the tracker dictionary
            if camera_id not in self.trackers:
                self.trackers[camera_id] = DeepSort(
                    max_iou_distance=self.max_iou_distance,
                    max_age=self.max_age,
                    nms_max_overlap=self.nms_max_overlap,
                    gating_only_position=self.gating_only_position
                )

            # Initialize Kalman filter list for the camera if not already done
            if camera_id not in self.kf_lists:
                self.kf_lists[camera_id] = []

            # Process the current detected frame
            decoded_frame = _decode_frame(frame)

            track_input = [
                (
                    [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]],
                    # Convert [x1, y1, x2, y2] to [left, top, width, height]
                    score,
                    clazz
                )
                for detection in detections
                for bbox, score, clazz in [(detection['bbox'], detection['score'], detection['class'])] if
                score > self.detection_score_threshold  # Enforce minimum score threshold here
            ]

            tracks = self.trackers[camera_id].update_tracks(track_input, frame=decoded_frame)
            #logger.debug("Detected frame tracks: %s", tracks)

            detections = self.get_tracked_detections(detections, tracks)
            
            self.process_captured_frames(camera_id, frame_timestamp)

            producer_message = {
                'frame_number': frame_number,
                'frame_timestamp': frame_timestamp,
                'frame': frame,
                'frame_metadata': frame_metadata,
                'camera_metadata': camera_metadata,
                'detections': detections
            }

            self.producer.produce_message(self.outbound_topic, producer_message)
            
            # Update Kalman filter list for the current camera
            self.kf_lists[camera_id] = update_kalman_filters(
                detections, self.kf_lists[camera_id]
            )
            logger.debug("%s %s (d) %s", frame_number, camera_id, len(detections))
            self.last_frame_timestamp[camera_id] = frame_timestamp

        except Exception as e:
            logger.error("Exception in TrackerReidCallback callback function:", exc_info=e)
            raise e

    def get_tracked_detections(self, detections, tracks):
        """
        Retrieves a list of tracked detections filtered and processed based on the given detection and track data. Only tracks that meet the specified conditions (e.g., confirmed status, matched detections, valid bounding boxes) are included in the result.

        Args:
            detections (list[dict]): A list of detection data. Each detection is represented
                as a dictionary containing a 'bbox' key, which is a list representing
                the bounding box [min_x, min_y, max_x, max_y].
            tracks (list): A list of track objects. Each track should have methods
                and attributes such as `is_confirmed`, `to_tlbr`, and `track_id`.

        Returns:
            list[dict]: A list of processed tracked detections. Each detection
            dictionary includes the keys:
                - 'id': The identifier of the track.
                - 'bbox': List representing the bounding box as [min_x, min_y, max_x, max_y].
                - 'color': The assigned color as an RGB tuple, with the current configuration as yellow (255, 255, 0).
        """
        original_boxes = [detection['bbox'] for detection in detections if len(detection['bbox']) == 4]

        detections = []
        for track in tracks:
            #logger.debug("Tracks confirmed: %s", track.is_confirmed())

            if not track.is_confirmed() and self.only_confirmed_tracks:
                continue
            bbox = track.to_tlbr()  # [min_x, min_y, max_x, max_y]
            #logger.debug("Bbox: %s", bbox)
            track_id = track.track_id

            if len(bbox) != 4 or any(coord is None for coord in bbox):  # Skip invalid boxes
                continue
            if self.match_detection:
                # Check if the tracked box matches any original detection
                valid = any(
                    calculate_iou(bbox, original_box) >= self.max_iou_distance
                    for original_box in original_boxes
                )

                if not valid:
                    #logger.debug(f"Discarding ghost track ID {track_id} with BBox {bbox}.")
                    continue

            try:
                detections.append({
                    'id': track_id,
                    'bbox': [int(coord) for coord in bbox],
                    'color': (255, 255, 0)  # Yellow color
                })
            except (ValueError, TypeError) as e:
                logger.error(f"Error processing track ID {track_id}: {e}")
        # Create a message with the filtered tracked detections
        #logger.debug("Detections in detected frames: %s", detections)
        return detections

    def process_captured_frames(self, camera_id, frame_timestamp):
        """
        Processes captured frames for a given camera, retrieving and handling older frames.
        It retrieves frames from the cache that have a timestamp less than the specified
        frame_timestamp, excluding the frame with the exact frame_timestamp, then selects
        a subset based on the prediction factor, and processes them further.

        Args:
            camera_id: The unique identifier of the camera whose frames are being processed.
            frame_timestamp (int): The timestamp of the frame to process and compare against.

        Raises:
            Any exceptions raised internally due to processing logic or cache retrieval issues
            will be managed by the implementation or propagated to the caller.

        Returns:
            None
        """
        # Retrieve and remove frames with timestamps < frame_timestamp from cache
        last_timestamp = self.last_frame_timestamp.get(camera_id, 0)
        older_frames = self.captured_frames_cache.get_frame_cache(camera_id).get_and_remove_frames_between(
            last_timestamp, frame_timestamp)
        #logger.debug("This timestamp: %s", frame_timestamp)

        # Log the timestamps of older frames
        #logger.debug("Timestamps of older frames: %s", [frame['frame_timestamp'] for frame in older_frames])
        #logger.debug("Retrieved %d frames older than timestamp %s", len(older_frames), frame_timestamp)
        # Exclude the current frame (with the exact timestamp) from older_frames
        older_frames = [
            old_frame for old_frame in older_frames
            if old_frame['frame_timestamp'] != frame_timestamp
        ]
        selected_frames = extract_elements(older_frames, self.prediction_factor)
        # Process the selected frames
        for old_frame in selected_frames:
            self.track_captured_frames(old_frame)

    def track_captured_frames(self, old_frame):
        """
        Processes a previously captured frame by decoding, predicting objects, tracking, and
        publishing the detections to an outbound topic. Ensures proper bounding box validation
        and frame handling during the process.

        Parameters:
            old_frame (dict): A dictionary containing the following keys:
                - 'frame_number' (int): The frame number of the captured frame.
                - 'frame' (ndarray): Encoded image data of the frame.
                - 'frame_metadata' (dict): Metadata associated with the frame.
                - 'frame_timestamp' (float): Timestamp of when the frame was captured.
                - 'camera_metadata' (dict): Metadata specific to the camera that captured
                  the frame, including 'camera_id'.

        Returns:
            None

        Raises:
            None
        """
        old_frame_number = old_frame['frame_number']
        old_frame_data = old_frame['frame']
        old_frame_metadata = old_frame['frame_metadata']
        old_frame_timestamp = old_frame['frame_timestamp']
        old_camera_metadata = old_frame['camera_metadata']
        #logger.debug("Processing frame (captured): %s %s %s", old_frame_number, old_frame_timestamp, old_camera_metadata["camera_id"])
        decoded_old_frame = _decode_frame(old_frame_data)
        # Predict using the Kalman Filters specific to this camera
        old_camera_id = old_frame["camera_metadata"]["camera_id"]
        predictions = predict_kalman_filters(self.kf_lists[old_camera_id])
        #logger.debug("Predictions: %s", predictions)
        track_input = [
            (
                [bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]],
                score,
                clazz
            )
            for detection in predictions
            for bbox, score, clazz in [(detection['bbox'], detection['score'], detection['class'])]
            if not (
                    bbox[0] < 0 or bbox[1] < 0 or bbox[2] <= bbox[0] or bbox[3] <= bbox[1]  # Ensure bounding box coordinates are valid
                    or (decoded_old_frame[bbox[1]:bbox[3], bbox[0]:bbox[2]] is None)  # Get the crop
                    or (decoded_old_frame[bbox[1]:bbox[3],bbox[0]:bbox[2]].size == 0)  # Ensure the cropped image is not empty
            )
        ]

        tracks = self.trackers[old_camera_metadata["camera_id"]].update_tracks(track_input, frame=decoded_old_frame)
        detections = self.get_tracked_detections(predictions, tracks)

        # Create a message for the current detected frame
        producer_message = {
            'frame_number': old_frame_number,
            'frame_timestamp': old_frame_timestamp,
            'frame': old_frame_data,
            'frame_metadata': old_frame_metadata,
            'camera_metadata': old_camera_metadata,
            'detections': detections
        }
        # Send current frame to tracker
        self.producer.produce_message(self.outbound_topic, producer_message)
        logger.debug("%s %s (c) %s ", old_frame_number, old_camera_id, len(detections))


def calculate_iou(box1, box2):
    """
        Calculate the Intersection over Union (IoU) of two bounding boxes.

        This function determines the degree of overlap between two rectangular
        regions defined by their bounding box coordinates. IoU is a metric widely
        used in computer vision tasks, such as object detection, to evaluate
        how well bounding boxes predicted by a model match ground truth boxes.
        The IoU is calculated as the ratio of the overlap area to the
        combined area of the two bounding boxes.

        Args:
            box1: A list or tuple of four floats or integers representing the
                (x1, y1, x2, y2) coordinates of the first bounding box.
            box2: A list or tuple of four floats or integers representing the
                (x1, y1, x2, y2) coordinates of the second bounding box.

        Returns:
            A float representing the IoU value. The result ranges between 0 and 1,
            where 0 indicates no overlap and 1 indicates complete overlap.
    """
    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])
    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    # Calculate the area of intersection
    intersection = max(0, x2 - x1) * max(0, y2 - y1)

    # Calculate the area of both bounding boxes
    box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
    box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])

    # Calculate the union area
    union = box1_area + box2_area - intersection

    # Avoid division by zero
    if union == 0:
        return 0

    return intersection / union

def extract_elements(lst, fc):
    """
    Extracts a specific number of elements from a list, evenly distributed
    based on the given factor.

    This function allows selecting elements from a list such that the resulting
    elements are spaced as evenly as possible, determined by the `fc` factor.

    Parameters:
        lst (list): The original list from which elements will be extracted.
        fc (float): A factor between 0 and 1 determining the portion of the list
                    to select. Values outside this range will result in an error.

    Raises:
        ValueError: If the `fc` factor is not between 0 and 1.

    Returns:
        list: A list of selected elements, distributed approximately equally
              according to the given factor.
    """
    if not (0 <= fc <= 1):
        raise ValueError("Factor 'fc' must be between 0 and 1.")

    n = len(lst)
    num_to_select = int(n * fc + 0.5)  # Round to nearest whole number

    if num_to_select == 0:
        return []

    # Calculate the step size
    step_size = n / num_to_select

    # Select elements with a regular distribution
    selected_indices = [int(i * step_size) for i in range(num_to_select)]
    selected_elements = [lst[i] for i in selected_indices]

    return selected_elements
