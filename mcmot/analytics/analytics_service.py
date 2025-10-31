from analytics import AnalyticsConfiguration
from analytics.analytics_callback import AnalyticsCallback
from framework import MessageConsumer
from framework.frame_event.pipeline_configuration import PipelineConfiguration
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration

class AnalyticsService:
    """
    Handles analytics service operations.

    The AnalyticsService class is designed to initialize a message consumer for
    processing analytics data based on provided configurations. It leverages
    specific configurations to define its behavior and manages the lifecycle of
    message consumption. The primary goal of this class is to facilitate seamless
    data processing through callback mechanisms and ensure clean shutdown of
    operations.

    Attributes
    ----------
    MODULE_NAME : str
        Static attribute representing the name of the analytics module.
    consumer : MessageConsumer
        Instance of MessageConsumer responsible for consuming incoming messages.

    Methods
    -------
    __init__(pipeline_configuration: PipelineConfiguration,
             frame_sync_configuration: FrameSyncConfiguration,
             analytics_configuration: AnalyticsConfiguration)
        Initializes the AnalyticsService instance using the provided configurations.
    process()
        Starts the message consumption operation and handles graceful shutdown.
    """
    MODULE_NAME = "analytics"

    def __init__(self, pipeline_configuration: PipelineConfiguration, frame_sync_configuration: FrameSyncConfiguration,
                 analytics_configuration: AnalyticsConfiguration):
        """
        Initialize the class with configurations for pipeline, frame synchronization, and analytics.

        Parameters:
        pipeline_configuration (PipelineConfiguration): The configuration object for the data pipeline.
        frame_sync_configuration (FrameSyncConfiguration): The configuration object for frame synchronization.
        analytics_configuration (AnalyticsConfiguration): The configuration object for analytics.

        Attributes:
        _consume_callback (AnalyticsCallback): Instance of AnalyticsCallback initialized with the analytics configuration.
        consumer (MessageConsumer): Instance of MessageConsumer initialized with pipeline configuration, frame synchronization
            configuration, and the consume callback.
        """
        # Create a ConsumeCallback instance
        self._consume_callback = AnalyticsCallback(output_path=analytics_configuration.output,
                                                   log_wait_time=analytics_configuration.log_wait_time,
                                                   api_key=analytics_configuration.api_key,
                                                   prompt=analytics_configuration.prompt)

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
