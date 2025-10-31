# framework/__init__.py
from framework.frame_event.message_consumer_kafka import MessageConsumer
from framework.frame_event.message_producer_kafka import MessageProducer

__all__ = ['MessageConsumer', 'MessageProducer']
__version__ = "1.0.0"

