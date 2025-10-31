import logging

from framework.frame_event.pipeline_configuration import PipelineConfiguration
from framework.frame_synchronization.frame_sync_configuration import FRAME_SYNC, FrameSyncConfiguration
from framework.utils.config_utils import read_config, MODULE_CONFIG
from framework.utils.logging_utils import setup_logging
from analytics import AnalyticsService, AnalyticsConfiguration
from unification import UnificationService

logger=logging.getLogger("application")
if __name__ == "__main__":
    # Set up logging for the application environment
    setup_logging("dev")
    logger = logging.getLogger("application")
    try:
        arguments = read_config()
        pipeline = arguments.get('pipeline')

        pipeline_configuration = PipelineConfiguration(
            bootstrap_servers=arguments.get("bootstrap-servers", ["localhost: 9092"]),
            inbound_topics=[f"{UnificationService.MODULE_NAME}-{pipeline}-topic"],
            outbound_topics=None
        )

        frame_sync_configuration = None if FRAME_SYNC not in arguments else FrameSyncConfiguration(
            backlog_threshold=arguments.get(FRAME_SYNC).get("backlog-threshold", 10),
            backlog_check_interval=arguments.get(FRAME_SYNC).get("backlog-check-interval", 1),
            frame_sync_type=arguments.get(FRAME_SYNC).get("type", "timestamp"),
            enable_sequencing=arguments.get(FRAME_SYNC).get("enable-sequencing", True),
            retention_time=arguments.get(FRAME_SYNC).get("retention-time", 300),
            ignore_initial_delay=arguments.get(FRAME_SYNC).get("ignore-initial-delay", False), unify=False
        )

        analytics_configuration = AnalyticsConfiguration(
            output=arguments.get(MODULE_CONFIG).get("output", "./output"),
            api_key=arguments.get(MODULE_CONFIG).get("api-key", None),
            prompt=arguments.get(MODULE_CONFIG).get("prompt", "Describe the image."),
            log_wait_time=arguments.get(MODULE_CONFIG).get("log-wait-time", 0),
        )

        analytics_service = AnalyticsService(pipeline_configuration, frame_sync_configuration, analytics_configuration)
        analytics_service.process()

    except ValueError as e:
        logger.error("Invalid JSON input. Please provide a valid JSON-formatted string.")
    except KeyboardInterrupt:
        logger.error("Program interrupted by user. Cleaning up...")
    finally:
        # Perform any necessary cleanup here
        logger.info("Exiting program.")
