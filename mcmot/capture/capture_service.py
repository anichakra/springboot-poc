# Import necessary packages
import logging

from capture import CaptureConfiguration, CaptureCallback
from framework import MessageProducer, MessageConsumer
from framework.frame_event.pipeline_configuration import PipelineConfiguration
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration

logger = logging.getLogger("application")

def handle_exception(exception: Exception, context_message: str = "An error occurred"):
    """
    Logs an exception with an error message and traceback for debugging purposes.

    Attributes:
    exception: Exception
        The exception that occurred and needs to be logged.
    context_message: str, optional
        Optional context message to provide additional details about where
        or why the exception occurred.

    Args:
    exception
        Represents the instance of the Exception to be logged. It is
        mandatory and takes any Python exception object.
    context_message
        A string providing a custom message to describe the context of the
        exception. Defaults to "An error occurred".

    Return:
    None
    """
    logger.error(f"{context_message}: {str(exception)}", exc_info=True)

class CaptureService:
    """
    Represents a service for capturing and processing video frames based on configurations
    and a message-driven architecture.

    This class is responsible for setting up the necessary dependencies, including message
    producers and consumers, to manage video capture and subsequent frame processing. It
    utilizes the provided configurations to initialize its components and operates within
    a specified pipeline for handling messages.

    Attributes:
        MODULE_NAME (str): The name of the module used for identification within the
            message pipeline.

    Methods:
        process: Starts the consumer instance for capturing and processing video frames.

    Parameters:
        pipeline_configuration (PipelineConfiguration): Configuration details for the
            message pipeline, including bootstrap servers and topic details.
        frame_sync_configuration (FrameSyncConfiguration): Configuration for syncing
            video frames during processing.
        capture_configuration (CaptureConfiguration): Configuration data related to
            video capture, including video path and camera metadata.
    """
    MODULE_NAME = "capture"

    def __init__(self, pipeline_configuration: PipelineConfiguration,
                 frame_sync_configuration: FrameSyncConfiguration, capture_configuration: CaptureConfiguration):

        self._consume_callback = CaptureCallback(
            producer=MessageProducer(pipeline_configuration.bootstrap_servers),
            outbound_topic=pipeline_configuration.outbound_topics[0],
            video_path=capture_configuration.video_path,
            camera_metadata=capture_configuration.camera_metadata,
            frame_sync_configuration=frame_sync_configuration)

        # Pass the ConsumeCallback instance to MessageConsumer
        self.consumer = MessageConsumer(
            bootstrap_servers=pipeline_configuration.bootstrap_servers,
            topic=pipeline_configuration.inbound_topics[0],
            group_id=f"{self.MODULE_NAME}-{capture_configuration.camera_metadata.get("camera_id")}",
            callback=self._consume_callback
        )

    def process(self):
        """
        Starts the detection process for a consumer instance. The method initializes
        the consumer, handles signals for interruption, and ensures the consumer
        is stopped gracefully when interrupted.

        :raises KeyboardInterrupt: If the process is manually interrupted by the user.
        """
        logger.debug("Capture process started...")
        try:
            self.consumer.start()
        except KeyboardInterrupt:
            logger.info("Interrupted! Exiting gracefully...")
            self.consumer.stop()
