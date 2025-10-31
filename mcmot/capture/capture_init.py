import logging
from capture import CaptureConfiguration
from capture import CaptureService
from framework.frame_event.pipeline_configuration import PipelineConfiguration
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration, FRAME_SYNC
from framework.utils.config_utils import read_config, MODULE_CONFIG
from framework.utils.logging_utils import setup_logging

if __name__ == "__main__":
    # Set up logging for the application environment
    setup_logging("dev")
    logger = logging.getLogger("application")
    try:
        config = read_config()
        pipeline = config.get('pipeline')

        location = config.get(MODULE_CONFIG).get('location')
        camera_id=config.get(MODULE_CONFIG).get("camera-id")
        frame_sync = config.get(FRAME_SYNC, False)
        video_format = config.get(MODULE_CONFIG).get("format", "avi")

        pipeline_configuration = PipelineConfiguration(
            bootstrap_servers=config.get("bootstrap-servers", ["localhost: 9092"]),
            inbound_topics=[f"camera-{pipeline}-topic"],
            outbound_topics=[f"{CaptureService.MODULE_NAME}-{pipeline}-topic"]
        )

        frame_sync_configuration = None if FRAME_SYNC not in config else FrameSyncConfiguration(
            backlog_threshold=config.get(FRAME_SYNC).get("backlog-threshold", 10),
            backlog_check_interval=config.get(FRAME_SYNC).get("backlog-check-interval", 1),
            frame_sync_type=config.get(FRAME_SYNC).get("type", "number"), enable_sequencing=False,
            retention_time=config.get(FRAME_SYNC).get("retention-time", 300),
            ignore_initial_delay=config.get(FRAME_SYNC).get("ignore-initial-delay", False)
        )

        # Create a CaptureConfiguration instance based on the parsed JSON input
        capture_configuration = CaptureConfiguration(
            camera_metadata={
                "camera_id": camera_id,
                "camera_name": location,
                "compression": config.get(MODULE_CONFIG).get("compression", "H.265"),
                "bitrate": config.get(MODULE_CONFIG).get("bitrate", "6Mbps"),
                "encoding": config.get(MODULE_CONFIG).get("encoding", "HEVC"),
                "format": video_format
            },
            video_path=f"capture/video/{location}/{location}-{camera_id}.{video_format}",
        )

        # Create an instance of CaptureService using the CaptureConfiguration
        capture_service = CaptureService(pipeline_configuration, frame_sync_configuration, capture_configuration)

        # Start the capture processing operation
        capture_service.process()

    except ValueError as e:
        # Handle invalid JSON input errors
        logging.error("Invalid JSON input. Please provide a valid JSON-formatted string.")
    except KeyboardInterrupt:
        # Handle program interruptions (e.g., Ctrl+C)
        logging.error("Program interrupted by user. Cleaning up...")
    finally:
        # Perform any necessary cleanup actions before exiting
        logging.info("Exiting program.")
