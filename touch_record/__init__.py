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
    Pinch,
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
    CallbackEventListener,
    EventListener,
    ListenerConfig,
)
from .core.event_parser import (
    EventParser,
    TouchEventStream,
)
from .core.gesture_recognizer import (
    BatchGestureRecognizer,
    GestureRecognizer,
    RealtimeGestureRecognizer,
    recognize_gestures,
)
from .recorder.base_recorder import BaseRecorder
from .recorder.realtime_recorder import RealtimeRecorder
from .recorder.batch_recorder import BatchRecorder
from .generator.base_generator import BaseGenerator
from .generator.adb_generator import AdbGenerator
from .generator.u2_generator import U2Generator
from .generator.hybrid_generator import HybridGenerator
from .replayer.base_replayer import BaseReplayer
from .replayer.adb_replayer import AdbReplayer
from .replayer.u2_replayer import U2Replayer

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
    "Pinch",
    "Swipe",
    "Tap",
    # Core - Device Info
    "DeviceInfo",
    "DeviceInfoCollector",
    "InputDevice",
    # Core - Event Listener
    "BufferedEventListener",
    "CallbackEventListener",
    "EventListener",
    "ListenerConfig",
    # Core - Event Parser
    "EventParser",
    "TouchEventStream",
    # Core - Gesture Recognizer
    "BatchGestureRecognizer",
    "GestureRecognizer",
    "RealtimeGestureRecognizer",
    "recognize_gestures",
    # Recorder
    "BaseRecorder",
    "RealtimeRecorder",
    "BatchRecorder",
    # Generator
    "BaseGenerator",
    "AdbGenerator",
    "U2Generator",
    "HybridGenerator",
    # Replayer
    "BaseReplayer",
    "AdbReplayer",
    "U2Replayer",
]
