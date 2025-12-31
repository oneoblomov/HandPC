"""
Gesture Control Sistemi
Ana modul paketleri
"""

__version__ = "2.1.0"
__author__ = "Gesture Control Team"
__description__ = "El hareketleri ile bilgisayar kontrolu"

from .core.gesture_detector import GestureDetector
from .core.action_handler import ActionHandler

__all__ = ['GestureDetector', 'ActionHandler']
