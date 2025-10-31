import logging

from framework import MessageConsumer
from framework.frame_event.pipeline_configuration import PipelineConfiguration
from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration
from observability import ObservabilityConfiguration
from observability.observability_callback import ObservabilityCallback

logger = logging.getLogger("application")

class ObservabilityService:
    """
    ObservabilityService handles the ingestion and processing of message streams to provide
    real-time observability data such as detection parameters, timestamps, frame rates, and
    other context-specific information. It integrates with the MessageConsumer to manage
    incoming data streams and leverages the ObservabilityCallback for processing the messages.

    This class is designed to be instantiated with configuration objects specifying the pipeline,
    stream, and frame synchronization details. Using these configurations, it sets up the necessary
    callbacks and consumers to handle data streams efficiently. The main functionality is encapsulated
    in the process method, which initiates the message consumption and provides a mechanism for
    graceful termination.

    Attributes:
        MODULE_NAME (str): A static identifier used for group operations related
            to the class across the system.

    Parameters:
        pipeline_configuration (PipelineConfiguration): Configuration related to the pipeline,
            including inbound topics and connection details.
        frame_sync_configuration (FrameSyncConfiguration): Configuration for frame synchronization,
            specifying frame processing logic or synchronization constraints.
        stream_configuration (ObservabilityConfiguration): Configuration for observability parameters,
            including data display settings like timestamps, FPS, colors, and thickness for visual attributes.

    Raises:
        No errors raised directly by this class.
    """
    MODULE_NAME = "observability"

    def __init__(self, pipeline_configuration: PipelineConfiguration, frame_sync_configuration: FrameSyncConfiguration,
                 stream_configuration: ObservabilityConfiguration):
        """
        Initializes an instance of the class with provided pipeline, frame synchronization, and
        stream configuration settings. Creates and configures the message consumer and the
        observability callback handler.

        Args:
            pipeline_configuration (PipelineConfiguration): Configuration object containing
                pipeline settings, such as bootstrap servers and inbound topics.
            frame_sync_configuration (FrameSyncConfiguration): Configuration object specifying
                frame synchronization settings for managing frame ingesting and processing.
            stream_configuration (ObservabilityConfiguration): Configuration object containing
                stream display settings, such as text color, box thickness, and other observability
                options.
        """
        self._consume_callback = ObservabilityCallback(

            module_name=pipeline_configuration.inbound_topics[0].removesuffix("_topic"),
            detection_header_parameter=stream_configuration.detection_header_parameter,
            show_timestamp=stream_configuration.show_timestamp,
            show_frame_number=stream_configuration.show_frame_number, show_fps=stream_configuration.show_fps,
            show_camera_id=stream_configuration.show_camera_id,
            text_color=stream_configuration.text_color,
            text_thickness=stream_configuration.text_thickness,
            box_color=stream_configuration.box_color,
            box_thickness=stream_configuration.box_thickness
        )
        # Pass the ConsumeCallback instance to MessageConsumer
        self.consumer = MessageConsumer(
            bootstrap_servers=pipeline_configuration.bootstrap_servers,
            topic=pipeline_configuration.inbound_topics[0],
            group_id=self.MODULE_NAME,
            callback=self._consume_callback,
            frame_sync_config=frame_sync_configuration
        )

    def process(self):
        # Initialize a MessageConsumer object using the topic_key_dict
        try:
            self.consumer.start()
        except KeyboardInterrupt:
            print("Interrupted! Exiting gracefully...")
            self.consumer.consumer.close()
