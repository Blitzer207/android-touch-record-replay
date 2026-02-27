"""
测试事件解析器
"""

import pytest

from touch_record.core.event_parser import EventParser
from touch_record.core.event_types import RawEvent, TouchDown, TouchMove, TouchUp


class TestRawEvent:
    """测试 RawEvent 类"""

    def test_touch_event_detection(self):
        """测试触摸事件检测"""
        # X 坐标事件
        event = RawEvent("/dev/input/event0", 0x03, 0x35, 0x0000035a)
        assert event.is_touch_event() is True
        assert event.is_x_position() is True

        # Y 坐标事件
        event = RawEvent("/dev/input/event0", 0x03, 0x36, 0x0000021c)
        assert event.is_y_position() is True

        # 追踪 ID 事件
        event = RawEvent("/dev/input/event0", 0x03, 0x39, 0x00000001)
        assert event.is_tracking_id() is True

        # 压力事件
        event = RawEvent("/dev/input/event0", 0x03, 0x3A, 0x00000064)
        assert event.is_pressure() is True

        # 同步报告
        event = RawEvent("/dev/input/event0", 0x00, 0x00, 0x00000000)
        assert event.is_syn_report() is True

        # 非触摸事件
        event = RawEvent("/dev/input/event0", 0x02, 0x00, 0x00000000)
        assert event.is_touch_event() is False


class TestEventParser:
    """测试 EventParser 类"""

    def test_parse_line_valid(self):
        """测试解析有效的 getevent 输出行"""
        parser = EventParser()

        line = "/dev/input/event0: 0003 0035 0000035a"
        raw = parser.parse_line(line)

        assert raw is not None
        assert raw.device == "/dev/input/event0"
        assert raw.type_code == 0x03
        assert raw.code == 0x35
        assert raw.value == 0x0000035a

    def test_parse_line_invalid(self):
        """测试解析无效的 getevent 输出行"""
        parser = EventParser()

        line = "invalid line format"
        raw = parser.parse_line(line)

        assert raw is None

    def test_parse_tap_sequence(self):
        """测试解析点击手势序列"""
        parser = EventParser()
        events = []

        # 模拟点击事件序列
        lines = [
            "/dev/input/event0: 0003 0039 00000001",  # tracking_id
            "/dev/input/event0: 0003 0035 000003e8",  # x = 1000
            "/dev/input/event0: 0003 0036 000002d0",  # y = 720
            "/dev/input/event0: 0001 014a 00000001",  # BTN_TOUCH down
            "/dev/input/event0: 0000 0000 00000000",  # SYN_REPORT
            "/dev/input/event0: 0001 014a 00000000",  # BTN_TOUCH up
            "/dev/input/event0: 0003 0039 ffffffff",  # tracking_id -1
            "/dev/input/event0: 0000 0000 00000000",  # SYN_REPORT
        ]

        for line in lines:
            raw = parser.parse_line(line)
            if raw:
                for touch_event in parser._process_raw_event(raw):
                    events.append(touch_event)

        # 应该有一个 Down 和一个 Up
        assert len(events) >= 2
        assert any(isinstance(e, TouchDown) for e in events)
        assert any(isinstance(e, TouchUp) for e in events)

    def test_parse_swipe_sequence(self):
        """测试解析滑动手势序列"""
        parser = EventParser()
        events = []

        # 模拟滑动事件序列
        lines = [
            "/dev/input/event0: 0003 0039 00000001",  # tracking_id
            "/dev/input/event0: 0003 0035 00000100",  # x = 256 (start)
            "/dev/input/event0: 0003 0036 00000200",  # y = 512
            "/dev/input/event0: 0001 014a 00000001",  # BTN_TOUCH down
            "/dev/input/event0: 0000 0000 00000000",  # SYN_REPORT
            "/dev/input/event0: 0003 0035 00000200",  # x = 512 (move)
            "/dev/input/event0: 0000 0000 00000000",  # SYN_REPORT
            "/dev/input/event0: 0003 0035 00000300",  # x = 768 (move)
            "/dev/input/event0: 0000 0000 00000000",  # SYN_REPORT
            "/dev/input/event0: 0001 014a 00000000",  # BTN_TOUCH up
            "/dev/input/event0: 0003 0039 ffffffff",  # tracking_id -1
            "/dev/input/event0: 0000 0000 00000000",  # SYN_REPORT
        ]

        for line in lines:
            raw = parser.parse_line(line)
            if raw:
                for touch_event in parser._process_raw_event(raw):
                    events.append(touch_event)

        # 应该有 Down、Move 和 Up
        assert len(events) >= 2
        assert any(isinstance(e, TouchDown) for e in events)
        assert any(isinstance(e, TouchMove) for e in events)
        assert any(isinstance(e, TouchUp) for e in events)
