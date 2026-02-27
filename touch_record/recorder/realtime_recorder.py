"""
实时录制器

实时录制触摸操作，每识别到一个手势立即处理。
"""

import time
from typing import Callable, List, Optional

from .base_recorder import BaseRecorder
from ..core.event_listener import CallbackEventListener, ListenerConfig
from ..core.event_parser import EventParser
from ..core.gesture_recognizer import RealtimeGestureRecognizer
from ..core.gesture_types import Gesture


class RealtimeRecorder(BaseRecorder):
    """
    实时录制器

    特点：
    - 每识别到一个手势立即调用回调
    - 适合需要即时处理的场景
    - 使用 RealtimeGestureRecognizer 进行实时识别
    """

    def __init__(
        self,
        listener_config: Optional[ListenerConfig] = None,
        parser: Optional[EventParser] = None,
        gesture_callback: Optional[Callable[[Gesture], None]] = None,
        event_callback: Optional[Callable] = None,
    ):
        # 使用实时手势识别器
        recognizer = RealtimeGestureRecognizer()
        super().__init__(listener_config, parser, recognizer)

        self.gesture_callback = gesture_callback
        self.event_callback = event_callback
        self._listener: Optional[CallbackEventListener] = None

    def start_recording(self):
        """开始录制"""
        if self._is_recording:
            raise RuntimeError("Recording is already in progress")

        # 使用支持回调的监听器
        self._listener = CallbackEventListener(
            self.listener_config,
            on_event=self._on_raw_event,
        )
        self._listener.start()
        self._is_recording = True

    def stop_recording(self):
        """停止录制"""
        if not self._is_recording:
            return

        if self._listener:
            self._listener.stop()
            self._listener = None
        self._is_recording = False

    def _on_raw_event(self, raw_line: str):
        """处理原始事件行"""
        # 解析原始事件
        raw = self.parser.parse_line(raw_line)
        if raw is None:
            return

        # 处理事件并生成触摸事件
        for touch_event in self.parser._process_raw_event(raw):
            # 识别手势
            gesture = self.recognizer.add_event(touch_event)

            if gesture:
                # 存储手势
                self._events.append(gesture)

                # 调用手势回调
                if self.gesture_callback:
                    self.gesture_callback(gesture)

            # 调用事件回调
            if self.event_callback:
                self.event_callback(touch_event)

    def on_gesture(self, gesture: Gesture):
        """当识别到新手势时调用"""
        self._events.append(gesture)

    def on_event(self, event):
        """当收到新事件时调用"""
        self._events.append(event)

    def record_gestures(
        self,
        duration: Optional[float] = None,
        max_gestures: Optional[int] = None,
    ) -> List[Gesture]:
        """
        录制手势

        Args:
            duration: 最大录制时长（秒），None 表示无限
            max_gestures: 最大手势数量，None 表示无限

        Returns:
            录制的手势列表
        """
        self.start_recording()

        try:
            if duration is not None:
                end_time = time.time() + duration
                while time.time() < end_time:
                    if max_gestures and len(self.get_gestures()) >= max_gestures:
                        break
                    time.sleep(0.1)
            else:
                while True:
                    if max_gestures and len(self.get_gestures()) >= max_gestures:
                        break
                    time.sleep(0.1)

        finally:
            self.stop_recording()

        return self.get_gestures()


def realtime_record(
    gesture_callback: Optional[Callable[[Gesture], None]] = None,
    duration: Optional[float] = None,
    max_gestures: Optional[int] = None,
    **kwargs
) -> List[Gesture]:
    """
    便捷函数：实时录制手势

    Args:
        gesture_callback: 手势回调函数
        duration: 最大录制时长
        max_gestures: 最大手势数量
        **kwargs: 传递给 ListenerConfig 的参数

    Returns:
        录制的手势列表
    """
    config = ListenerConfig(**kwargs)
    recorder = RealtimeRecorder(config, gesture_callback=gesture_callback)
    return recorder.record_gestures(duration, max_gestures)
