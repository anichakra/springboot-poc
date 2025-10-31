class TrackerConfiguration:
    """
    Defines the configuration parameters for a tracker.

    The TrackerConfiguration class encapsulates configuration parameters used in a tracking system.
    This class is designed to provide a structured way of specifying and validating parameters such
    as distance thresholds, age limits, non-maximum suppression overlap thresholds, and other settings
    important for tracking logic. The configuration ensures that parameter values fall within acceptable
    ranges to avoid errors during runtime. Additionally, it supports optional parameters such as
    camera identification for more contextual usage.

    Attributes:
        max_iou_distance (float): The maximum Intersection over Union (IoU) distance allowed for
            matching, ranging between 0 and 1.
        max_age (int): The maximum age of a track before it is removed, must be greater than 0.
        nms_max_overlap (float): The maximum allowed overlap ratio for non-maximal suppression,
            ranging between 0 and 1.
        detection_score_threshold (float): The detection score threshold for considering a detection,
            ranging between 0 and 1.
        gating_only_position (bool): Indicates whether gating is applied only based on position.
        ignore_capture (bool): Determines if capture events should be ignored during tracking.
        match_detection (bool): Indicates whether detections are matched within the tracker.
        prediction_factor (float): The prediction reliability factor, ranging between 0 and 1.
        only_confirmed_tracks (bool): Whether to process only confirmed tracks.
        camera_id (str, optional): The identifier for the camera associated with the tracked object. This is required if this tracker is tracking only one camera feed.

    Methods:
        __init__(self, max_iou_distance, max_age, nms_max_overlap, detection_score_threshold,
                 gating_only_position, ignore_capture, match_detection, prediction_factor,
                 only_confirmed_tracks, camera_id):
            Initializes the TrackerConfiguration instance with specified parameters, validating
            the range and types of values where applicable.

        __str__(self):
            Returns a string representation of the TrackerConfiguration instance, summarizing
            the settings.
    """

    def __init__(self, max_iou_distance: float, max_age: int, nms_max_overlap: float, detection_score_threshold: float,
                 gating_only_position: bool,
                 ignore_capture: bool, match_detection: bool, prediction_factor: float, only_confirmed_tracks: bool,
                 camera_id: str = None):
        self.match_detection = match_detection
        self.detection_score_threshold = detection_score_threshold if 0 <= detection_score_threshold <= 1 else ValueError(
            "detection_score_threshold must be between 0 and 1")
        self.max_iou_distance = max_iou_distance if 0 <= max_iou_distance <= 1 else ValueError(
            "max_iou_distance must be between 0 and 1")
        self.ignore_capture = ignore_capture
        self.max_age = max_age if max_age > 0 else ValueError("max_age must be greater than 0")
        self.nms_max_overlap = nms_max_overlap if 0 <= nms_max_overlap <= 1 else ValueError(
            "nms_max_overlap must be between 0 and 1")
        self.gating_only_position = gating_only_position
        self.prediction_factor = prediction_factor if 0 <= prediction_factor <= 1 else ValueError(
            "prediction_factor must be between 0 and 1")
        self.only_confirmed_tracks = only_confirmed_tracks
        self.camera_id = camera_id

    def __str__(self):
        return (f"TrackerConfiguration("
                f"max_iou_distance={self.max_iou_distance}, "
                f"self.detection_score_threshold={self.detection_score_threshold}, "
                f"self.match_detection={self.match_detection}, "
                f"max_age={self.max_age}, "
                f"nms_max_overlap={self.nms_max_overlap}, "
                f"gating_only_position={self.gating_only_position}, "
                f"ignore_capture={self.ignore_capture}, "
                f"only_confirmed_tracks={self.only_confirmed_tracks}, "
                f"camera_id={self.camera_id}, "

                f"prediction_factor={self.prediction_factor} ")
