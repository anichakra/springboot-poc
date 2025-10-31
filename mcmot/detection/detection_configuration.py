
class DetectionConfiguration:
    """
    Represents a configuration for a detection system.

    This class is used to store and manage configuration parameters
    for a detection system, including the type of device, the model
    used, the detection classes being targeted, the confidence score
    threshold for predictions, and whether predictions are enabled.

    Attributes:
        device_type (str): The type of device for which the detection
            system will be operating.
        model (str): The name or identifier of the detection model.
        detection_classes (list): A list of classes or labels that
            the detection model will target.
        confidence_score (float): The minimum confidence score threshold
            to consider a detection valid.
        predict (bool): A boolean flag indicating whether to enable
            prediction functionality.
    """
    def __init__(self, device_type, model: str,
                 detection_classes: list, confidence_score: float,
                 predict: bool):
        self.device_type = device_type
        self.model = model
        self.detection_classes = detection_classes
        self.confidence_score = confidence_score
        self.predict = predict

    def __str__(self):
        return (f"DetectionConfiguration("
                f"device_type={self.device_type}, "
                f"model={self.model}, "
                f"detection_classes={self.detection_classes}, "
                f"confidence_score={self.confidence_score}, "
                f"predict={self.predict})")
