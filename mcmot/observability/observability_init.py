import logging

from framework.frame_event.pipeline_configuration import PipelineConfiguration
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration, FRAME_SYNC
from framework.utils.config_utils import read_config, MODULE_CONFIG
from framework.utils.logging_utils import setup_logging
from observability import ObservabilityService, ObservabilityConfiguration

if __name__ == "__main__":
    # Set up logging for the application environment

    setup_logging("dev")
    logger = logging.getLogger("application")
    try:
        arguments = read_config()
        pipeline = arguments.get('pipeline')

        MODULE_NAME = arguments.get(MODULE_CONFIG).get("module")
        INBOUND_TOPIC = f"{MODULE_NAME}-{pipeline}-topic"

        pipeline_configuration = PipelineConfiguration(
            bootstrap_servers=arguments.get("bootstrap-servers", ["localhost: 9092"]),
            inbound_topics=[f"{MODULE_NAME}-{pipeline}-topic"],
            outbound_topics=None
        )

        frame_sync_configuration = None if FRAME_SYNC not in arguments else FrameSyncConfiguration(
            backlog_threshold=arguments.get(FRAME_SYNC).get("backlog-threshold", 10),
            backlog_check_interval=arguments.get(FRAME_SYNC).get("backlog-check-interval", 1),
            frame_sync_type=arguments.get(FRAME_SYNC).get("type", "timestamp"),
            enable_sequencing=False,
            retention_time=arguments.get(FRAME_SYNC).get("retention-time", 300),
            ignore_initial_delay=arguments.get(FRAME_SYNC).get("ignore-initial-delay", False))

        stream_configuration = ObservabilityConfiguration(
            detection_header_parameter=arguments.get(MODULE_CONFIG).get("label"),
            show_timestamp=arguments.get(MODULE_CONFIG).get("show-timestamp", True),
            show_frame_number=arguments.get(MODULE_CONFIG).get("show-frame_number", True),
            show_fps=arguments.get(MODULE_CONFIG).get("show-fps", True),
            show_camera_id=arguments.get(MODULE_CONFIG).get("show-camera-id", True),
            text_color=arguments.get(MODULE_CONFIG).get("text-color", None),
            text_thickness=arguments.get(MODULE_CONFIG).get("text-thickness", 1),
            box_color=arguments.get(MODULE_CONFIG).get("box-color", None),
            box_thickness=arguments.get(MODULE_CONFIG).get("box-thickness", 1),
        )
        logger.debug("StreamConfiguration: %s", stream_configuration)

        stream_service = ObservabilityService(pipeline_configuration, frame_sync_configuration, stream_configuration)
        stream_service.process()

    except KeyboardInterrupt:
        logger.debug("Program interrupted by user. Cleaning up...")
    finally:
        # Perform any necessary cleanup here
        logger.debug("Exiting program.")
