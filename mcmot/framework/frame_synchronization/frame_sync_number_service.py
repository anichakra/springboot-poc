import logging
import threading
import time

from framework.frame_synchronization.frame_sequencing_service import FrameSequencingService
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration

logger = logging.getLogger("sync")


class FrameSyncNumberService:
    """
    Handles frame synchronization from multiple cameras for concurrent processing.

    The FrameSyncNumberService class provides functionality to manage, analyze, and synchronize
    camera frames based on their frame numbers and timestamps. It ensures that frames from
    different cameras are aligned and grouped correctly for processing. Thread-safe operations
    are implemented using locking mechanisms to avoid concurrency issues.

    Attributes:
        lock: A thread lock used to ensure thread-safe operations when collecting and processing
            frames.
        initial_camera_data: A dictionary tracking initialization time and elapsed time
            for each camera.
        frames_buffer: A list serving as a temporary storage for unsynchronized frames.
        fps: An integer indicating the frames per second. Configured through the FrameSyncConfiguration.
        current_camera_data: A dictionary holding real-time metadata for frames of each camera.
        retention_time: A timeout in seconds for clearing old frames from the buffer.

    """

    def __init__(self, config: FrameSyncConfiguration):
        """
        Initialize a FrameSyncManager instance to manage and synchronize frames from multiple cameras.

        Args:
            config (FrameSyncConfiguration): Configuration object containing frame synchronization
                settings such as fps and retention time.
        """
        self.frame_seq = FrameSequencingService(config.backlog_check_interval)
        self.lock = threading.Lock()  # Initialize a threading lock for thread-safe operations
        self.initial_camera_data = {}  # Dictionary to track initialization data for each camera
        self.frames_buffer = []  # List to buffer unsynchronized frames
        self.fps = config.fps  # Set frames per second from configuration
        self.current_camera_data = {}  # Dictionary to store the current frame's metadata for each camera
        self.retention_time = config.retention_time  # Set the timeout for clearing old frames from configuration

    def collect(self, frame_number, frame_timestamp, fps, camera_id, **kwargs):
        """
        Collects frame data and updates internal data structures for managing camera frames.

        This method ensures thread-safe handling of frame data across multiple cameras. It initializes camera-specific tracking
        information when a new camera ID is encountered, computes metadata for each frame, and appends the frame data to an
        internal buffer for further synchronization and processing.

        Args:
            frame_number (int): The sequential number of the frame being collected.
            frame_timestamp (float): The timestamp associated with the current frame.
            fps (int): The frames per second rate of the capturing process.
            camera_id (str): The identifier for the camera producing the frame.
            **kwargs: Arbitrary additional metadata to associate with the frame.

        Note:
            - If fps is not yet initialized for the object, it gets set upon the first call to this method.
            - The method uses a thread lock to ensure safe concurrent modifications.
        """
        with self.lock:  # Acquire lock for thread-safe operations
            if self.fps == 0:  # Check if fps is not initialized
                self.fps = fps  # Initialize fps if it's not set

            # Check if camera ID is new and initialize its metadata
            if camera_id not in self.initial_camera_data:
                self.initial_camera_data[camera_id] = {
                    'start_time': frame_timestamp,  # Record the starting timestamp for the camera
                    'elapsed_time': 0,  # Initialize elapsed time
                }

            logger.debug("Collecting frame: camera_id=%s, frame_number=%s", camera_id, frame_number)

            # Prepare metadata for the frame
            camera_data = {
                "frame_number": frame_number,  # Current frame number
                "frame_timestamp": frame_timestamp,  # Timestamp for the frame
                "elapsed_time": frame_timestamp - self.initial_camera_data[camera_id]["start_time"],
                # Calculate elapsed time
                "additional_info": kwargs  # Additional metadata passed via kwargs
            }

            # Update the current metadata for the camera
            self.current_camera_data[camera_id] = camera_data

            # Append the frame data to the buffer for later synchronization
            self.frames_buffer.append({
                "frame_number": frame_number,  # Current frame number
                "frame_timestamp": frame_timestamp,  # Timestamp for the frame
                "camera_id": camera_id,  # Camera identifier
                "camera_data": camera_data,  # Frame metadata including additional info
                "grouped": False  # Initially mark as not grouped
            })

    def sampling(self, camera_id):
        """
        Determines whether to skip frames or wait based on the current and expected frame numbers for a specific camera.

        The method uses the elapsed time and frame rate of the camera to calculate the expected frame and compare it with
        the actual frame number. It calculates the required skip count or wait time based on the difference between these 
        two values.

        Arguments:
            camera_id (str): The unique identifier for the camera, which must exist in the current_camera_data dictionary.

        Raises:
            KeyError: If the provided camera_id is not found in the current_camera_data.

        Returns:
            tuple[float | int, bool]: A tuple containing:
                - The skip count (integer >= 0) if frames need to be skipped, or wait time (float > 0) if the process needs to
                  pause.
                - A boolean indicating whether to skip frames (True) or wait (False).
        """
        if camera_id not in self.current_camera_data:  # Check if the camera ID exists in metadata
            raise KeyError(f"Camera ID '{camera_id}' not found in the data.")  # Raise error if camera is not found

        camera_data = self.current_camera_data[camera_id]  # Retrieve camera metadata
        logger.debug("camera_id %s elapsed time %s", camera_id, camera_data['elapsed_time'])

        # Calculate the expected frame number using elapsed time and fps
        expected_frame = int(camera_data.get('elapsed_time') * self.fps)

        # Calculate the difference between the expected and actual frame numbers
        skip_count = expected_frame - camera_data.get('frame_number', 0)
        logger.debug("Camera ID: %s, Current/Expected Frame: %s/%s", camera_id, camera_data['frame_number'],
                     expected_frame)

        if skip_count < 0:  # If the current frame is ahead of the expected frame
            wait_time = abs(skip_count / self.fps)  # Calculate how long to wait
            logger.debug("Camera ID: %s, Wait-time: %s", camera_id, wait_time)
            return wait_time, False  # Indicate wait is required
        logger.debug("Camera ID: %s, skip_count: %s", camera_id, skip_count)
        return max(skip_count, 0), True  # Return skip frame count and indicate skipping is required

    def synchronize(self, callback):
        """
        Synchronizes frames from multiple cameras, groups them by their frame_number, processes 
        the grouped frames using the provided callback, and cleans up ungrouped frames in the buffer.

        Parameters
        ----------
        callback : object
            An object with a `callback` method to process the grouped frames.

        Raises
        ------
        TypeError
            If the callback object does not have a `callback` method, or it is not callable.

        Examples
        --------
        None
        """
        with self.lock:  # Ensure thread-safe access to data
            grouped_frames = []  # Initialize a list to store grouped frames

            # Extract unique frame numbers from the buffer
            frame_numbers = {frame["frame_number"] for frame in self.frames_buffer}

            # Process frames in ascending order of frame number
            for frame_number in sorted(frame_numbers):
                # Group frames with the same frame number
                group = [
                    frame for frame in self.frames_buffer
                    if frame["frame_number"] == frame_number
                ]

                # Check if all cameras have provided frames for the current frame number
                if len(group) == len(self.initial_camera_data):
                    grouped_frames.append(group)  # Add the group to the list of grouped frames
                    for g_frame in group:
                        g_frame["grouped"] = True  # Mark the frames as grouped
                    logger.debug(f"Grouped frames for cameras: {[f['camera_id'] for f in group]}")

            self.frame_seq.sequence()  # Start sequencing grouped frames
            msg = self.frame_seq.next_group()  # Retrieve the next grouped sequence
            while msg:
                callback.callback(msg)  # Process the grouped frames with the callback
                msg = self.frame_seq.next_group()  # Continue to the next group

            # Cleanup frames that are ungrouped or outside the retention time
            before_cleanup = len(self.frames_buffer)
            self.frames_buffer = [
                entry for entry in self.frames_buffer
                if not entry.get("grouped") and (time.time() - entry.get("entry_time")) <= self.retention_time
            ]
            after_cleanup = len(self.frames_buffer)
            logger.debug(
                f"Cleaned up frames buffer: {before_cleanup} -> {after_cleanup} entries with {self.retention_time}")
            