FRAME_SYNC = "frame-sync"


class FrameSyncConfiguration:
    """
    Represents a configuration class designed for managing frame synchronization
    and backlog validation in a multi-camera setup. It provides a detailed set
    of parameters to configure thresholds, intervals, synchronization types, and
    other related settings.

    This class is primarily used to ensure seamless synchronization of frames
    across multiple cameras or sources while adhering to specified latency and
    timing constraints. It enforces input validation and offers flexibility by
    using default values where applicable, ensuring robust configuration.

    Attributes:
        backlog_threshold (int): The backlog threshold value. Must be a positive
            integer if specified. When this threshold is reached then synchronization module is called.
        backlog_check_interval (float): The interval at which the backlog is
            checked. This is in seconds. Must be a non-negative float if specified.
        frame_sync_type (str): The type of frame synchronization. Accepted
            values are 'timestamp', 'number', or None. A frame can either or both of these two attributes. Which attribute to be used for frame synchronization has to be mentioned here.
        fps (int): Frames per second for synchronization. Defaults to 0. Must
            be greater than or equal to 0. When 0 then frame synchronization will use the FPS as mentioned in the frame's metadata otherwise it will use th fps mentioned here.
        retention_time (float): Timeout value (in seconds) for processing. A group of frames are synchronized and kept in a bucket and wait till all the cameras' frames are grouped for a particular timestamp or number. The unsettle group will wait till this time before getting eliminated from the cache.
            Defaults to 60. Must be greater than 0.
        latency_threshold (float): Maximum acceptable latency threshold for
            processing (in seconds). Defaults to 60.0. Must be greater than or
            equal to 0.
        ignore_initial_delay (bool): Flag to determine whether the initial delay
            should be ignored. Defaults to False. If True, at least one of
            `backlog_threshold` or `backlog_check_interval` must be provided. If its ignored then it will start reading from the last frame in the queue for processing ignoring others during initialization of the CV module.
        enable_sequencing (bool): Determines whether frame sequencing is
            enabled. If frame sequencing is required before synchronization. For already sequenced frames no need for sequencing. Defaults to False.
        seek_to_end (bool): Flag to determine whether the last frame in the
            topic offset should be used, ignoring all other frames. This takes
            precedence over other settings. When set to true then always the last frame from the queue will be processed disregarding other frames. So it will never create any delay or latency and run along with the previous module.
        unify (bool): Flag to enable unification of multi-source frames. If set to true then the grouping of frames for multiple cameras will be done and grouped frames will be send through callback mechanism to the CV module. The CV module's callback method will always get array of group of synchronized frames.
            Defaults to False.
    """

    def __init__(self, backlog_threshold: int = 0, backlog_check_interval: float = 0.0, frame_sync_type: str = None,
                 enable_sequencing: bool = False, fps: int = 0, retention_time: float = 60.0,
                 latency_threshold: float = 60.0, ignore_initial_delay: bool = False, unify: bool = False,
                 seek_to_end: bool = False):
        """
        Initializes an instance with the specified configuration parameters for managing and validating
        streaming or queue-like structures. Validation ensures appropriate values for parameters and
        integrity of the setup.

        Attributes:
            backlog_threshold (int): Threshold for backlog control.
            backlog_check_interval (float): Interval for checking backlog conditions.
            frame_sync_type (str): Synchronization type for frames. Must be one of {"timestamp", "number", None}.
            enable_sequencing (bool): Flag to enable sequencing.
            fps (int): Frames per second, used for performance adjustments.
            retention_time (float): Retention period for cached or processed data in seconds.
            latency_threshold (float): Maximum allowable latency in seconds.
            ignore_initial_delay (bool): If True, skips initial delay checks under certain conditions.
            unify (bool): Whether to unify input data streams or frames.
            seek_to_end (bool): If True, processes data starting from the most recent end of the stream.

        Args:
            backlog_threshold: Threshold defined for backlog control. Defaults to 0.
            backlog_check_interval: Interval for backlog checks. Can be 0. Defaults to 0.0.
            frame_sync_type: Synchronization type for frames. Should be one of {"timestamp", "number", None}.
                             Defaults to None.
            enable_sequencing: Boolean. If True, enables sequencing. Defaults to False.
            fps: Frames per second. Can be 0. Defaults to 0.
            retention_time: Retention period in seconds for cached data. Must be positive. Defaults to 60.0.
            latency_threshold: Maximum latency threshold in seconds for operations. Defaults to 60.0.
            ignore_initial_delay: Boolean flag to enable bypassing delays on initialization. Defaults to False.
            unify: Boolean flag for unification behavior. Defaults to False.
            seek_to_end: Boolean flag to start processing from stream's end point. Defaults to False.

        Raises:
            ValueError: If validation for any parameter fails.
        """

        def validate_positive(value, name, allow_zero=False):
            if value < 0 or (not allow_zero and value == 0):
                raise ValueError(f"'{name}' must be greater than {0 if allow_zero else 0}, got '{value}' instead.")

        validate_positive(fps, "fps", allow_zero=True)
        validate_positive(latency_threshold, "latency_threshold", allow_zero=True)
        validate_positive(retention_time, "retention_time")
        validate_positive(backlog_check_interval, "backlog_check_interval", allow_zero=True)
        validate_positive(backlog_threshold, "backlog_threshold", allow_zero=True)

        if ignore_initial_delay and backlog_threshold <= 0 and backlog_check_interval <= 0:
            raise ValueError(
                "If 'ignore_initial_delay' is True, either 'backlog_threshold' or 'backlog_check_interval' must be greater than 0."
            )

        valid_frame_sync_types = {"timestamp", "number", None}
        if frame_sync_type not in valid_frame_sync_types:
            raise ValueError(
                f"'frame_sync_type' must be either 'timestamp', 'number', or None, got '{frame_sync_type}' instead."
            )

        self.backlog_threshold = backlog_threshold
        self.backlog_check_interval = backlog_check_interval
        self.frame_sync_type = frame_sync_type
        self.fps = fps
        self.retention_time = retention_time
        self.latency_threshold = latency_threshold
        self.ignore_initial_delay = ignore_initial_delay
        self.enable_sequencing = enable_sequencing
        self.seek_to_end = seek_to_end
        self.unify = unify

    def __str__(self):
        return (
            f"FrameSyncConfig("
            f"backlog_threshold={self.backlog_threshold}, "
            f"backlog_check_interval={self.backlog_check_interval}, "
            f"frame_sync_type='{self.frame_sync_type}', "
            f"fps={self.fps}, "
            f"retention_time={self.retention_time}, "
            f"latency_threshold={self.latency_threshold}, "
            f"ignore_initial_delay={self.ignore_initial_delay}, "
            f"enable_sequencing={self.enable_sequencing})"
        )
