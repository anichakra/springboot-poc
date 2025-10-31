import logging

from capture import CaptureService
from detection import DetectionService
from framework.frame_event.pipeline_configuration import PipelineConfiguration
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration, FRAME_SYNC
from framework.utils.config_utils import read_config, MODULE_CONFIG
from framework.utils.logging_utils import setup_logging
from tracker import TrackerConfiguration
from tracker import TrackerService

if __name__ == "__main__":
    # Set up logging for the application environment
    setup_logging("dev")
    logger = logging.getLogger("application")
    try:
        config = read_config()
        pipeline = config.get('pipeline')
        detection_module = config.get(MODULE_CONFIG).get('detection-module-name', DetectionService.MODULE_NAME)

        pipeline_configuration = PipelineConfiguration(
            bootstrap_servers=config.get("bootstrap-servers", ["localhost: 9092"]),
            inbound_topics=[f"{CaptureService.MODULE_NAME}-{pipeline}-topic", f"{detection_module}-{pipeline}-topic"],
            outbound_topics=[f"{TrackerService.MODULE_NAME}-{pipeline}-topic"]
        )

        frame_sync_configuration = None if FRAME_SYNC not in config else FrameSyncConfiguration(
            backlog_threshold=config.get(FRAME_SYNC).get("backlog-threshold", 10),
            backlog_check_interval=config.get(FRAME_SYNC).get("backlog-check-interval", 1),
            frame_sync_type=config.get(FRAME_SYNC).get("type", "timestamp"),  # Type of frame synchronization
            ignore_initial_delay=config.get(FRAME_SYNC).get("ignore-initial-delay", False),
            retention_time=config.get(FRAME_SYNC).get("retention-time", 300),
            seek_to_end=config.get(FRAME_SYNC).get("seek-to-end", False),
            enable_sequencing=config.get(FRAME_SYNC).get("enable-sequencing", True),
        )

        tracker_configuration = TrackerConfiguration(
            max_iou_distance=config.get(MODULE_CONFIG).get("max-iou-distance", 0.7),
            max_age=config.get(MODULE_CONFIG).get("max-age", 100),
            nms_max_overlap=config.get(MODULE_CONFIG).get("nms-max-overlap", 1.0),
            detection_score_threshold=config.get(MODULE_CONFIG).get("detection-score-threshold", 0.7),
            match_detection=config.get(MODULE_CONFIG).get("match-detection", False),
            gating_only_position=config.get(MODULE_CONFIG).get("gating-only-position", False),
            ignore_capture=config.get(MODULE_CONFIG).get("ignore-capture", False),
            prediction_factor=config.get(MODULE_CONFIG).get("prediction-factor", 0),
            only_confirmed_tracks=config.get(MODULE_CONFIG).get("only-confirmed-tracks", False),
            camera_id=config.get(MODULE_CONFIG).get("camera_id"),
        )
        tracker_service = TrackerService(pipeline_configuration, frame_sync_configuration, tracker_configuration )
        tracker_service.process()

    except ValueError as e:
        logger.error("Invalid JSON input. Please provide a valid JSON-formatted string.")
    except KeyboardInterrupt:
        logger.error("Program interrupted by user. Cleaning up...")
    finally:
        # Perform any necessary cleanup here
        logger.info("Exiting program.")
