
import logging

from framework.frame_synchronization.frame_cache import FrameCache

logger = logging.getLogger("application")

class TrackerCaptureCallback:
    """
    Handles callback operations for capturing and storing video frames in a cache.

    This class is responsible for receiving frame-related messages, extracting
    necessary metadata, and storing the data in a frame cache for further processing
    or retrieval. It ensures that frames are organized and stored based on their
    associated camera ID and timestamp.

    Attributes:
    captured_frames_cache: FrameCache
        The cache object used for storing and organizing captured frames.

    Methods:
    __init__(captured_frames_cache)
        Initializes the TrackerCaptureCallback with the given frame cache instance.
    callback(message)
        Handles the incoming frame messages and stores them in the appropriate cache.
    """
    def __init__(self, captured_frames_cache: FrameCache):
        """
        Represents an initializer for setting up the captured frames cache.

        This constructor initializes an instance of the class, setting up
        the required captured frames cache for managing frame data.

        Attributes:
        captured_frames_cache: FrameCache
            An instance of FrameCache used to store and manage captured frames.
        """
        self.captured_frames_cache = captured_frames_cache

    def callback(self, message):
        """
        Handles incoming messages and processes them to extract and store frame data.

        The method is responsible for extracting relevant information from the given
        message, such as the frame timestamp and camera metadata, and using this
        information to update internal caches.

        Parameters:
            message (dict): A dictionary containing the incoming message data. Expected
            keys include 'frame_timestamp' as part of the message structure.

        Raises:
            None

        Returns:
            None
        """
        #logger.debug("Messages in Tracker Capture: %s", message)
        frame_timestamp = message['frame_timestamp']  # Use frame timestamp as the key

        camera_id = message['camera_metadata']['camera_id']  # Retrieve the camera ID from the message
        # Store the captured message in the cache
        self.captured_frames_cache.add_camera(camera_id)
        self.captured_frames_cache.get_frame_cache(camera_id).add_frame(frame_timestamp, message)
