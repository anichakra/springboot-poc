
class ObservabilityConfiguration:
    """
    Configuration for observing and displaying detection parameters and metadata.

    This class facilitates customization of display options for detection overlays
    and metadata. It allows the user to define visual and display preferences
    such as text and bounding box attributes, as well as additional metadata
    like timestamps, frame numbers, frames-per-second (FPS), and camera ID.

    Attributes
    ----------
    detection_header_parameter : str
        A parameter name or identifier for detection observations.
    text_color : str
        Specifies the color of the text for display.
    text_thickness : int
        The thickness of the text strokes, in pixels.
    box_color : str
        Specifies the color for bounding box overlays.
    box_thickness : int
        The thickness of the bounding box lines, in pixels.
    show_timestamp : bool
        Indicates whether to overlay the timestamp on observations.
    show_frame_number : bool
        Indicates whether to overlay the frame number on observations.
    show_fps : bool
        Indicates whether to overlay the frames-per-second (FPS) on observations.
    show_camera_id : bool
        Indicates whether to overlay the camera ID on observations.
    """

    def __init__(self,
                 detection_header_parameter: str,
                 text_color: str,
                 text_thickness: int,
                 box_color: str,
                 box_thickness: int,
                 show_timestamp: bool = False,
                 show_frame_number: bool = False,
                 show_fps: bool = False,
                 show_camera_id: bool = False,
                 ):
        """
        Initializes an instance of the class.

        Parameters:
            detection_header_parameter: str
                A parameter to set for the detection header.
            text_color: str
                Color value to use for the text displayed.
            text_thickness: int
                Thickness value to use for the text displayed.
            box_color: str
                Color value to use for the bounding box displayed.
            box_thickness: int
                Thickness value to use for the bounding box displayed.
            show_timestamp: bool, optional
                Indicates whether to display the timestamp. Default is False.
            show_frame_number: bool, optional
                Indicates whether to display the frame number. Default is False.
            show_fps: bool, optional
                Indicates whether to display the frames per second (FPS). Default is False.
            show_camera_id: bool, optional
                Indicates whether to display the camera ID. Default is False.
        """
        self.detection_header_parameter = detection_header_parameter
        self.show_timestamp = show_timestamp
        self.show_frame_number = show_frame_number
        self.show_fps = show_fps
        self.show_camera_id = show_camera_id
        self.text_color = text_color
        self.text_thickness = text_thickness
        self.box_color = box_color
        self.box_thickness = box_thickness

    def __str__(self):
        return (f"ObservabilityConfiguration("
                f"detection_header_parameter={self.detection_header_parameter}, "
                f"color={self.text_color}, "
                f"thickness={self.text_thickness}, "
                f"color={self.box_color}, "
                f"thickness={self.box_thickness}, "
                f"show_timestamp={self.show_timestamp}, "
                f"show_frame_number={self.show_frame_number}, "
                f"show_fps={self.show_fps}, "
                f"show_camera_id={self.show_camera_id})")
