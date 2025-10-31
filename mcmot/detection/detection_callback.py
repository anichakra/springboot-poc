import base64
import logging
import random

import cv2
import numpy as np
import torch
from ultralytics import YOLO

from framework.utils.prediction_utils import predict_kalman_filters, update_kalman_filters, kf_list
from framework import MessageProducer

logger = logging.getLogger("application")

color_green = (0, 255, 0)  # Green bounding box

def detect_boundaries_boxes(results, detection_classes: list):
    """
    Detects boundary boxes from the given results and filters them based on specified detection classes.

    This function processes the results from object detection models, extracting the bounding box
    coordinates, confidence scores, and class information. It supports filtering by specific
    detection classes if provided. The bounding boxes, class names, confidence scores, and other
    metadata are returned in a structured format.

    Parameters:
        results (list): A list of detection result objects. Each result object contains detection
            metadata (e.g., bounding boxes, confidence scores, class IDs).
        detection_classes (list): A list of class names to filter the detections. If empty or None,
            detections for all classes will be included.

    Returns:
        list: A list of dictionaries, where each dictionary contains information about a detected
        object, including its bounding box coordinates, class name, confidence score, detection
        model used, and assigned color.
    """
    detections = []

    for result in results:
        for det in result.boxes:
            # Extract and scale bounding box coordinates
            x1, y1, x2, y2 = map(int, det.xyxy[0])
            # Extract confidence and class information
            confidence = float(det.conf)  # Confidence score
            if detection_classes:
                for detection_class in detection_classes:
                    if detection_class in result.names[int(det.cls)]:  # Filter for the "person" class (customize as needed)
                        detections.append({
                            'class': detection_class,
                            'bbox': [x1, y1, x2, y2],
                            'score': round(confidence, 3),
                            'model': 'yolo',
                            'color': color_green

                        })
            else:
                # get the class
                cls = int(det.cls[0])

                # get the class name
                class_name = result.names[cls]
                detections.append({
                    'class': class_name,
                    'bbox': [x1, y1, x2, y2],
                    'score': round(confidence, 3),
                    'model': 'yolo',
                    'color': get_colours(cls)
                })
    return detections


# Function to get class colors
def get_colours(cls_num):
    """
    Generate a unique color based on a class number.

    The function iteratively generates a unique color for a given class
    number by assigning base colors and applying incremental adjustments
    using pre-defined patterns.

    Args:
        cls_num (int): The class number used to determine the color.

    Returns:
        tuple: A tuple representing the RGB color in the format (R, G, B),
        where each component is an integer between 0 and 255.
    """
    base_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    color_index = cls_num % len(base_colors)
    increments = [(1, -2, 1), (-2, 1, -1), (1, -1, 2)]
    color = [base_colors[color_index][i] + increments[color_index][i] *
    (cls_num // len(base_colors)) % 256 for i in range(3)]
    return tuple(color)


def detect(frame, model, device, confidence_score,detection_classes: list):
    """
    Detects objects in an image using a provided machine learning model and returns the detections.

    Decodes an input image from a base64 string, processes it with a machine learning
    model to detect objects and their boundaries, then scales detections back to the
    original image dimensions and returns the detected objects.

    Args:
        frame (str): The input image encoded as a base64 string.
        model: The object detection model used for processing the image.
        device: The device to execute the model on (e.g., "cpu", "cuda").
        confidence_score (float): Minimum confidence score threshold for detections.
        detection_classes (list): List of class names to filter detections by.

    Returns:
        list: The detections scaled to the original image size.
    """
    try:
        # Decode base64 string to bytes
        frame_data = base64.b64decode(frame)
        # Convert bytes to numpy array
        frame_np = np.frombuffer(frame_data, dtype=np.uint8)
        # Decode image
        frame_decoded = cv2.imdecode(frame_np, cv2.IMREAD_COLOR)

        # Get original frame dimensions

        results = model(frame_decoded, show=False, conf=confidence_score, save=False, device=device, verbose=False)

        # Extract detections and scale them back to the original image size
        detections = detect_boundaries_boxes(results, detection_classes)
        return detections
    except Exception as e:
        print("Exception in detect:", str(e))
        raise e

class DetectionCallback:
    """
    Handles detection callback operations related to video frame processing, applying object
    detection models, and communicating processed results through a message producer.

    This class is designed to process video frames by applying an object detection model (YOLO),
    filter detections using a Kalman filter, and produce messages containing detection results.
    It supports different configurations such as confidence thresholds, prediction mechanisms,
    and dynamic adjustment of detection thresholds for advanced usage.

    Attributes:
        device: The computation device to be used ('cpu', 'cuda', or 'mps').
        outbound_topic: The topic name for sending processed messages.
        detection_class: The class or type of object to detect in the frames.
        yolo: The YOLO model instance used for detection.
        frame_count: Counts the number of frames processed.
        random_threshold: Randomized threshold controlling detection versus prediction.
        kf_list_local: Local list of Kalman filters initialized for detection tracking.
        confidence_score: Confidence threshold for YOLO to classify detections.
        predict: Boolean flag to enable prediction using Kalman filters.
        producer: Message producer used to send the processed detection messages.
        buffer: Accumulated buffer of processed messages waiting to be sent.

    Methods:
        __init__: Initializes the DetectionCallback instance with required configurations.
        callback: Processes incoming frame messages, performs detection or prediction,
                  and communicates processed data through the producer.
    """
    def __init__(self, producer: MessageProducer, outbound_topic: str, device_type: str, model: str,
                 detection_class, confidence_score: float, predict: bool = False):
        self.device = torch.device(
            device_type if device_type else ("mps" if torch.backends.mps.is_available() else "cpu"))
        self.outbound_topic = outbound_topic
        self.detection_class = detection_class
        self.yolo = YOLO(model)
        self.frame_count = 0
        self.random_threshold = 1.0
        self.kf_list_local = kf_list
        self.confidence_score = confidence_score
        self.predict = predict
        self.producer = producer

        self.buffer = []

    def callback(self, message):
        """
        Processes incoming message, performs detection or prediction, and sends the
        processed message to an outbound topic. The function is responsible for managing
        frame data, applying detection or Kalman filter predictions, and adjusting the
        random threshold to control detection probability.

        Parameters:
            message (dict): The message containing frame data and metadata to be
                processed. Must include at least the keys 'frame', 'frame_metadata',
                'camera_metadata', 'frame_number', and 'frame_timestamp'.

        Raises:
            KeyError: If the required keys are missing in the provided message.

        """
        if isinstance(message, dict):
            self.buffer.append(message)

            frame = message['frame']
            frame_metadata = message['frame_metadata']
            camera_metadata = message["camera_metadata"]

            detected_message = {
                'frame_number': message['frame_number'] ,
                'frame_timestamp': message['frame_timestamp'],
                'frame': frame,
                'frame_metadata': frame_metadata,
                'camera_metadata': camera_metadata
            }

            if random.random() < self.random_threshold:
                detections = detect(frame, self.yolo, self.device, self.confidence_score, self.detection_class)
                detected_message['detections'] = detections
                self.kf_list_local = update_kalman_filters(detections, self.kf_list_local)
                logging.debug("Detections: %s", detections)

            else:
                predictions = predict_kalman_filters(self.kf_list_local)
                detected_message['detections'] = predictions


            self.producer.produce_message(self.outbound_topic, detected_message)
            self.frame_count += 1
            if self.predict and self.frame_count > 700 and self.frame_count % 100 == 0 and self.random_threshold > 0.5:
                self.random_threshold -= 0.05
