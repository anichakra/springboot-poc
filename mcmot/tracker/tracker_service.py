import logging
from concurrent.futures import ThreadPoolExecutor

from framework import MessageConsumer
from framework import MessageProducer
from framework.frame_event.pipeline_configuration import PipelineConfiguration
from framework.frame_synchronization.frame_cache import FrameCache

from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration
from tracker import TrackerConfiguration
from tracker.tracker_capture_callback import TrackerCaptureCallback
from tracker.tracker_detection_callback import TrackerDetectionCallback

logger = logging.getLogger("application")

class TrackerService:
    """
    Handles tracking operations using message consumption, detection callbacks, and synchronization.

    This class initializes components required for tracking, consuming messages from Kafka topics, and processing
    frames and detections. It integrates capture and detection callbacks, and utilizes a thread pool executor to manage
    message processing workflows. The TrackerService is configured with pipeline, frame synchronization, and tracker
    parameters, effectively linking components for streamlined tracking tasks.

    Attributes:
        MODULE_NAME (str): Name of the module unique to the tracker service.
        tracker_configuration (TrackerConfiguration): Configuration settings specifying the tracker behavior and
                                                      thresholds used during tracking.

    Methods:
        __init__(pipeline_configuration, frame_sync_configuration, tracker_configuration):
            Initializes the TrackerService with configurations and sets up necessary components.

        process():
            Starts the tracking process by consuming messages and synchronizing data based on configurations.
    """
    MODULE_NAME = "tracker"

    def __init__(self, pipeline_configuration: PipelineConfiguration,
                 frame_sync_configuration: FrameSyncConfiguration,
                 tracker_configuration: TrackerConfiguration):
        """
        Initializes the core components and configurations of a tracking module, including message
        consumers and detection callback handlers. The initialization procedure enables the system
        to handle frame captures, perform detection tracking, synchronize frames, and communicate
        with the configured pipeline.

        Attributes:
            tracker_configuration: Configuration for the tracker, including parameters
                such as IOU distance, age constraints, and detection thresholds.

        """
        self.tracker_configuration = tracker_configuration
        captured_frames = FrameCache()

        self.callback = TrackerDetectionCallback(
            producer=MessageProducer(bootstrap_servers=pipeline_configuration.bootstrap_servers),
            outbound_topic=pipeline_configuration.outbound_topics[0], captured_frames_cache=captured_frames,
            max_iou_distance=tracker_configuration.max_iou_distance, max_age=tracker_configuration.max_age,
            nms_max_overlap=tracker_configuration.nms_max_overlap,
            detection_score_threshold=tracker_configuration.detection_score_threshold,
            match_detection=tracker_configuration.match_detection,
            gating_only_position=tracker_configuration.gating_only_position,
            prediction_factor=tracker_configuration.prediction_factor,
            only_confirmed_tracks=tracker_configuration.only_confirmed_tracks,
        )


        _consume_detection_callback = self.callback

        _consume_capture_callback = TrackerCaptureCallback(captured_frames_cache=captured_frames)

        self.consumer_capture = MessageConsumer(
            bootstrap_servers=pipeline_configuration.bootstrap_servers,
            topic=pipeline_configuration.inbound_topics[0],
            group_id=self.MODULE_NAME,
            callback=_consume_capture_callback,
            frame_sync_config=frame_sync_configuration,
            key=tracker_configuration.camera_id
        )

        self.consumer_detection = MessageConsumer(
            bootstrap_servers=pipeline_configuration.bootstrap_servers,
            topic=pipeline_configuration.inbound_topics[1],
            group_id=self.MODULE_NAME,
            callback=_consume_detection_callback,
            frame_sync_config=frame_sync_configuration,
            key=tracker_configuration.camera_id
        )

    def process(self):
        """
        Processes the tracking operation based on the given configuration and handles
        the execution of consumer capture and detection tasks in a thread pool. Ensures
        graceful exit when interrupted.

        Raises:
            KeyboardInterrupt: Raised when the process is interrupted, ensuring proper
            cleanup of resources.
        """
        logger.debug("Tracking process started...")
        try:
            if self.tracker_configuration.ignore_capture:
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future_detection = executor.submit(self.consumer_detection.start)
                    future_detection.result()
            else:
                with ThreadPoolExecutor(max_workers=2) as executor:
                    future_capture = executor.submit(self.consumer_capture.start)
                    future_detection = executor.submit(self.consumer_detection.start)
                    future_capture.result()
                    future_detection.result()
            logger.debug("Tracking Started...")
        except KeyboardInterrupt:
            print("Interrupted! Exiting gracefully...")
            self.consumer_capture.consumer.close()
            self.consumer_detection.consumer.close()
