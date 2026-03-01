"""
批量录制器

批量录制所有触摸操作，停止后统一处理。
"""

from typing import List, Optional

from .base_recorder import BaseRecorder
from ..core.event_listener import BufferedEventListener, ListenerConfig
from ..core.event_parser import EventParser
from ..core.gesture_recognizer import GestureRecognizer
from ..core.gesture_types import Gesture


class BatchRecorder(BaseRecorder):
    """
    批量录制器

    特点：
    - 收集所有事件
    - 停止后统一生成手势
    """

    def __init__(
        self,
        listener_config: Optional[ListenerConfig] = None,
        parser: Optional[EventParser] = None,
    ):
        super().__init__(listener_config, parser)

    def start_recording(self):
        """开始录制"""
        if self._is_recording:
            raise RuntimeError("Recording is already in progress")

        # 使用缓冲监听器
        self._listener = BufferedEventListener(self.listener_config)
        self._listener.start()
        self._is_recording = True

    def stop_recording(self):
        """停止录制并处理事件"""
        if not self._is_recording:
            return

        # 收集所有原始行
        raw_lines = []
        if self._listener:
            raw_lines.extend(self._listener.flush())
            self._listener.stop()
            self._listener = None

        self._is_recording = False

        # 解析事件
        self.parser.reset()
        touch_events = self.parser.parse_lines(raw_lines)

        # 识别手势
        self._gestures = self.recognizer.recognize_from_events(touch_events)


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
    import time

    config = ListenerConfig(**kwargs)
    recorder = BatchRecorder(config)
    recorder.start_recording()
    time.sleep(duration)
    recorder.stop_recording()
    return recorder.get_gestures()
