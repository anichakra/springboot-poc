import logging
import threading
import time

from framework.frame_synchronization.frame_sequencing_service import FrameSequencingService
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration

logger = logging.getLogger("sync")


class FrameSyncTimestampService:
    """
    Manages timestamp synchronization for frames from multiple cameras in real-time.

    This class is responsible for collecting frame metadata, evaluating delays between
    frames from different cameras, and grouping frames based on their timestamps. It
    supports mechanisms to skip or wait processing based on frame delay, synchronize
    frames with a given callback, and ensures accurate sequencing of grouped frames in
    a buffer.

    Attributes:
        lock (threading.Lock): A lock object to ensure thread-safe operations.
        initial_camera_data (dict): Holds initial metadata for each camera including delay 
            and start time.
        current_camera_data (dict): Keeps track of the most recent metadata for each camera.
        frames_buffer (list): A buffer storing metadata of all collected frames for processing.
        fps (int): Frame rate, initialized from the configuration or determined dynamically.
        retention_time (float): Maximum time in seconds a frame is retained in the buffer.
        latency_threshold (float): Max allowed threshold for delays during synchronization.
        tolerance (float): Calculated value for acceptable timestamp variation between frames.
        frame_seq (FrameSequencingService): Service to handle frame grouping and sequencing
            based on the configuration.
    """

    def __init__(self, config: FrameSyncConfiguration):
        """
        Class responsible for handling frame synchronization. This class initializes and manages 
        data structures for storing frame data and handles parameters related to frame rates, 
        retention times, and tolerances specified by the configuration. It creates a frame 
        sequencing service to manage the sequence of frames based on the given interval.

        Args:
            config (FrameSyncConfiguration): The configuration object containing various 
            synchronization parameters.
        """
        self.lock = threading.Lock()
        self.initial_camera_data, self.current_camera_data, self.frames_buffer = {}, {}, []
        self.fps, self.retention_time, self.latency_threshold = config.fps, config.retention_time, config.latency_threshold
        self.tolerance = 0
        # Create an instance of FrameSequencingService using the backlog interval from the config
        self.frame_seq = FrameSequencingService(config.backlog_check_interval)

    def collect(self, frame_number, frame_timestamp, fps, camera_id, **kwargs):
        """
        Collects frame metadata, ensures synchronization initialization, and computes timing-related details 
        for a given camera frame. Metadata is stored in the frames buffer for further processing.
        
        Args:
            frame_number (int): The number identifying the frame being processed.
            frame_timestamp (float): The timestamp of the frame to be used for delay calculations.
            fps (int): The frames per second rate of the camera feed.
            camera_id (Any): The unique identifier for the camera.
            **kwargs: Additional metadata or configuration details related to the frame or camera.
        """
        if self.fps == 0:  # If the frame rate is not initialized
            self.fps = fps
            logger.debug(f"FPS initialized to {self.fps} and tolerance set to {self.tolerance}")
        if self.tolerance == 0:  # If the tolerance is not initialized
            self.tolerance = 1 / self.fps  # Calculate tolerance as the inverse of FPS

        with self.lock:  # Ensure thread-safe operations
            current_time = time.time()  # Capture the current time

            # Initialize data for a new camera that hasn't been encountered before
            if camera_id not in self.initial_camera_data:
                # Calculate initial delay based on latency threshold
                initial_delay = min(self.latency_threshold,
                                    current_time - frame_timestamp) if self.latency_threshold else current_time - frame_timestamp

                # Store initial latency and start time for the camera
                self.initial_camera_data[camera_id] = {'initial_delay': initial_delay, 'start_time': current_time}
                logger.debug(f"Initialized camera data for camera_id {camera_id} with delay {initial_delay}")

            # Retrieve initial delay and update current metadata for the frame
            initial_delay = self.initial_camera_data[camera_id]["initial_delay"]
            self.current_camera_data[camera_id] = {
                'frame_number': frame_number,
                'frame_timestamp': frame_timestamp,
                'elapsed_time': current_time - self.initial_camera_data[camera_id]['start_time'],
                'delay': current_time - frame_timestamp - initial_delay,
                'additional_info': kwargs  # Store any additional metadata provided
            }

            # Store the frame metadata in the buffer for later synchronization
            self.frames_buffer.append({
                "frame_timestamp": frame_timestamp,
                "frame_number": frame_number,
                "camera_id": camera_id,
                "camera_data": self.current_camera_data[camera_id],
                'entry_time': current_time,  # Record when the frame was added to the buffer
            })
            logger.debug(f"Frame metadata added to buffer for camera_id {camera_id}")

    def sampling(self, camera_id):
        """
        Determine if the process for a camera ID should be skipped or delayed.

        This function calculates a delay value using the current camera data referencing
        the provided camera ID. Based on the computed delay, it determines whether to skip
        an operation or wait, returning the necessary timing adjustments and a boolean
        indicating the action to take.

        Parameters:
            camera_id (str): The unique identifier of the camera for which the action determination is made.

        Returns:
            tuple[int, bool]:
                - The absolute delay value or calculated frame delay.
                - A boolean indicating whether to wait (True) or skip (False).

        Raises:
            KeyError: If the provided camera ID is not found within the initial camera data.
        """
        # Ensure the provided camera ID is valid
        if camera_id not in self.initial_camera_data:
            logger.debug(f"Camera ID '{camera_id}' not found.")
            raise KeyError(f"Camera ID '{camera_id}' not found in the data.")

        # Calculate the delay for the given camera
        delay = self.current_camera_data[camera_id]['delay']
        action = "wait" if delay >= 0 else "skip"  # Choose action based on delay value
        logger.debug(f"Camera ID {camera_id}: Calculated delay={delay}, action={action}")
        return (abs(delay), False) if delay < 0 else (max(int(delay * self.fps), 0), True)

    def synchronize(self, callback):
        """
        Synchronize frames from the buffer by grouping them based on timestamp tolerance and ensuring no duplicate
        cameras within each group.

        Args:
            callback (Callable): A callback interface instance responsible for handling the grouped frames processed 
            in sequence.
        """
        with self.lock:  # Ensure thread-safe operations

            # Iterate over the frames buffer to group frames by timestamp tolerance
            for item in self.frames_buffer:
                if item.get("grouped"):  # Skip frames already grouped
                    continue

                group = [item]  # Start a new group with the current frame
                for frame in self.frames_buffer:
                    if frame.get("grouped"):  # Skip already grouped frames
                        continue

                    # Check if the frame timestamp is within tolerance of the group
                    if abs(frame["frame_timestamp"] - item["frame_timestamp"]) <= self.tolerance:
                        # Avoid adding frames from the same camera to the group
                        if not any(f["camera_id"] == frame["camera_id"] for f in group):
                            group.append(frame)

                            # If the group contains frames from all cameras, stop grouping
                            if len(group) == len(self.initial_camera_data):
                                self.frame_seq.collect_group(group)  # Collect the group for sequencing
                                for g_frame in group:
                                    g_frame["grouped"] = item["frame_timestamp"]  # Mark frames as grouped
                                break

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
