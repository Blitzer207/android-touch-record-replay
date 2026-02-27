"""
测试手势识别器
"""

import pytest

from touch_record.core.gesture_recognizer import (
    BatchGestureRecognizer,
    RealtimeGestureRecognizer,
    GestureRecognizer,
    recognize_gestures,
)
from touch_record.core.gesture_types import LongPress, Swipe, Tap
from touch_record.core.event_types import TouchDown, TouchMove, TouchUp


class TestGestureRecognizer:
    """测试 GestureRecognizer 基础类"""

    def test_recognize_tap(self):
        """测试识别点击"""
        recognizer = GestureRecognizer()

        down = TouchDown(timestamp=0.0, x=500, y=500)
        up = TouchUp(timestamp=0.2, x=505, y=505)  # 移动距离小

        recognizer.add_event(down)
        gesture = recognizer.add_event(up)

        assert gesture is not None
        assert isinstance(gesture, Tap)
        assert gesture.x == 505
        assert gesture.y == 505

    def test_recognize_swipe(self):
        """测试识别滑动"""
        recognizer = GestureRecognizer()

        down = TouchDown(timestamp=0.0, x=500, y=500)
        move1 = TouchMove(timestamp=0.1, x=600, y=500)
        move2 = TouchMove(timestamp=0.2, x=700, y=500)
        up = TouchUp(timestamp=0.3, x=800, y=500)

        recognizer.add_event(down)
        recognizer.add_event(move1)
        recognizer.add_event(move2)
        gesture = recognizer.add_event(up)

        assert gesture is not None
        assert isinstance(gesture, Swipe)
        assert gesture.start_x == 500
        assert gesture.end_x == 800
        assert gesture.direction == "right"

    def test_recognize_long_press(self):
        """测试识别长按"""
        recognizer = GestureRecognizer(long_press_duration=0.5)

        down = TouchDown(timestamp=0.0, x=500, y=500)
        up = TouchUp(timestamp=0.8, x=502, y=502)  # 持续时间长，移动小

        recognizer.add_event(down)
        gesture = recognizer.add_event(up)

        assert gesture is not None
        assert isinstance(gesture, LongPress)

    def test_multiple_gestures(self):
        """测试识别多个手势"""
        recognizer = GestureRecognizer()

        # 第一个点击
        down1 = TouchDown(timestamp=0.0, x=200, y=200)
        up1 = TouchUp(timestamp=0.2, x=205, y=205)

        # 第二个滑动
        down2 = TouchDown(timestamp=0.5, x=100, y=100)
        move2 = TouchMove(timestamp=0.6, x=500, y=100)
        up2 = TouchUp(timestamp=0.7, x=900, y=100)

        recognizer.add_event(down1)
        g1 = recognizer.add_event(up1)
        recognizer.add_event(down2)
        recognizer.add_event(move2)
        g2 = recognizer.add_event(up2)

        assert isinstance(g1, Tap)
        assert isinstance(g2, Swipe)
        assert g2.direction == "right"

        gestures = recognizer.get_gestures()
        assert len(gestures) == 2


class TestRealtimeGestureRecognizer:
    """测试实时手势识别器"""

    def test_realtime_tap(self):
        """测试实时识别点击"""
        recognizer = RealtimeGestureRecognizer()

        down = TouchDown(timestamp=0.0, x=500, y=500)
        up = TouchUp(timestamp=0.2, x=505, y=505)

        g1 = recognizer.add_event(down)
        assert g1 is None  # Down 不产生手势

        g2 = recognizer.add_event(up)
        assert isinstance(g2, Tap)

    def test_realtime_swipe_detection(self):
        """测试实时滑动检测"""
        recognizer = RealtimeGestureRecognizer(swipe_threshold=50.0)

        down = TouchDown(timestamp=0.0, x=100, y=100)
        move1 = TouchMove(timestamp=0.1, x=200, y=100)
        move2 = TouchMove(timestamp=0.2, x=300, y=100)
        move3 = TouchMove(timestamp=0.3, x=400, y=100)  # 距离 300px，超过阈值
        up = TouchUp(timestamp=0.4, x=500, y=500)

        recognizer.add_event(down)
        assert recognizer._is_swiping is False

        recognizer.add_event(move1)
        recognizer.add_event(move2)
        assert recognizer._is_swiping is False

        recognizer.add_event(move3)
        assert recognizer._is_swiping is True  # 应该检测到开始滑动

        g = recognizer.add_event(up)
        assert isinstance(g, Swipe)


class TestBatchGestureRecognizer:
    """测试批量手势识别器"""

    def test_batch_recognize(self):
        """测试批量识别"""
        recognizer = BatchGestureRecognizer()

        events = [
            TouchDown(timestamp=0.0, x=100, y=100, tracking_id=1),
            TouchMove(timestamp=0.1, x=200, y=100, tracking_id=1),
            TouchUp(timestamp=0.2, x=300, y=100, tracking_id=1),
            TouchDown(timestamp=0.5, x=400, y=400, tracking_id=2),
            TouchUp(timestamp=0.6, x=405, y=405, tracking_id=2),
        ]

        gestures = recognizer.recognize_from_events(events)

        assert len(gestures) == 2
        assert isinstance(gestures[0], Swipe)
        assert isinstance(gestures[1], Tap)


class TestSwipeDirection:
    """测试滑动方向检测"""

    def test_swipe_directions(self):
        """测试各方向滑动"""
        recognizer = GestureRecognizer()

        # 向右
        events = [
            TouchDown(timestamp=0.0, x=100, y=500),
            TouchUp(timestamp=0.2, x=900, y=505),
        ]
        recognizer.reset()
        recognizer.add_event(events[0])
        g = recognizer.add_event(events[1])
        assert g.direction == "right"

        # 向左
        events = [
            TouchDown(timestamp=0.0, x=900, y=500),
            TouchUp(timestamp=0.2, x=100, y=505),
        ]
        recognizer.reset()
        recognizer.add_event(events[0])
        g = recognizer.add_event(events[1])
        assert g.direction == "left"

        # 向下
        events = [
            TouchDown(timestamp=0.0, x=500, y=100),
            TouchUp(timestamp=0.2, x=505, y=900),
        ]
        recognizer.reset()
        recognizer.add_event(events[0])
        g = recognizer.add_event(events[1])
        assert g.direction == "down"

        # 向上
        events = [
            TouchDown(timestamp=0.0, x=500, y=900),
            TouchUp(timestamp=0.2, x=505, y=100),
        ]
        recognizer.reset()
        recognizer.add_event(events[0])
        g = recognizer.add_event(events[1])
        assert g.direction == "up"


def test_recognize_gestures_function():
    """测试便捷函数"""
    events = [
        TouchDown(timestamp=0.0, x=500, y=500),
        TouchUp(timestamp=0.2, x=505, y=505),
    ]

    gestures = recognize_gestures(events, realtime=True)
    assert len(gestures) == 1
    assert isinstance(gestures[0], Tap)

    gestures = recognize_gestures(events, realtime=False)
    assert len(gestures) == 1
    assert isinstance(gestures[0], Tap)
