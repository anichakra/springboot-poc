import logging

from framework.frame_synchronization.frame_sync_configuration import FrameSyncConfiguration
from framework.frame_synchronization.frame_sync_number_service import FrameSyncNumberService
from framework.frame_synchronization.frame_sync_timestamp_service import FrameSyncTimestampService

logger = logging.getLogger("sync")

class FrameSyncService:
    """
    Manages frame synchronization through configurable service layers.

    The FrameSyncService class is designed to handle synchronization of frames based on
    either timestamps or frame numbers. It is initialized with a synchronization configuration
    and dynamically selects the appropriate service to handle synchronization. The class provides
    methods to collect frame data, perform synchronization, and manage camera-specific operations.
    It simplifies synchronization logic and integrates a user-defined callback for custom processing.

    Attributes:
        sync_type: Specifies the type of synchronization ('timestamp' or 'number').
        service: Instance of the underlying service handling the synchronization process.
    """

    def __init__(self, config:FrameSyncConfiguration):
        """
        Initializes a FrameSync instance determining the synchronization service
        based on the provided configuration.

        Parameters
        ----------
        config : FrameSyncConfiguration
            The configuration object containing synchronization settings,
            including the sync type.

        Raises
        ------
        ValueError
            If the sync type in the configuration is not 'number' or 'timestamp'.
        """
        self.sync_type = config.frame_sync_type.lower()

        if self.sync_type == "timestamp":
            self.service = FrameSyncTimestampService(config)
        elif self.sync_type == "number":
            self.service = FrameSyncNumberService(config)
        else:
            raise ValueError(f"Invalid sync_type '{self.sync_type}'. Expected 'number' or 'timestamp'.")

        logger.info(f"Initialized FrameSync with type '{self.sync_type}'.")

    def collect(self, frame_number, frame_timestamp, fps, camera_id, **kwargs):

        """
        Collects data for a specific camera frame.

        This method is used to collect and process data corresponding
        to a specific frame from a camera. It includes information
        such as the frame number, timestamp, frames per second (fps),
        camera identifier, and additional parameters.

        Parameters:
        frame_number : int
            The number assigned to the specific camera frame.
        frame_timestamp : float
            The timestamp of the frame in seconds since the epoch.
        fps : float
            The frames per second rate at which the camera operates.
        camera_id : str
            The identifier for the camera that provided the frame.
        **kwargs : dict
            Additional optional parameters required for custom configurations
            or processing related to the frame.

        Returns:
        None
        """
        self.service.collect(frame_number, frame_timestamp, fps, camera_id, **kwargs)

    def synchronize(self, callback):
        """
        Performs synchronization of a service with a provided callback function.

        The function invokes the synchronization process of a specified service
        object by passing the callback function as an argument. The callback is
        triggered during or after the synchronization process, depending on the
        implementation details of the invoked method. This allows external handling
        or monitoring of synchronization phases.

        Parameters:
            callback: Callable
                A function provided by the caller to be used during or after the
                synchronization process. It must adhere to the signature expected
                by the service's `synchronize` method.

        Raises:
            This function does not explicitly raise errors itself. Refer to the
            `self.service.synchronize` method for potential exceptions and their
            handling.
        """
        self.service.synchronize(callback)

    def sampling(self, camera_id):
        """
        Provides functionality to skip or enforce a wait based on a given camera ID by delegating
        the operation to the associated service.

        Arguments:
            camera_id (str): The identifier for the camera whose skip or wait action is
                to be processed.

        Returns:
            Any: The result returned from the service's skip or wait operation.

        """
        return self.service.sampling(camera_id)
