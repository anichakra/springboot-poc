from detection import DetectionConfiguration
from detection.detection_callback import DetectionCallback
from framework import MessageConsumer, MessageProducer
import logging

from framework.frame_event.pipeline_configuration import PipelineConfiguration
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration

logger = logging.getLogger("application")

class DetectionService:
    """
    Facilitates the detection process in a message-based pipeline.

    This class is responsible for managing the setup and operation of a detection
    pipeline. It includes consumer initialization, integration with detection-specific
    configuration, and proper handling of interruptions for graceful shutdown. The
    class uses configured instances of `DetectionCallback` and `MessageConsumer`
    to process incoming messages and perform detection tasks.
    """
    MODULE_NAME = "detection"

    def __init__(self,pipeline_configuration: PipelineConfiguration,
                 frame_sync_configuration: FrameSyncConfiguration, detection_configuration: DetectionConfiguration):

        self._consume_callback = DetectionCallback(
            producer=MessageProducer(pipeline_configuration.bootstrap_servers),
            outbound_topic=pipeline_configuration.outbound_topics[0],
            device_type =detection_configuration.device_type,
            model=detection_configuration.model,
            confidence_score=detection_configuration.confidence_score,
            predict=detection_configuration.predict, detection_class=detection_configuration.detection_classes)

        # Pass the ConsumeCallback instance to MessageConsumer
        self.consumer = MessageConsumer(
            bootstrap_servers=pipeline_configuration.bootstrap_servers,
            topic=pipeline_configuration.inbound_topics[0],
            group_id=self.MODULE_NAME,
            callback=self._consume_callback,
            frame_sync_config=frame_sync_configuration,
        )

    def process(self):
        """
        Starts the detection process for a consumer instance. The method initializes
        the consumer, handles signals for interruption, and ensures the consumer
        is stopped gracefully when interrupted.

        :raises KeyboardInterrupt: If the process is manually interrupted by the user.
        """
        logger.debug("Detection process started...")
        try:
            self.consumer.start()
        except KeyboardInterrupt:
            logger.info("Interrupted! Exiting gracefully...")
            self.consumer.stop()

