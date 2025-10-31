class PipelineConfiguration:
    """
    Represents the configuration for a pipeline, including Kafka server details and topic information.

    The PipelineConfiguration class is designed to encapsulate the configuration details necessary
    for a pipeline that interacts with Kafka topics. It includes the Kafka bootstrap servers,
    inbound topics, and outbound topics that the pipeline is configured to consume from or
    produce to. This class ensures that at least one of inbound or outbound topics is specified
    during initialization.

    Attributes:
    bootstrap_servers (list[str]): List of Kafka server addresses used as bootstrap servers.
    inbound_topics (list[str] | None): List of topics from which the pipeline consumes messages.
        If set to None, no consumption occurs.
    outbound_topics (list[str] | None): List of topics to which the pipeline produces messages.
        If set to None, no production occurs.

    Raises:
    ValueError: If neither inbound_topics nor outbound_topics is provided or both are empty.
    """
    def __init__(self, bootstrap_servers: list[str], inbound_topics: list[str] | None,
                 outbound_topics: list[str] | None):
        """
        Initializes the instance with Kafka bootstrap servers and optional inbound or
        outbound topics. Ensures that at least one of inbound or outbound topics is
        provided and not empty.

        Attributes:
            bootstrap_servers (list[str]): List of Kafka bootstrap servers.
            inbound_topics (list[str] | None): List of inbound Kafka topics to subscribe
                to, or None if not applicable.
            outbound_topics (list[str] | None): List of outbound Kafka topics to publish
                to, or None if not applicable.

        Raises:
            ValueError: If both 'inbound_topics' and 'outbound_topics' are not provided
                or are empty.
        """
        if not (inbound_topics or outbound_topics):
            raise ValueError("At least one of 'inbound_topics' or 'outbound_topics' must be provided and not empty.")
        self.bootstrap_servers = bootstrap_servers
        self.inbound_topics = inbound_topics
        self.outbound_topics = outbound_topics

    def __repr__(self):
        return (f"PipelineConfiguration(bootstrap_servers={self.bootstrap_servers}, "
                f"inbound_topics={self.inbound_topics}, "
                f"outbound_topics={self.outbound_topics})")

    def __str__(self):
        return (f"PipelineConfiguration with bootstrap_servers={self.bootstrap_servers}, "
                f"inbound_topics={self.inbound_topics}, "
                f"outbound_topics={self.outbound_topics}")
