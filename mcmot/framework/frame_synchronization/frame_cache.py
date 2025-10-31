from collections import OrderedDict


class FrameCache:
    """
    A cache for storing frames with timestamp-based management.

    The FrameCache class provides methods to store and retrieve frames efficiently
    based on their timestamps. It ensures that the number of stored frames does not
    exceed a specified maximum size, with older entries being evicted to make room
    for new ones. It also supports operations to retrieve and remove frames within
    specified timestamp ranges, making it suitable for time-series data management.

    Attributes:
        cache (OrderedDict): Stores frame data with timestamps as keys.
        max_size (int): The maximum size of the cache. Older entries are evicted when the size exceeds this limit.
    """

    def __init__(self, max_size=1000):
        """
        Represents a basic cache with a fixed maximum size to store key-value pairs.
        Provides functionality to store and retrieve items in a predictable order.

        Attributes:
            max_size (int): Indicates the maximum number of items the cache can hold. Defaults to 1000.

        Args:
            max_size (int, optional): Specifies the maximum number of items the cache is
                permitted to hold. If not provided, defaults to 1000.
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.cache = {}

    def add_camera(self, camera_id):
        """
        Adds a camera identifier to the cache if it does not already exist. This method ensures that
        each camera ID is uniquely handled within the cache. If the camera ID is new, it initializes
        a corresponding FrameCache instance for it. If the camera ID already exists, no action is
        taken for that ID.

        Args:
            camera_id: The identifier of the camera being added to the cache.

        Returns:
            bool: True if a new entry was created for the camera_id, False otherwise.
        """
        if camera_id not in self.cache:
            self.cache[camera_id] = FrameCache()
            return True  # Indicates a new entry was created
        return False  # Indicates that the camera_id already existed

    def get_frame_cache(self, camera_id):
        """
        Retrieve the cached frame for a specific camera.

        This method retrieves the frame data for the given camera
        ID from the cache. Frames are stored in the cache with
        camera IDs as their keys and can be accessed using this
        method.

        Args:
            camera_id (str): The unique identifier of the camera.

        Returns:
            Any: The cached frame associated with the provided
            camera ID, or None if the camera ID does not exist
            in the cache.
        """
        return self.cache.get(camera_id)

    def add_frame(self, frame_timestamp, frame_data):
        """
        Adds a frame to the cache, maintaining its size under the specified limit
        and ensuring the most recently added or updated frames have priority within
        the cache. Older frames are evicted to make space for newer ones if the
        cache exceeds its defined maximum size.

        Parameters:
        frame_timestamp : Any
            The unique identifier or timestamp of the frame to be cached.
        frame_data : Any
            The data associated with the frame to be stored in the cache.
        """
        if frame_timestamp in self.cache:
            # If frame already exists, remove it to update its position
            self.cache.pop(frame_timestamp)
        self.cache[frame_timestamp] = frame_data

        # If cache size exceeds max_size, evict the oldest frame
        if self.max_size and len(self.cache) > self.max_size:
            self.cache.popitem()

    def get_and_remove_frames_before(self, frame_timestamp):
        """
        Retrieve and remove frames stored in cache with timestamps earlier than the provided
        timestamp value, maintaining only more recent frames in the cache.

        Parameters
        ----------
        frame_timestamp : Any
            The timestamp indicating the threshold. Frames with timestamps earlier than this
            value will be removed and returned.

        Returns
        -------
        list
            A list of frames that were stored in the cache with timestamps earlier than the
            provided frame_timestamp.
        """
        frames_to_return = []
        keys_to_remove = []

        # Iterate through the cache and find frames with earlier timestamps
        for ts, frame in self.cache.items():
            if ts < frame_timestamp:
                frames_to_return.append(frame)
                keys_to_remove.append(ts)
            else:
                break  # Remaining frames are guaranteed to be after timestamp

        # Remove old frames from the cache
        for ts in keys_to_remove:
            self.cache.pop(ts)

        return frames_to_return

    def get_and_remove_frames_between(self, from_timestamp, to_timestamp):
        """
        Extracts and removes frames within a specified timestamp range.

        Filters and removes all frames that fall within the specified range
        defined by the `from_timestamp` and `to_timestamp` parameters.
        Frames are first retrieved by removing all frames before the
        `to_timestamp`. Then, frames with a timestamp greater than
        `from_timestamp` are kept, effectively narrowing down the range.

        Parameters:
            from_timestamp: float
                The lower bound for the frame timestamps. Frames with
                timestamps greater than this value will be retained.
            to_timestamp: float
                The upper bound for the frame timestamps. Frames with
                timestamps earlier than this value will be initially
                retrieved and filtered.

        Returns:
            list
                A list of frames that have timestamps within the specified
                range.
        """
        # Step 1: Retrieve all frames before the upper bound (to_timestamp)
        frames = self.get_and_remove_frames_before(to_timestamp)

        # Step 2: Filter frames to include only those with timestamps >= from_timestamp
        filtered_frames = [frame for frame in frames if frame['frame_timestamp'] > from_timestamp]

        return filtered_frames
