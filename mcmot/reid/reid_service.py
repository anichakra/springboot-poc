import logging

from framework import MessageProducer, MessageConsumer
from framework.frame_event.pipeline_configuration import PipelineConfiguration

from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration
from reid import ReidConfiguration
from reid.reid_callback import ReidCallback

logger = logging.getLogger("application")


class ReidService:
    """
    Facilitates the setup and management of a Re-identification (ReID) service.

    This class provides the structure for initializing and managing components
    required for performing ReID operations. It configures the necessary
    producers and consumers for message handling, initializes callbacks for
    processing, and integrates them with a message broker. The service is
    equipped to handle inbound and outbound message streams and manage the
    lifecycle of these components.

    :ivar MODULE_NAME: The name of the module that groups related operations.
    :type MODULE_NAME: str
        ReID service, such as topics, model paths, and bootstrap server
        details.
    :type reid_configuration: ReidConfiguration

    :ivar _consume_callback: Callback object responsible for handling message
        consumption and processing logic for ReID.
    :type _consume_callback: ReidCallback
    :ivar consumer: Object responsible for consuming messages from an inbound
        topic in the message broker.
    :type consumer: MessageConsumer
    """
    MODULE_NAME = "reid"

    def __init__(self, pipeline_configuration: PipelineConfiguration,
                 frame_sync_configuration: FrameSyncConfiguration, reid_configuration: ReidConfiguration):

        # Create a ConsumeCallback instance
        self._consume_callback = ReidCallback(
            producer=MessageProducer(pipeline_configuration.bootstrap_servers),
            outbound_topic=pipeline_configuration.outbound_topics[0], model=reid_configuration.model,
            model_path=reid_configuration.model_path, device=reid_configuration.device
        )
        # Pass the ConsumeCallback instance to MessageConsumer
        self.consumer = MessageConsumer(
            bootstrap_servers=pipeline_configuration.bootstrap_servers,
            topic=pipeline_configuration.inbound_topics[0],
            group_id=self.MODULE_NAME,
            callback=self._consume_callback,
            frame_sync_config=frame_sync_configuration,
        )
        logger.debug("Reid Setup Completed")

    def process(self):
        # Initialize a MessageConsumer object using the topic_key_dict
        try:
            logger.debug("Reid consumer started")
            self.consumer.start()
        except KeyboardInterrupt:
            logger.info("Interrupted! Exiting gracefully...")
            self.consumer.consumer.close()
