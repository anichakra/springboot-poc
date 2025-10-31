import random

import cv2
import numpy as np
from pykalman import KalmanFilter  # Install this package if not installed
from ultralytics import YOLO

from framework.utils.config_utils import read_config

# Store YOLO bounding boxes and velocity using Kalman filters
kf_list = []  # A list of Kalman filters, one for each detected object
tracked_objects = []  # Track object IDs with their Kalman filters


def initialize_kalman_filter(bbox):
    """
    Initialize a Kalman Filter for a detected bounding box.
    :param bbox: The bounding box [x1, y1, x2, y2].
    :return: KalmanFilter object.
    """
    x, y, width, height = bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]  # Convert to center + size state
    kf = KalmanFilter(
        transition_matrices=np.array([[1, 0, 1, 0, 0, 0],
                                      [0, 1, 0, 1, 0, 0],
                                      [0, 0, 1, 0, 0, 0],
                                      [0, 0, 0, 1, 0, 0],
                                      [0, 0, 0, 0, 1, 0],
                                      [0, 0, 0, 0, 0, 1]]),
        observation_matrices=np.array([[1, 0, 0, 0, 0, 0],  # x
                                       [0, 1, 0, 0, 0, 0],  # y
                                       [0, 0, 0, 0, 1, 0],  # width
                                       [0, 0, 0, 0, 0, 1]])  # height
    )
    initial_state = [x, y, 0, 0, width, height]  # Start with position and no velocity
    kf.initial_state_mean = initial_state
    kf.initial_state_covariance = np.eye(6) * 1e-2

    # Use random observations with correct shape during EM initialization
    random_observations = np.random.rand(100, 4)  # 100 samples of (x, y, width, height)
    kf = kf.em(random_observations, n_iter=5)  # Train the Kalman Filter with EM
    return kf


def update_kalman_filters(detections, kf_list):
    """
    Update Kalman filters using YOLO detections. Create new filters if necessary.
    :param detections: Detected bounding boxes from YOLO in format [{'class': 'person', 'bbox': [x1, y1, x2, y2]}].
    :param kf_list: List of existing Kalman filters.
    :return: Updated Kalman filter list.
    """
    updated_kf_list = []
    used_detections = set()  # To track detections already matched to Kalman filters

    for kf in kf_list:
        # Get Kalman filter current predicted state
        filtered_state_mean = kf.initial_state_mean
        filtered_state_covariance = kf.initial_state_covariance
        predicted_state_mean, predicted_state_covariance = kf.filter_update(
            filtered_state_mean=filtered_state_mean,
            filtered_state_covariance=filtered_state_covariance
        )
        kf.initial_state_mean = predicted_state_mean  # Update filter states
        kf.initial_state_covariance = predicted_state_covariance

        # Match the current Kalman filter to the closest YOLO detection
        best_match = None
        best_distance = float("inf")
        for i, det in enumerate(detections):
            if i in used_detections:
                continue
            bbox = det['bbox']
            x, y = (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2  # Center of bounding box
            det_center = np.array([x, y])

            # Compare detection center to Kalman filter predicted center
            kf_center = np.array([predicted_state_mean[0], predicted_state_mean[1]])
            distance = np.linalg.norm(det_center - kf_center)

            if distance < best_distance:  # Find closest detection
                best_distance = distance
                best_match = i

        # Update the Kalman filter with the matched detection
        if best_match is not None and best_distance < 50:  # Threshold to associate detection
            used_detections.add(best_match)
            bbox = detections[best_match]['bbox']
            x, y = (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2
            width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            updated_observation = np.array([x, y, width, height])

            # Update Kalman filter's observation
            predicted_state_mean, predicted_state_covariance = kf.filter_update(
                filtered_state_mean=predicted_state_mean,
                filtered_state_covariance=predicted_state_covariance,
                observation=updated_observation
            )
            kf.initial_state_mean = predicted_state_mean  # Update the Kalman filter state
            kf.initial_state_covariance = predicted_state_covariance

            updated_kf_list.append(kf)

    # Create new Kalman filters for unmatched detections
    for i, det in enumerate(detections):
        if i not in used_detections:
            bbox = det['bbox']
            new_kf = initialize_kalman_filter(bbox)
            updated_kf_list.append(new_kf)

    return updated_kf_list


def predict_kalman_filters(kf_list):
    """
    Predict bounding boxes using the Kalman filters.
    :param kf_list: List of Kalman filters.
    :return: Predicted bounding boxes in the format [x1, y1, x2, y2].
    """
    predictions = []
    for kf in kf_list:
        # Retrieve the initial state mean and covariance from the Kalman filter.
        filtered_state_mean = kf.initial_state_mean
        filtered_state_covariance = kf.initial_state_covariance

        # Predict the next state using filter_update
        state_mean, _ = kf.filter_update(
            filtered_state_mean=filtered_state_mean,
            filtered_state_covariance=filtered_state_covariance
        )

        # Extract predicted bounding box coordinates
        x, y, _, _, width, height = state_mean
        x1, y1 = int(x - width // 2), int(y - height // 2)
        x2, y2 = int(x + width // 2), int(y + height // 2)
        predictions.append([x1, y1, x2, y2])
    return predictions


def stream_video():
    yolo = YOLO("detection/model/yolov8n.pt")
    global kf_list
    config = read_config()
    video_url = "capture/video/" + config.get("video", "store/store-1.mp4")
    print(cv2.getBuildInformation())
    # Open the video using OpenCV
    cap = cv2.VideoCapture(video_url, cv2.CAP_FFMPEG)
    # cap = cv2.VideoCapture(video_url)
    if not cap.isOpened():
        print("Unable to open video stream with OpenCV.")

    # Stream the video frame by frame
    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            break
        if not cap.isOpened():
            print(f"Error opening video file {video_url}")
            return
        frame_count = 0  # Initialize frame counter
        random_threshold = 1.0  # Initial randomness threshold
        while True:
            ret, frame = cap.read()
            if not ret:
                # Restart the video when it reaches the end
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            # Display the frame (or process as needed)
            cv2.imshow("Frame", frame)

            if random.random() < random_threshold:
                # Frame passed to YOLO model
                results = yolo(frame)
                detections = []
                for result in results:
                    for det in result.boxes:
                        x1, y1, x2, y2 = map(int, det.xyxy[0])  # Bounding box coordinates
                        if 'person' in result.names[int(det.cls)]:  # Check if the detected object is a person
                            detections.append({'class': 'person', 'bbox': [x1, y1, x2, y2]})
                            # cv2.rectangle(detected_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Update Kalman filter with YOLO detections
                kf_list = update_kalman_filters(detections, kf_list)

            else:
                # Predict bounding boxes using Kalman filters
                predictions = predict_kalman_filters(kf_list)
                for x1, y1, x2, y2 in predictions:
                    # Draw predicted bounding boxes
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)  # Use blue for predictions

            cv2.imshow("Frame_detected", frame)
            frame_count += 1
            if frame_count > 700 and frame_count % 100 == 0 and random_threshold > 0.5:
                random_threshold -= 0.05

            # Break on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        # Release the video capture object and close OpenCV windows
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    stream_video()
