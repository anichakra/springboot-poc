
class UnificationConfiguration:
    """Represents the configuration required for unification, allowing specification
    of parameters like output location, API key, and a default prompt.

    This class is designed to encapsulate configuration details for a unification
    operation, including the output target, optional authentication API key, and
    a customizable prompt.

    Attributes:
    output: str
        The output location or designation for the operation result.
    api_key: str, optional
        The API key used for authentication, defaulting to None if not provided.
    prompt: str
        The default prompt used during the operation, with a default value of
        "Describe the image.".
    """
    def __init__(self,output: str,
                 api_key: str = None,
                 prompt: str = "Describe the image."):
        """
            Initializes the class instance to handle operations related to image description.

            Attributes:
            ----------
            output : str
                The output file or path where the result will be stored or managed.
            api_key : str, optional
                The authentication key used to access the relevant API for processing.
                Defaults to None if not provided.
            prompt : str
                The textual description or instruction for image analysis. Defaults to
                "Describe the image."

            Parameters:
            ----------
            output : str
                Specifies where the processed data or output will be saved or used.
            api_key : str, optional
                Input parameter used for API-level access if any authentication is required.
                Defaults to None when not specified.
            prompt : str, optional
                Indicates the default guiding instruction or query for the image description
                operation. Defaults to "Describe the image."
        """
        self.output = output
        self.api_key = api_key
        self.prompt = prompt

    def __str__(self):
        return (f"TrackerConfiguration("
                f"output='{self.output}', "
                f"api_key='{self.api_key}', "
                f"prompt='{self.prompt}')")
