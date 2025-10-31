import numpy as np
from pykalman import KalmanFilter  # Install this package if not installed

color_blue = (255, 0, 0)  # Blue bounding box

# Store YOLO bounding boxes and velocity using Kalman filters
kf_list = []  # A list of Kalman filters, one for each detected object
tracked_objects = []  # Track object IDs with their Kalman filters

def initialize_kalman_filter(bbox):
    """
        Initializes and configures a Kalman filter using a bounding box. The Kalman filter
        is set up with predefined transition and observation matrices suitable for
        tracking the object's position and dimensions over time. It also initializes
        the state vector and covariance matrix.

        The provided bounding box coordinates are used to generate the initial state
        of the Kalman filter, specifically extracting the x, y coordinates, width,
        and height.

        Parameters:
            bbox (list[float]): A list representing the bounding box with the format
            [x_min, y_min, x_max, y_max].

        Returns:
            KalmanFilter: A configured Kalman filter object ready for tracking.
    """
    x, y, width, height = bbox[0], bbox[1], bbox[2] - bbox[0], bbox[3] - bbox[1]
    kf = KalmanFilter(
        transition_matrices=np.array([
            [1, 0, 1, 0, 0.5, 0],
            [0, 1, 0, 1, 0, 0.5],
            [0, 0, 1, 0, 1, 0],
            [0, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1],
        ]),
        observation_matrices=np.array([
            [1, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 1],
        ])
    )
    initial_state = [x, y, 0, 0, width, height]
    kf.initial_state_mean = initial_state
    kf.initial_state_covariance = np.eye(6) * 1e-2  # Adjust covariance as needed
    return kf


def update_kalman_filters(detections, kf_list, max_unmatched_frames=3, match_threshold=50):
    """
    Updates a list of Kalman filters based on detected objects and matches them with the
    provided detections. Kalman filters that do not get matched are tracked for unmatched
    frames, and new Kalman filters are initialized for unmatched detections. Filters with
    too many unmatched frames are removed.

    Args:
        detections (list): A list of detection dictionaries. Each detection dictionary
            should contain a 'bbox' key with the bounding box coordinates defined as
            [xmin, ymin, xmax, ymax].
        kf_list (list): A list of existing Kalman filter objects. Each Kalman filter must
            support methods and attributes for state prediction, updating, and tracking
            unmatched frames.
        max_unmatched_frames (int, optional): The maximum number of consecutive frames a
            Kalman filter can remain unmatched before being removed from the list. Default
            is 3.
        match_threshold (float, optional): Maximum allowable Euclidean distance between a
            Kalman filter's predicted state and a detection to consider them as a match.
            Default is 50.

    Returns:
        list: An updated list of Kalman filter objects after processing new detections and
        handling matching logic. Each filter in the list is either an updated filter from
        the input list or a new filter created for unmatched detections.
    """
    updated_kf_list = []
    used_detections = set()  # Track detections already matched to Kalman filters

    for kf in kf_list:
        # Increment unmatched frame count if no match is found
        if hasattr(kf, "unmatched_frames"):
            kf.unmatched_frames += 1
        else:
            kf.unmatched_frames = 0

        # Get Kalman filter's predicted state
        filtered_state_mean = kf.initial_state_mean
        filtered_state_covariance = kf.initial_state_covariance
        predicted_state_mean, predicted_state_covariance = kf.filter_update(
            filtered_state_mean=filtered_state_mean,
            filtered_state_covariance=filtered_state_covariance,
        )
        kf.initial_state_mean = predicted_state_mean
        kf.initial_state_covariance = predicted_state_covariance

        # Match the Kalman filter to the closest YOLO detection
        best_match = None
        best_distance = float("inf")
        for i, det in enumerate(detections):
            if i in used_detections:
                continue
            bbox = det["bbox"]
            x, y = (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2  # Center of bounding box
            det_center = np.array([x, y])
            kf_center = np.array([predicted_state_mean[0], predicted_state_mean[1]])

            # Calculate Euclidean distance
            distance = np.linalg.norm(det_center - kf_center)

            if distance < best_distance:
                best_distance = distance
                best_match = i

        # Update Kalman filter with the matched detection
        if best_match is not None and best_distance < match_threshold:
            used_detections.add(best_match)
            bbox = detections[best_match]["bbox"]
            x, y = (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2
            width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
            updated_observation = np.array([x, y, width, height])

            predicted_state_mean, predicted_state_covariance = kf.filter_update(
                filtered_state_mean=predicted_state_mean,
                filtered_state_covariance=predicted_state_covariance,
                observation=updated_observation,
            )
            kf.initial_state_mean = predicted_state_mean
            kf.initial_state_covariance = predicted_state_covariance
            kf.unmatched_frames = 0  # Reset unmatched frames
            updated_kf_list.append(kf)
        else:
            # Only keep Kalman filter if it hasn't been unmatched for too long
            if kf.unmatched_frames < max_unmatched_frames:
                updated_kf_list.append(kf)

    # Create new Kalman filters for unmatched detections
    for i, det in enumerate(detections):
        if i not in used_detections:
            bbox = det["bbox"]
            # Ignore detections smaller than a threshold (likely noise)
            bbox_width = bbox[2] - bbox[0]
            bbox_height = bbox[3] - bbox[1]
            if bbox_width > 10 and bbox_height > 10:  # Adjust this threshold as needed
                new_kf = initialize_kalman_filter(bbox)
                updated_kf_list.append(new_kf)

    return updated_kf_list


def predict_kalman_filters(kf_list):
    """
    Predict bounding boxes and confidence scores using a list of Kalman filters.

    This function iterates over a list of Kalman filter objects, retrieves their
    predicted states, and uses these predictions to calculate bounding box
    coordinates, confidence scores, and other associated metadata. Predictions are
    then filtered based on specific criteria, such as bounding box area or position.
    The filtered results are compiled into a list of dictionaries representing the
    predicted bounding boxes.

    Parameters:
        kf_list (list): A list of Kalman filter objects. Each Kalman filter object
            should have attributes 'initial_state_mean' and
            'initial_state_covariance', as well as a method `filter_update` that
            returns an updated state mean and predicted covariance.

    Returns:
        list: A list of dictionaries, where each dictionary represents a predicted
        bounding box. Each dictionary contains the following keys:
          - 'class' (str): Always set to 'person' (indicating the object class).
          - 'bbox' (list): A list of four integers specifying the bounding box
            [x1, y1, x2, y2].
          - 'score' (float): The confidence score normalized between 0 and 1, rounded
            to 3 decimal places.
          - 'model' (str): Always set to 'kalman' (indicating the prediction method).
          - 'color' (str): The color string for the bounding box (e.g., 'blue').
    """
    predictions = []
    print("---------------")
    for kf in kf_list:
        # Retrieve Kalman filter's predicted state
        filtered_state_mean = kf.initial_state_mean
        filtered_state_covariance = kf.initial_state_covariance

        # Predict the next state
        state_mean, predicted_covariance = kf.filter_update(  # Returns updated covariance
            filtered_state_mean=filtered_state_mean,
            filtered_state_covariance=filtered_state_covariance,
        )

        # Extract predicted bounding box coordinates
        x, y, _, _, width, height = state_mean
        x1, y1 = int(x - width // 2), int(y - height // 2)
        x2, y2 = int(x + width // 2), int(y + height // 2)

        # Compute uncertainty (e.g., based on position variances)
        # Variance is the diagonal of the covariance matrix
        position_variance_x = predicted_covariance[0, 0]
        position_variance_y = predicted_covariance[1, 1]
        overall_uncertainty = np.sqrt(position_variance_x + position_variance_y)

        # Normalize confidence (can be adjusted based on application needs)
        confidence = 1 / (1 + overall_uncertainty)  # Higher variance -> lower confidence

        # Apply a threshold or filter predictions if confidence is too low
        area = (x2 - x1) * (y2 - y1)
        if (area < 10000 and y1 > 200) or y2 > 400:
            continue

        predictions.append({
            'class': 'person',
            'bbox': [x1, y1, x2, y2],
            'score': round(confidence, 3),
            'model': 'kalman',
            'color': color_blue
        })

        print([x1, y1, x2, y2], area, f"Confidence: {confidence:.2f}")
    return predictions
