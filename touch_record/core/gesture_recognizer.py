"""
手势识别器

从触摸事件序列中识别常见手势（点击、滑动、长按）。
"""

import math
from datetime import datetime
from typing import List, Optional, Tuple

from .event_types import TouchDown, TouchEvent, TouchMove, TouchUp
from .gesture_types import Gesture, LongPress, Swipe, Tap


class GestureRecognizer:
    """
    手势识别器

    识别规则：
    - 点击：Down -> Up，移动距离 < 阈值，持续时间 < 阈值
    - 长按：Down -> Up，移动距离 < 阈值，持续时间 >= 阈值
    - 滑动：Down -> Move... -> Up，移动距离 >= 阈值
    """

    # 默认阈值配置
    DEFAULT_TAP_THRESHOLD = 10.0  # 点击最大移动距离（像素）
    DEFAULT_TAP_DURATION = 0.3  # 点击最大持续时间（秒）
    DEFAULT_LONG_PRESS_DURATION = 0.5  # 长按最小持续时间（秒）
    DEFAULT_SWIPE_THRESHOLD = 50.0  # 滑动最小距离（像素）

    def __init__(
        self,
        tap_threshold: float = DEFAULT_TAP_THRESHOLD,
        tap_duration: float = DEFAULT_TAP_DURATION,
        long_press_duration: float = DEFAULT_LONG_PRESS_DURATION,
        swipe_threshold: float = DEFAULT_SWIPE_THRESHOLD,
    ):
        self.tap_threshold = tap_threshold
        self.tap_duration = tap_duration
        self.long_press_duration = long_press_duration
        self.swipe_threshold = swipe_threshold

        self._events: List[TouchEvent] = []
        self._gestures: List[Gesture] = []
        self._last_gesture_end_time: float = 0.0

    def add_event(self, event: TouchEvent) -> Optional[Gesture]:
        """
        添加一个触摸事件并尝试识别手势

        Args:
            event: 触摸事件

        Returns:
            如果识别到完整手势则返回，否则返回 None
        """
        self._events.append(event)

        if isinstance(event, TouchDown):
            return self._on_down(event)

        elif isinstance(event, TouchUp):
            return self._on_up(event)

        elif isinstance(event, TouchMove):
            return self._on_move(event)

        return None

    def _on_down(self, event: TouchDown) -> Optional[Gesture]:
        """处理触摸按下事件"""
        # Down 事件不产生手势，只是开始追踪
        return None

    def _on_up(self, event: TouchUp) -> Optional[Gesture]:
        """处理触摸抬起事件"""
        # 查找对应的 Down 事件
        down_event = self._find_last_down()
        if down_event is None:
            return None

        # 计算距离和持续时间
        distance = self._calculate_distance(down_event, event)
        duration = event.timestamp - down_event.timestamp

        # 计算延迟
        delay = event.timestamp - self._last_gesture_end_time
        self._last_gesture_end_time = event.timestamp

        # 识别手势
        if distance < self.tap_threshold:
            # 移动距离小，可能是点击或长按
            if duration < self.long_press_duration:
                gesture = Tap(
                    start_time=down_event.timestamp,
                    end_time=event.timestamp,
                    duration=duration,
                    x=event.x,
                    y=event.y,
                )
            else:
                gesture = LongPress(
                    start_time=down_event.timestamp,
                    end_time=event.timestamp,
                    duration=duration,
                    x=event.x,
                    y=event.y,
                )
        else:
            # 移动距离大，是滑动
            gesture = Swipe(
                start_time=down_event.timestamp,
                end_time=event.timestamp,
                duration=duration,
                start_x=down_event.x,
                start_y=down_event.y,
                end_x=event.x,
                end_y=event.y,
            )

        # 设置延迟
        gesture.delay_before = delay
        self._gestures.append(gesture)
        return gesture

    def _on_move(self, event: TouchMove) -> Optional[Gesture]:
        """
        处理触摸移动事件

        目前只记录事件，实际手势识别在 Up 时完成
        """
        return None

    def _find_last_down(self) -> Optional[TouchDown]:
        """查找最后一个 Down 事件"""
        for event in reversed(self._events):
            if isinstance(event, TouchDown):
                return event
        return None

    def _calculate_distance(
        self, event1: TouchEvent, event2: TouchEvent
    ) -> float:
        """计算两个事件之间的距离"""
        dx = event1.x - event2.x
        dy = event1.y - event2.y
        return math.sqrt(dx * dx + dy * dy)

    def recognize_all(self, events: List[TouchEvent]) -> List[Gesture]:
        """
        从事件列表中识别所有手势

        Args:
            events: 触摸事件列表

        Returns:
            识别出的手势列表
        """
        gestures = []
        for event in events:
            gesture = self.add_event(event)
            if gesture:
                gestures.append(gesture)
        return gestures

    def get_gestures(self) -> List[Gesture]:
        """获取已识别的所有手势"""
        return self._gestures.copy()

    def reset(self):
        """重置识别器状态"""
        self._events.clear()
        self._gestures.clear()
        self._last_gesture_end_time = 0.0


class RealtimeGestureRecognizer(GestureRecognizer):
    """
    实时手势识别器

    在接收到事件时立即识别手势，适用于实时录制场景
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_down: Optional[TouchDown] = None
        self._move_count: int = 0
        self._is_swiping: bool = False

    def add_event(self, event: TouchEvent) -> Optional[Gesture]:
        """添加事件并实时识别"""
        if isinstance(event, TouchDown):
            return self._handle_down(event)
        elif isinstance(event, TouchMove):
            return self._handle_move(event)
        elif isinstance(event, TouchUp):
            return self._handle_up(event)
        return None

    def _handle_down(self, event: TouchDown) -> Optional[Gesture]:
        """处理按下事件"""
        self._current_down = event
        self._move_count = 0
        self._is_swiping = False
        return None

    def _handle_move(self, event: TouchMove) -> Optional[Gesture]:
        """处理移动事件"""
        if self._current_down is None:
            return None

        self._move_count += 1

        # 检测是否开始滑动
        if not self._is_swiping and self._move_count >= 3:
            distance = self._calculate_distance(self._current_down, event)
            if distance >= self.swipe_threshold:
                self._is_swiping = True

        return None

    def _handle_up(self, event: TouchUp) -> Optional[Gesture]:
        """处理抬起事件"""
        if self._current_down is None:
            return None

        down = self._current_down
        distance = self._calculate_distance(down, event)
        duration = event.timestamp - down.timestamp

        # 计算延迟
        delay = event.timestamp - self._last_gesture_end_time
        self._last_gesture_end_time = event.timestamp

        if distance < self.tap_threshold:
            if duration < self.long_press_duration:
                gesture = Tap(
                    start_time=down.timestamp,
                    end_time=event.timestamp,
                    duration=duration,
                    x=event.x,
                    y=event.y,
                )
            else:
                gesture = LongPress(
                    start_time=down.timestamp,
                    end_time=event.timestamp,
                    duration=duration,
                    x=event.x,
                    y=event.y,
                )
        else:
            gesture = Swipe(
                start_time=down.timestamp,
                end_time=event.timestamp,
                duration=duration,
                start_x=down.x,
                start_y=down.y,
                end_x=event.x,
                end_y=event.y,
            )

        gesture.delay_before = delay

        # 重置状态
        self._current_down = None
        self._move_count = 0
        self._is_swiping = False

        self._gestures.append(gesture)
        return gesture


class BatchGestureRecognizer(GestureRecognizer):
    """
    批量手势识别器

    收集所有事件后统一识别，适用于批量录制场景
    """

    def recognize_from_events(self, events: List[TouchEvent]) -> List[Gesture]:
        """
        从事件列表中识别手势

        使用基于窗口的方法，更准确地识别复杂手势序列
        """
        self.reset()
        gestures = []

        # 按时间排序事件
        sorted_events = sorted(events, key=lambda e: e.timestamp)

        i = 0
        last_timestamp = 0.0

        while i < len(sorted_events):
            event = sorted_events[i]

            if isinstance(event, TouchDown):
                # 找到完整的 Down-Up 序列
                sequence = self._extract_touch_sequence(sorted_events, i)

                if sequence:
                    down, moves, up = sequence
                    gesture = self._recognize_sequence(down, moves, up, last_timestamp)

                    if gesture:
                        gestures.append(gesture)
                        last_timestamp = up.timestamp
                        i += len(moves) + 2  # 跳过已处理的事件
                        continue

            i += 1

        self._gestures = gestures
        return gestures

    def _extract_touch_sequence(
        self, events: List[TouchEvent], start_index: int
    ) -> Optional[Tuple[TouchDown, List[TouchMove], TouchUp]]:
        """
        提取一个完整的触摸序列 (Down -> [Move...] -> Up)

        Returns:
            (down_event, move_events, up_event) 或 None
        """
        if start_index >= len(events):
            return None

        down = events[start_index]
        if not isinstance(down, TouchDown):
            return None

        tracking_id = down.tracking_id

        # 查找同一 tracking_id 的事件序列
        moves = []
        i = start_index + 1

        while i < len(events):
            event = events[i]

            # 检查是否为同一追踪 ID
            if event.tracking_id != tracking_id:
                i += 1
                continue

            if isinstance(event, TouchUp):
                return down, moves, event
            elif isinstance(event, TouchMove):
                moves.append(event)
                else:
                    # 遇到新的 Down，序列结束
                    break

            i += 1

        return None

    def _recognize_sequence(
        self,
        down: TouchDown,
        moves: List[TouchMove],
        up: TouchUp,
        last_timestamp: float,
    ) -> Optional[Gesture]:
        """识别一个触摸序列对应的手势"""
        # 计算移动距离
        if moves:
            # 有移动事件，计算最大移动距离
            max_distance = max(
                self._calculate_distance(down, m) for m in moves
            )
            end_distance = self._calculate_distance(down, up)
            distance = max(max_distance, end_distance)
        else:
            distance = self._calculate_distance(down, up)

        duration = up.timestamp - down.timestamp
        delay = up.timestamp - last_timestamp

        if distance < self.tap_threshold:
            if duration < self.long_press_duration:
                gesture = Tap(
                    start_time=down.timestamp,
                    end_time=up.timestamp,
                    duration=duration,
                    x=up.x,
                    y=up.y,
                )
            else:
                gesture = LongPress(
                    start_time=down.timestamp,
                    end_time=up.timestamp,
                    duration=duration,
                    x=up.x,
                    y=up.y,
                )
        else:
            # 滑动
            if moves:
                # 使用移动最远的点作为终点
                farthest_move = max(
                    moves, key=lambda m: self._calculate_distance(down, m)
                )
                end_x, end_y = farthest_move.x, farthest_move.y
            else:
                end_x, end_y = up.x, up.y

            gesture = Swipe(
                start_time=down.timestamp,
                end_time=up.timestamp,
                duration=duration,
                start_x=down.x,
                start_y=down.y,
                end_x=end_x,
                end_y=end_y,
            )

        gesture.delay_before = delay
        return gesture


def recognize_gestures(
    events: List[TouchEvent],
    realtime: bool = False,
    **kwargs,
) -> List[Gesture]:
    """
    便捷函数：从事件列表中识别手势

    Args:
        events: 触摸事件列表
        realtime: 是否使用实时识别模式
        **kwargs: 传递给识别器的参数

    Returns:
        识别出的手势列表
    """
    if realtime:
        recognizer = RealtimeGestureRecognizer(**kwargs)
    else:
        recognizer = BatchGestureRecognizer(**kwargs)
        return recognizer.recognize_from_events(events)

    return recognizer.recognize_all(events)
