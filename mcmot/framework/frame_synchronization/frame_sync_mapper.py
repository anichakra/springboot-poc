from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration
from framework.frame_synchronization.frame_sync_parameters import FrameSyncParameters


class FrameSyncMapper:
    """
    Maps frame synchronization parameters to a configuration object.

    This class provides a static method to convert an instance of `FrameSyncParameters`
    into a `FrameSyncConfig` object. The method transforms the input values appropriately
    based on various conditions, allowing for configuration of frame synchronization
    based on the specified parameters.

    The primary purpose of this class is to facilitate the generation of a configuration
    object that defines various aspects of frame synchronization, such as buffer size,
    retention time, latency thresholds, and synchronization type. It is designed to handle
    optional and mandatory properties while ensuring proper validation and default values.

    """

    @staticmethod
    def map(parameters):
        """
            Maps the provided frame synchronization parameters to a configuration object.

            This method validates the input parameters and derives the necessary configuration
            values required for frame synchronization. Derived values include synchronization
            window interval, maximum buffer size, backlog check interval, frame sync type,
            latency threshold, and retention time for frames in the buffer. The resulting
            configuration encapsulates these derived values and is returned as a FrameSyncConfiguration instance.

            Args:
                parameters (FrameSyncParameters): A required parameter object containing various
                attributes needed for configuration such as sync interval (milliseconds),
                buffer size, checkpoint interval, ordering key type, discard policy, latency
                threshold, and buffer timeout.

            Returns:
                FrameSyncConfiguration: A configuration object embedding the finalized synchronization
                settings suitable for managing frame processing.

            Raises:
                ValueError: If the given parameter is not an instance of FrameSyncParameters.
        """
        if not isinstance(parameters, FrameSyncParameters):
            raise ValueError("'parameters' must be an instance of FrameSyncParameters.")

        # sync_window_ms is not mandatory. If not set then fps will be retrieved from frame. 
        # It is only mandatory if from frame fps cannot be retrieved.
        fps = 0
        if parameters.sync_window_ms and parameters.sync_window_ms > 0:
            fps = round(1 / parameters.sync_window_ms)

        # max_buffer_size is not mandatory. It is only mandatory when checkpoint_interval_ms is set or set to more than 0.
        backlog_threshold = 0
        if parameters.max_buffer_size:
            backlog_threshold = parameters.max_buffer_size

        # Time interval of frame synchronization. If not set or set to 0 then backlog_check will never be done. Hence skip to end will not be done.
        backlog_check_interval = 0
        if parameters.checkpoint_interval_ms:
            backlog_check_interval = parameters.checkpoint_interval_ms / 1000

        # if not set then frame sync will not be done, it will be ignored.
        frame_sync_type = None
        if parameters.ordering_key and parameters.ordering_key in ["timestamp", "number"]:
            frame_sync_type = parameters.ordering_key

        # We have to set backlog_check_interval more than 0 to make ignore_initial_delay as true
        ignore_initial_delay = parameters.discard_policy == "discard_oldest" and backlog_check_interval > 0

        # This is the initial latency threshold. If there is a delay in getting the frames to the module how much at least it can wait.
        # Normally we must keep it to less than 10 seconds to minimize the delay or gap.
        latency_threshold = 10
        if parameters.latency_threshold_ms:
            latency_threshold = parameters.latency_threshold_ms / 1000

        # Default value is set to 1 minutes to keep the frames in the buffer.
        retention_time = 60
        if parameters.buffer_timeout:
            retention_time = parameters.buffer_timeout / 1000

        # Create and return the FrameSyncConfig object
        return FrameSyncConfiguration(backlog_threshold=backlog_threshold, backlog_check_interval=backlog_check_interval,
                               frame_sync_type=frame_sync_type, enable_sequencing=True, fps=fps,
                               retention_time=retention_time, latency_threshold=latency_threshold,
                               ignore_initial_delay=ignore_initial_delay)
