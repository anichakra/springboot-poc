import logging
import threading
import time
from typing import List, Dict, Any

logger = logging.getLogger("sync")

class FrameSequencingService:
    """
    FrameSequencingService

    A service class designed to handle the sequencing and grouping of frame metadata
    over a specified duration. The class facilitates the collection, grouping, and
    retrieval of frame data, ensuring they are processed in the correct chronological
    order. It supports concurrent operations using thread locking mechanisms to
    maintain data consistency.

    Attributes:
        duration (float): The time interval over which group_frames are collected
            before sorting.
        lock (threading.Lock): A threading lock to ensure thread-safe operations.
        temp_buffer (list): A temporary buffer to hold frames during sequencing.
        frames_buffer (list): A buffer to store frame metadata for synchronization.
        grouped_frames_buffer (list): A shared buffer for storing grouped frame data
            for sequencing and retrieval.
        last_sequence_time (float): Tracks the last time the sequencing process was
            executed.
    """
    def __init__(self, duration: float):
        """
        Class to handle grouping and sorting of frames over a specified duration.

        Attributes:
        duration (float): Time duration for collecting group_frames before sorting.
        lock (threading.Lock): Lock to synchronize access to shared resources.
        temp_buffer (list): Temporary buffer for storing unsorted frames.
        frames_buffer (list): Buffer for storing sorted frames.
        grouped_frames_buffer (list): Shared buffer to store all group_frames.
        last_sequence_time (float): Tracks the last time the `sequence` method was called.

        Methods:
        __init__(self, duration: float): Initializes the object with the specified duration and sets up
        necessary attributes for managing frame grouping and sorting.
        """
        self.duration = duration  # Collect group_frames for this duration before sorting

        self.lock = threading.Lock()
        self.temp_buffer = []
        self.frames_buffer = []
        self.grouped_frames_buffer = []  # Shared buffer to store all group_frames
        self.last_sequence_time = time.time()  # Tracks the last time `sequence` was called

    def collect(self, frame_metadata, camera_id, **kwargs):
        """
        Adds frame metadata to a synchronized buffer for future processing, associating it
        with the given camera ID and optional additional information. This method is thread-
        safe and ensures the metadata is stored alongside its timestamp and time of entry.

        Args:
            frame_metadata (dict): Metadata for the frame, including at minimum the
                `frame_timestamp`.
            camera_id (str): Identifier for the camera that captured the frame.
            **kwargs: Additional optional metadata to associate with the frame.

        Returns:
            None
        """
        with self.lock:
            current_time = time.time()
            frame_timestamp = frame_metadata["frame_timestamp"]

            # Add frame metadata to buffer for future synchronization
            self.frames_buffer.append({
                "frame_timestamp": frame_timestamp,
                "camera_id": camera_id,
                'entry_time': current_time,
                'additional_info': kwargs
            })
            logger.debug("frames:%s", len(self.frames_buffer))

    def collect_group(self, group_frame: List[Dict[str, Any]]):
        """
        Collects a group of data frames into a buffer for further processing. This
        method is thread-safe and ensures data is appended to the buffer in a
        controlled manner.

        Args:
            group_frame (List[Dict[str, Any]]): A list of dictionaries where each
            dictionary represents a data frame to be grouped and stored.

        """
        with self.lock:
            self.grouped_frames_buffer.append(group_frame)

    def sequence(self):
        """
        Sorts and processes frame data based on their timestamps. This function ensures
        thread-safety while reordering frame data in chronological order. It clears the
        `frames_buffer` after sorting and assigns the sorted list to a temporary buffer.

        Returns:
            None
        """
        with self.lock:
            self.temp_buffer = sorted(self.frames_buffer, key=lambda x: x["frame_timestamp"])
            logger.debug(f"temp buffer: %s", len(self.temp_buffer))
            self.frames_buffer.clear()

    def next(self):
        """
        Retrieves the next message from the temporary buffer, if available.

        The method ensures thread-safety by using a lock during the
        operation. It checks whether the temporary buffer is empty and
        returns None if there are no more groups left to retrieve. If
        groups are available, it removes and returns the first sorted
        group's message.

        Returns:
            str or None:  The message string of the first group in the
            sorted temporary buffer, or None if the temporary buffer is
            empty.
        """
        with self.lock:
            if not self.temp_buffer:
                return None  # No groups are left to retrieve
            return self.temp_buffer.pop(0)["additional_info"]["message"]  # Remove and return the first sorted group

    def sequence_groups(self):
        """
        Sequences groups from the grouped_frames_buffer based on the minimum frame_timestamp of each group if
        the configured duration between sequences has elapsed. The operation is thread-safe and ensures proper
        synchronization using a lock.

        Returns:
            None

        Raises:
            Not applicable
        """
        with self.lock:
            current_time = time.time()
            if current_time - self.last_sequence_time < self.duration:
                return  # Wait until the configured duration ends before sequencing

            with self.lock:
                # Sort by the minimum `frame_timestamp` in each group
                self.grouped_frames_buffer.sort(
                    key=lambda group: min(frame["frame_timestamp"] for frame in group)
                )
                logger.debug("grouped_frames_buffer %s:", self.grouped_frames_buffer)

            self.last_sequence_time = current_time  # Update the last sequence time

    def next_group(self) -> List[Dict[str, Any]]|None:
        """
        Retrieves and removes the next group of frames from the grouped frames buffer.

        This method is thread-safe, ensuring that operations on the grouped frames buffer
        are synchronized when accessed by multiple threads. If the buffer is empty, the
        method returns None, otherwise, it removes and returns the first sorted group from
        the buffer.

        Returns:
            List[Dict[str, Any]]|None: The next group of frames as a list of dictionaries,
            or None if the buffer is empty.
        """
        with self.lock:
            if not self.grouped_frames_buffer:
                return None  # No groups are left to retrieve
            return self.grouped_frames_buffer.pop(0)  # Remove and return the first sorted group