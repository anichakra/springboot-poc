class ReidConfiguration:
    """
    Represents a configuration for a Re-identification (ReID) system.

    This class is used to define and organize configuration parameters
    for a ReID model. It includes information about the model type,
    the path to the model's file, and the device on which the model
    will be executed.

    Attributes:
    model: str
        The name or identifier of the ReID model.
    model_path: str
        The file path to the saved ReID model.
    device: str
        The device type (e.g., "cpu", "cuda") where the model will run.
    """

    def __init__(self, model: str, model_path: str,
                 device: str):
        self.model = model
        self.model_path = model_path
        self.device = device

    def __str__(self):
        return (f"ReidConfiguration(model='{self.model}', "
                f"model_path='{self.model_path}', device='{self.device}', "
                )
