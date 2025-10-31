from capture import CaptureService
from detection import DetectionConfiguration
from detection import DetectionService
from framework.frame_event.pipeline_configuration import PipelineConfiguration
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration, FRAME_SYNC
from framework.utils.config_utils import read_config, MODULE_CONFIG
from framework.utils.logging_utils import setup_logging
import logging

if __name__ == "__main__":
    # Set up logging for the application environment
    setup_logging("dev")
    logger = logging.getLogger("application")
    try:
        config = read_config()
        pipeline = config.get('pipeline')
        pipeline_configuration = PipelineConfiguration(
            bootstrap_servers=config.get("bootstrap-servers", ["localhost: 9092"]),
            inbound_topics=[f"{CaptureService.MODULE_NAME}-{pipeline}-topic"],
            outbound_topics=[f"{DetectionService.MODULE_NAME}-{pipeline}-topic"]
        )

        frame_sync_configuration = None if FRAME_SYNC not in config else FrameSyncConfiguration(
            backlog_threshold=config.get(FRAME_SYNC).get("backlog-threshold", 10),
            backlog_check_interval=config.get(FRAME_SYNC).get("backlog-check-interval", 1),
            frame_sync_type=config.get(FRAME_SYNC).get("type", "timestamp"), enable_sequencing=False,
            retention_time=config.get(FRAME_SYNC).get("retention-time", 300),
            ignore_initial_delay=config.get(FRAME_SYNC).get("ignore-initial-delay", False))

        # Create an instance of DetectionConfiguration using the parsed JSON values
        detection_configuration = DetectionConfiguration(

            device_type=config.get(MODULE_CONFIG).get("device-type"),  # Type of device being used
            model=config.get(MODULE_CONFIG).get("model", "model/yolov8n.pt"),  # Detection model identifier
            detection_classes=config.get(MODULE_CONFIG).get("classes", []),  # Detection classes
            confidence_score=0.3,  # Minimum confidence score threshold
            predict=config.get(MODULE_CONFIG).get("predict", False),  # Flag to indicate whether predictions are enabled

        )

        # Initialize the DetectionService with application ID and configuration
        detection_service = DetectionService(pipeline_configuration, frame_sync_configuration, detection_configuration)

        # Start processing using the detection service
        detection_service.process()

    except ValueError as e:
        # Log an error if the JSON input is invalid
        logger.error("Invalid JSON input. Please provide a valid JSON-formatted string.")
    except KeyboardInterrupt:
        # Log a message and clean up if the program is interrupted manually
        logger.error("Program interrupted by user. Cleaning up...")
    finally:
        # Final cleanup and exit logging
        logger.info("Exiting program.")
