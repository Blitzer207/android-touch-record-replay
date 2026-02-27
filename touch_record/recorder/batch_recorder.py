"""
批量录制器

批量录制所有触摸操作，停止后统一处理。
"""

from typing import List, Optional

from .base_recorder import BaseRecorder
from ..core.event_listener import BufferedEventListener, ListenerConfig
from ..core.event_parser import EventParser, TouchEventStream
from ..core.gesture_recognizer import BatchGestureRecognizer
from ..core.gesture_types import Gesture


class BatchRecorder(BaseRecorder):
    """
    批量录制器

    特点：
    - 收集所有事件
    - 停止后统一生成手势
    - 使用 BatchGestureRecognizer 进行批量识别
    - 更准确地识别复杂手势序列
    """

    def __init__(
        self,
        listener_config: Optional[ListenerConfig] = None,
        parser: Optional[EventParser] = None,
    ):
        # 使用批量手势识别器
        recognizer = BatchGestureRecognizer()
        super().__init__(listener_config, parser, recognizer)

        self._listener: Optional[BufferedEventListener] = None
        self._raw_lines: List[str] = []

    def start_recording(self):
        """开始录制"""
        if self._is_recording:
            raise RuntimeError("Recording is already in progress")

        # 使用缓冲监听器
        self._listener = BufferedEventListener(self.listener_config)
        self._listener.start()
        self._is_recording = True
        self._raw_lines.clear()

    def stop_recording(self):
        """停止录制并处理事件"""
        if not self._is_recording:
            return

        # 收集所有原始行
        if self._listener:
            self._raw_lines.extend(self._listener.flush())
            self._listener.stop()
            self._listener = None

        self._is_recording = False

        # 处理并识别手势
        self._process_events()

    def _process_events(self):
        """处理收集的事件并识别手势"""
        # 解析事件
        stream = TouchEventStream(parser=self.parser)
        touch_events = stream.feed_lines(self._raw_lines)

        # 识别手势
        if isinstance(self.recognizer, BatchGestureRecognizer):
            gestures = self.recognizer.recognize_from_events(touch_events)
        else:
            gestures = self.recognizer.recognize_all(touch_events)

        self._events.clear()
        self._events.extend(gestures)

    def on_gesture(self, gesture: Gesture):
        """当识别到新手势时调用（批量模式下不使用）"""
        # 批量模式下，手势在 stop_recording 时统一生成
        pass

    def on_event(self, event):
        """当收到新事件时调用（批量模式下不使用）"""
        # 批量模式下，事件在 stop_recording 时统一处理
        pass

    def get_raw_lines(self) -> List[str]:
        """获取原始事件行"""
        return self._raw_lines.copy()

    def record_for_duration(self, duration: float) -> List[Gesture]:
        """
        录制指定时长

        Args:
            duration: 录制时长（秒）

        Returns:
            识别出的手势列表
        """
        import time

        self.start_recording()
        time.sleep(duration)
        self.stop_recording()
        return self.get_gestures()


def batch_record(
    duration: float,
    **kwargs
) -> List[Gesture]:
    """
    便捷函数：批量录制手势

    Args:
        duration: 录制时长（秒）
        **kwargs: 传递给 ListenerConfig 的参数

    Returns:
        识别出的手势列表
    """
    config = ListenerConfig(**kwargs)
    recorder = BatchRecorder(config)
    return recorder.record_for_duration(duration)
