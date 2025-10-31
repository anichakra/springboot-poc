
class CaptureConfiguration:
    """
    Represents the configuration for a capture operation.

    This class is used to store metadata related to a camera capture operation
    and the path where the captured video is saved. It also allows specifying
    the number of loops for which the operation is performed. It provides
    a string representation for easier debugging or logging purposes.
    """
    def __init__(self, camera_metadata: dict, video_path: str):
        self.camera_metadata = camera_metadata
        self.video_path = video_path

    def __str__(self):
        attributes = {
            "camera_metadata": self.camera_metadata,
            "video_path": self.video_path
        }
        return f"CaptureConfiguration({', '.join(f'{key}={value!r}' for key, value in attributes.items())})"
