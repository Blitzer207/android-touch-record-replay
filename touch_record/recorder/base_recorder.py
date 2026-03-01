"""
基础录制器接口

定义录制器的抽象基类，统一录制行为。
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..core.event_listener import BufferedEventListener, ListenerConfig
from ..core.event_parser import EventParser
from ..core.gesture_recognizer import GestureRecognizer
from ..core.gesture_types import Gesture


class BaseRecorder(ABC):
    """
    录制器抽象基类

    定义录制器的通用接口和功能。
    """

    def __init__(
        self,
        listener_config: Optional[ListenerConfig] = None,
        parser: Optional[EventParser] = None,
    ):
        self.listener_config = listener_config or ListenerConfig()
        self.parser = parser or EventParser()
        self.recognizer = GestureRecognizer()

        self._listener: Optional[BufferedEventListener] = None
        self._is_recording = False
        self._gestures: List[Gesture] = []

    @abstractmethod
    def start_recording(self):
        """开始录制"""
        pass

    @abstractmethod
    def stop_recording(self):
        """停止录制"""
        pass

    def is_recording(self) -> bool:
        """是否正在录制"""
        return self._is_recording

    def get_gestures(self) -> List[Gesture]:
        """获取识别的手势"""
        return self._gestures.copy()

    def reset(self):
        """重置录制器"""
        self._gestures.clear()

    def __enter__(self):
        self.start_recording()
        return self

    def __exit__(self, *args):
        self.stop_recording()
