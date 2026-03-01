"""
Android 触摸录制回放框架

触摸操作录制和回放工具
"""

__version__ = "0.1.0"
__author__ = "Your Name"

from .core.event_types import (
    RawEvent,
    TouchDown,
    TouchEvent,
    TouchMove,
    TouchUp,
)
from .core.gesture_types import (
    Gesture,
    LongPress,
    Swipe,
    Tap,
)
from .core.device_info import (
    DeviceInfo,
    DeviceInfoCollector,
    InputDevice,
)
from .core.event_listener import (
    BufferedEventListener,
    EventListener,
    ListenerConfig,
)
from .core.event_parser import (
    EventParser,
    parse_event_lines,
)
from .core.gesture_recognizer import (
    GestureRecognizer,
    recognize_gestures,
)
from .recorder.base_recorder import BaseRecorder
from .recorder.batch_recorder import BatchRecorder, batch_record
from .generator.adb_generator import AdbGenerator
from .replayer.adb_replayer import AdbReplayer

__all__ = [
    # Version
    "__version__",
    # Core - Event Types
    "RawEvent",
    "TouchDown",
    "TouchEvent",
    "TouchMove",
    "TouchUp",
    # Core - Gesture Types
    "Gesture",
    "LongPress",
    "Swipe",
    "Tap",
    # Core - Device Info
    "DeviceInfo",
    "DeviceInfoCollector",
    "InputDevice",
    # Core - Event Listener
    "BufferedEventListener",
    "EventListener",
    "ListenerConfig",
    # Core - Event Parser
    "EventParser",
    "parse_event_lines",
    # Core - Gesture Recognizer
    "GestureRecognizer",
    "recognize_gestures",
    # Recorder
    "BaseRecorder",
    "BatchRecorder",
    "batch_record",
    # Generator
    "AdbGenerator",
    # Replayer
    "AdbReplayer",
]
