class AnalyticsConfiguration:
    """
    Represents configuration settings for analytics.

    This class is used to specify the configuration details required for
    analytics-related operations. It includes attributes for output location,
    log wait time duration, API key, and a prompt message. Instances of this
    class allow storing and accessing these configuration details.
    """
    def __init__(self, output: str, log_wait_time: int,
                 api_key: str = None,
                 prompt: str = "Describe the image."):
        self.output = output
        self.api_key = api_key
        self.prompt = prompt
        self.log_wait_time = log_wait_time

    def __str__(self):
        return (f"AnalyticsConfiguration("
                f"output='{self.output}', "
                f"log_wait_time='{self.log_wait_time}', "
                f"api_key='{self.api_key}', "
                f"prompt='{self.prompt}')")
