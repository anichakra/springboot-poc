import logging

from detection import DetectionService
from framework.frame_event.pipeline_configuration import PipelineConfiguration
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration, FRAME_SYNC
from framework.utils.config_utils import read_config, MODULE_CONFIG
from framework.utils.logging_utils import setup_logging
from reid import ReidConfiguration
from reid import ReidService

if __name__ == "__main__":
    # Set up logging for the application environment
    setup_logging("dev")
    logger = logging.getLogger("application")
    try:
        config = read_config()
        pipeline = config.get('pipeline')
        pipeline_configuration = PipelineConfiguration(
            bootstrap_servers=config.get("bootstrap-servers", ["localhost: 9092"]),
            inbound_topics=[f"{DetectionService.MODULE_NAME}-{pipeline}-topic"],
            outbound_topics=[f"{ReidService.MODULE_NAME}-{pipeline}-topic"]
        )

        frame_sync_configuration = None if FRAME_SYNC not in config else FrameSyncConfiguration(
            backlog_threshold=config.get(FRAME_SYNC).get("backlog-threshold", 10),
            backlog_check_interval=config.get(FRAME_SYNC).get("backlog-check-interval", 1),
            frame_sync_type=config.get(FRAME_SYNC).get("type", "timestamp"), enable_sequencing=False,
            retention_time=config.get(FRAME_SYNC).get("retention-time", 300),
            seek_to_end=config.get(FRAME_SYNC).get("seek-to-end", False),
            ignore_initial_delay=config.get(FRAME_SYNC).get("ignore-initial-delay", False))

        reid_configuration = ReidConfiguration(
            model_path=config.get(MODULE_CONFIG).get("model", "model/osnet_x1_0.pth"),
            model=config.get(MODULE_CONFIG).get("model", "model/osnet_x1_0.pth").split("/")[-1].split(".")[0],
            device=config.get(MODULE_CONFIG).get("device-type", "cpu")
        )

        reid_service = ReidService(pipeline_configuration, frame_sync_configuration, reid_configuration )
        reid_service.process()

    except ValueError as e:
        logging.error("Invalid JSON input. Please provide a valid JSON-formatted string.")
    except KeyboardInterrupt:
        logging.error("Program interrupted by user. Cleaning up...")
    finally:
        # Perform any necessary cleanup here
        logging.info("Exiting program.")
