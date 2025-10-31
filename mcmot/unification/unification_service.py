from framework import MessageConsumer, MessageProducer
from framework.frame_event.pipeline_configuration import PipelineConfiguration
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration
from unification import UnificationConfiguration
from unification.unification_callback import UnificationCallback

class UnificationService:
    """
    Class responsible for managing and coordinating the unification process.

    This class serves as a service layer that manages the initialization and
    configuration of the unification process, including handling inbound and
    outbound messaging, synchronization, and callbacks. It integrates various
    components such as message producers, consumers, and callback handlers
    to ensure the proper functioning of the unification pipeline.

    Attributes:
        MODULE_NAME (str): Name of the module used for identifying the group.
        unification_configuration (UnificationConfiguration): Configuration
            for the unification pipeline.
        _consume_callback (UnificationCallback): Callback instance that
            processes incoming messages and produces outbound results.
        consumer (MessageConsumer): Consumer instance that manages message
            consumption, synchronization, and processing.

    Methods:
        process():
            Starts the unification process by initiating the consumer's
            message handling. Handles graceful shutdown during interruptions.
    """
    MODULE_NAME = "unification"

    def __init__(self, pipeline_configuration: PipelineConfiguration,
                 frame_sync_configuration: FrameSyncConfiguration, unification_configuration: UnificationConfiguration):
        self.unification_configuration = unification_configuration

        # Create a ConsumeCallback instance
        self._consume_callback = UnificationCallback(producer=MessageProducer(pipeline_configuration.bootstrap_servers),
                                                     output_path=unification_configuration.output,
                                                     outbound_topic=pipeline_configuration.outbound_topics[0])

        # Pass the ConsumeCallback instance to MessageConsumer
        self.consumer = MessageConsumer(
            bootstrap_servers=pipeline_configuration.bootstrap_servers,
            topic=pipeline_configuration.inbound_topics[0],
            group_id=self.MODULE_NAME,
            callback=self._consume_callback,
            frame_sync_config=frame_sync_configuration,
        )

    def process(self):
        try:
            self.consumer.start()
        except KeyboardInterrupt:
            print("Interrupted! Exiting gracefully...")
            self.consumer.consumer.close()
            self.consumer.consumer.close()
            self._consume_callback.close_video_writer()
