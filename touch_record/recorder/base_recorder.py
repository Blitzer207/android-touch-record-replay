"""
基础录制器接口

定义录制器的抽象基类，统一录制行为。
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..core.event_listener import EventListener, ListenerConfig
from ..core.event_parser import EventParser, TouchEventStream
from ..core.gesture_recognizer import GestureRecognizer, recognize_gestures
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
        recognizer: Optional[GestureRecognizer] = None,
    ):
        self.listener_config = listener_config or ListenerConfig()
        self.parser = parser or EventParser()
        self.recognizer = recognizer or GestureRecognizer()

        self._listener: Optional[EventListener] = None
        self._is_recording = False
        self._events: List[object] = []  # 可以是原始事件或手势

    @abstractmethod
    def start_recording(self):
        """开始录制"""
        pass

    @abstractmethod
    def stop_recording(self):
        """停止录制"""
        pass

    @abstractmethod
    def on_gesture(self, gesture: Gesture):
        """当识别到新手势时调用"""
        pass

    @abstractmethod
    def on_event(self, event):
        """当收到新事件时调用"""
        pass

    def is_recording(self) -> bool:
        """是否正在录制"""
        return self._is_recording

    def get_events(self) -> List[object]:
        """获取录制的事件/手势"""
        return self._events.copy()

    def get_gestures(self) -> List[Gesture]:
        """获取识别的手势"""
        return [e for e in self._events if isinstance(e, Gesture)]

    def reset(self):
        """重置录制器"""
        self._events.clear()
        self.recognizer.reset()

    def _setup_listener(self):
        """设置事件监听器"""
        if self._listener is None:
            self._listener = EventListener(self.listener_config)
            self._listener.start()
        self._is_recording = True

    def _teardown_listener(self):
        """清理事件监听器"""
        if self._listener:
            self._listener.stop()
            self._listener = None
        self._is_recording = False

    def __enter__(self):
        self.start_recording()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_recording()
