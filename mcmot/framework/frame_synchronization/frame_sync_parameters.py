def _validate_positive_int(value, field_name):
    """
    Validates that the given value is a positive integer. If the value is invalid,
    raises a ValueError with a descriptive message.

    Args:
        value (int): The value to be validated as a positive integer.
        field_name (str): The name of the field corresponding to the value, used
        in the error message.

    Returns:
        int: The validated positive integer.

    Raises:
        ValueError: If the value is not an integer or is not greater than zero.
    """
    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"'{field_name}' must be a positive integer. Given: {value}")
    return value


def _validate_enum(value, valid_values, field_name):
    """
    Validates if a given value is present within a predefined list of valid values.

    This function checks if the input value is contained in the list of valid
    values provided. If the value is not valid, it raises a ValueError with
    a detailed error message specifying the expected values and the provided
    invalid value. Useful for ensuring compliance with constraints and
    consistency across input data.

    Parameters:
        value: Any
            The value to be validated.
        valid_values: Iterable
            A list, tuple, or other iterable containing the set of acceptable
            values.
        field_name: str
            The name of the field being validated, used for error message clarity.

    Raises:
        ValueError: Raised if the given value is not present in the valid_values
        iterable.

    Returns:
        Any: Returns the validated value if it is within the valid_values iterable.
    """
    if value not in valid_values:
        raise ValueError(f"'{field_name}' must be one of {valid_values}. Given: {value}")
    return value


class FrameSyncParameters:
    """
    Represents the configuration parameters for frame synchronization.

    This class encapsulates the configuration settings used to manage frame
    synchronization processes. It includes parameters for buffer management,
    retry policies, ordering rules, and performance tuning. These settings allow
    the user to define and customize how frames are synchronized within a system,
    ensuring that the process meets specific requirements in terms of latency,
    ordering, and scalability.

    Attributes:
    sync_window_ms (int): The size of the synchronization window in milliseconds.
    max_buffer_size (int): The maximum number of frames that can be stored in the buffer.
    buffer_timeout (int): The maximum timeout period for buffered frames in milliseconds.
    retry_attempts (int): The number of retry attempts for failed synchronizations.
    retry_backoff_ms (int): The backoff duration in milliseconds between retry attempts.
    ordering_key (str): A key used to order frames within the buffer.
    latency_threshold_ms (int): The acceptable latency threshold in milliseconds for frame synchronization.
    parallel_threads (int): The number of threads to use for frame processing.
    discard_policy (str): The policy to follow when the buffer overflows. Possible values are "discard_oldest", "discard_newest", or "allow_partial".
    checkpoint_interval_ms (int): The interval in milliseconds for saving the state to the state store.
    state_store_path (str): The file path used for storing synchronization state.
    """

    def __init__(
            self,
            sync_window_ms: int = 100,
            max_buffer_size: int = 500,
            buffer_timeout: int = 60000,
            retry_attempts: int = 5,
            retry_backoff_ms: int = 1000,
            ordering_key: str = "timestamp",
            latency_threshold_ms: int = 5000,
            parallel_threads: int = 4,
            discard_policy: str = "discard_oldest",
            checkpoint_interval_ms: int = 10000,
            state_store_path: str = "/tmp/frame_synchronizer_state",
    ):
        """
        Class representing a configuration for frame synchronization. Configurable options
        determine how frames are buffered, ordered, synchronized, and stored, including
        their respective timeouts, retry mechanisms, and thread management for parallel
        operations. Validation is applied to ensure input values meet required conditions.

        Attributes:
            sync_window_ms: int
                The maximum time window, in milliseconds, to allow for synchronized frame
                alignment.
            max_buffer_size: int
                The maximum size of the buffer for holding frames before processing.
            buffer_timeout: int
                The maximum time, in milliseconds, that a frame can remain in the buffer.
            retry_attempts: int
                The maximum number of retry attempts for processing or synchronization.
            retry_backoff_ms: int
                The time, in milliseconds, between consecutive retry attempts.
            ordering_key: str
                The key by which frames will be ordered, typically based on a timestamp.
            latency_threshold_ms: int
                The threshold, in milliseconds, indicating tolerated latency for processing
                or synchronization.
            parallel_threads: int
                The number of threads to use for parallel frame synchronization tasks.
            discard_policy: str
                The policy to apply when the buffer reaches its maximum size. Options are:
                "discard_oldest", "discard_newest", or "allow_partial".
            checkpoint_interval_ms: int
                The time, in milliseconds, at which the synchronization state will be
                periodically checkpointed.
            state_store_path: str
                The path to the directory used for storing the state data.
        """
        self.sync_window_ms = _validate_positive_int(sync_window_ms, "sync_window_ms")
        self.max_buffer_size = _validate_positive_int(max_buffer_size, "max_buffer_size")
        self.buffer_timeout = _validate_positive_int(buffer_timeout, "buffer_timeout")
        self.retry_attempts = _validate_positive_int(retry_attempts, "retry_attempts")
        self.retry_backoff_ms = _validate_positive_int(retry_backoff_ms, "retry_backoff_ms")
        self.ordering_key = ordering_key if isinstance(ordering_key, str) else ValueError(
            "'ordering_key' must be a string."
        )
        self.latency_threshold_ms = _validate_positive_int(latency_threshold_ms, "latency_threshold_ms")
        self.parallel_threads = _validate_positive_int(parallel_threads, "parallel_threads")
        self.discard_policy = _validate_enum(
            discard_policy, ["discard_oldest", "discard_newest", "allow_partial"], "discard_policy"
        )
        self.checkpoint_interval_ms = _validate_positive_int(checkpoint_interval_ms, "checkpoint_interval_ms")
        self.state_store_path = state_store_path if isinstance(state_store_path, str) else ValueError(
            "'state_store_path' must be a string."
        )

    def __str__(self):
        """Returns a string representation of the configuration."""
        return (
            f"FrameSyncConfig("
            f"sync_window_ms={self.sync_window_ms}, "
            f"max_buffer_size={self.max_buffer_size}, "
            f"buffer_timeout={self.buffer_timeout}, "
            f"retry_attempts={self.retry_attempts}, "
            f"retry_backoff_ms={self.retry_backoff_ms}, "
            f"ordering_key={self.ordering_key}, "
            f"latency_threshold_ms={self.latency_threshold_ms}, "
            f"parallel_threads={self.parallel_threads}, "
            f"discard_policy={self.discard_policy}, "
            f"checkpoint_interval_ms={self.checkpoint_interval_ms}, "
            f"state_store_path={self.state_store_path})"
        )
