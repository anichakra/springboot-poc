# detection/__init__.py

from .detection_configuration import DetectionConfiguration
from .detection_service import DetectionService
from .detection_callback import DetectionCallback

__all__ = ['DetectionConfiguration', 'DetectionService', 'DetectionCallback']
__version__ = "1.0.0"
