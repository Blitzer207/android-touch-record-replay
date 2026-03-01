"""
手势识别器

从触摸事件序列中识别常见手势（点击、滑动、长按）。
"""

import math
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

    def recognize_from_events(self, events: List[TouchEvent]) -> List[Gesture]:
        """
        从事件列表中识别所有手势

        Args:
            events: 触摸事件列表

        Returns:
            识别出的手势列表
        """
        # 按时间排序事件
        sorted_events = sorted(events, key=lambda e: e.timestamp)

        gestures = []
        i = 0
        # 初始化 last_timestamp 为第一个事件的时间戳，避免第一个手势的 delay 过大
        last_timestamp = sorted_events[0].timestamp if sorted_events else 0.0

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

    def _calculate_distance(
        self, event1: TouchEvent, event2: TouchEvent
    ) -> float:
        """计算两个事件之间的距离"""
        dx = event1.x - event2.x
        dy = event1.y - event2.y
        return math.sqrt(dx * dx + dy * dy)


def recognize_gestures(
    events: List[TouchEvent],
    **kwargs,
) -> List[Gesture]:
    """
    便捷函数：从事件列表中识别手势

    Args:
        events: 触摸事件列表
        **kwargs: 传递给识别器的参数

    Returns:
        识别出的手势列表
    """
    recognizer = GestureRecognizer(**kwargs)
    return recognizer.recognize_from_events(events)
