"""
事件解析器

解析 getevent 的原始输出，转换为结构化的触摸事件。
"""

import re
from datetime import datetime
from typing import Dict, Generator, List, Optional, Tuple

from .device_info import DeviceInfo
from .event_types import (
    RawEvent,
    TouchDown,
    TouchEvent,
    TouchMove,
    TouchUp,
)


class EventParser:
    """
    getevent 事件解析器

    解析格式示例：
    /dev/input/event0: 0003 0035 0000035a  (ABS_MT_POSITION_X)
    /dev/input/event0: 0003 0036 0000021c  (ABS_MT_POSITION_Y)
    /dev/input/event0: 0003 0039 00000001  (ABS_MT_TRACKING_ID)
    /dev/input/event0: 0001 014a 00000001  (BTN_TOUCH)
    """

    # 正则表达式匹配 getevent 输出
    LINE_PATTERN = re.compile(
        r"^(/dev/input/event\d+):\s*([0-9a-fA-F]{4})\s+([0-9a-fA-F]{4})\s+([0-9a-fA-F]{8})"
    )

    def __init__(self, device_info: Optional[DeviceInfo] = None):
        self.device_info = device_info
        self._current_device: Optional[str] = None
        self._current_x: int = 0
        self._current_y: int = 0
        self._current_pressure: float = 0.0
        self._current_tracking_id: Optional[int] = None
        self._touch_down: bool = False

    def parse_line(self, line: str) -> Optional[RawEvent]:
        """
        解析单行 getevent 输出

        Args:
            line: getevent 输出行

        Returns:
            解析后的原始事件，如果无法解析则返回 None
        """
        match = self.LINE_PATTERN.match(line.strip())
        if not match:
            return None

        device = match.group(1)
        type_code = int(match.group(2), 16)
        code = int(match.group(3), 16)
        value = int(match.group(4), 16)

        self._current_device = device

        return RawEvent(
            device=device,
            type_code=type_code,
            code=code,
            value=value,
            timestamp=datetime.now().timestamp(),
        )

    def parse_block(
        self, lines: List[str]
    ) -> Generator[TouchEvent, None, None]:
        """
        解析一个事件块（一组相关的原始事件）

        一个事件块以 SYN_REPORT (0000 0000) 结束

        Args:
            lines: 事件行列表

        Yields:
            结构化的触摸事件
        """
        self._reset_state()

        for line in lines:
            raw = self.parse_line(line)
            if raw is None:
                continue

            yield from self._process_raw_event(raw)

    def parse_stream(
        self, line_stream: Generator[str, None, None]
    ) -> Generator[TouchEvent, None, None]:
        """
        解析事件流

        自动识别事件块边界（SYN_REPORT）

        Args:
            line_stream: 事件行生成器

        Yields:
            结构化的触摸事件
        """
        block: List[str] = []

        for line in line_stream:
            block.append(line)

            # 检测 SYN_REPORT
            if "0000 0000" in line:
                if block:
                    yield from self.parse_block(block)
                    block.clear()

        # 处理剩余的事件
        if block:
            yield from self.parse_block(block)

    def _process_raw_event(self, raw: RawEvent) -> Generator[TouchEvent, None, None]:
        """处理单个原始事件，生成触摸事件"""
        if not raw.is_touch_event():
            return

        # 更新当前状态
        if raw.is_x_position():
            self._current_x = raw.value

        elif raw.is_y_position():
            self._current_y = raw.value

        elif raw.is_pressure():
            self._current_pressure = raw.value / 255.0  # 归一化压力值

        elif raw.is_tracking_id():
            # tracking_id == -1 (0xffffffff) 表示触摸抬起
            if raw.value == 0xFFFFFFFF:
                if self._touch_down:
                    yield self._create_touch_up(raw.timestamp)
            else:
                self._current_tracking_id = raw.value

        # 检测 BTN_TOUCH 事件
        elif raw.type_code == 1 and raw.code == 0x014A:  # BTN_TOUCH
            if raw.value == 1:  # 按下
                if not self._touch_down:
                    yield self._create_touch_down(raw.timestamp)
            elif raw.value == 0:  # 抬起
                if self._touch_down:
                    yield self._create_touch_up(raw.timestamp)

        # 生成移动事件
        elif self._touch_down:
            yield self._create_touch_move(raw.timestamp)

    def _create_touch_down(self, timestamp: float) -> TouchDown:
        """创建触摸按下事件"""
        self._touch_down = True

        # 坐标转换
        x, y = self._convert_coordinates(self._current_x, self._current_y)

        return TouchDown(
            timestamp=timestamp,
            device=self._current_device or "",
            x=x,
            y=y,
            pressure=self._current_pressure,
            tracking_id=self._current_tracking_id,
        )

    def _create_touch_up(self, timestamp: float) -> TouchUp:
        """创建触摸抬起事件"""
        self._touch_down = False

        # 坐标转换
        x, y = self._convert_coordinates(self._current_x, self._current_y)

        event = TouchUp(
            timestamp=timestamp,
            device=self._current_device or "",
            x=x,
            y=y,
            tracking_id=self._current_tracking_id,
        )

        self._current_tracking_id = None
        return event

    def _create_touch_move(self, timestamp: float) -> TouchMove:
        """创建触摸移动事件"""

        # 坐标转换
        x, y = self._convert_coordinates(self._current_x, self._current_y)

        return TouchMove(
            timestamp=timestamp,
            device=self._current_device or "",
            x=x,
            y=y,
            pressure=self._current_pressure,
            tracking_id=self._current_tracking_id,
        )

    def _convert_coordinates(self, x: int, y: int) -> Tuple[float, float]:
        """坐标转换"""
        if self.device_info and self.device_info.touch_device:
            device = self.device_info.touch_device
            return self.device_info.convert_coordinates(x, y, device)
        return float(x), float(y)

    def _reset_state(self):
        """重置解析状态"""
        self._current_device = None
        self._current_x = 0
        self._current_y = 0
        self._current_pressure = 0.0
        self._current_tracking_id = None
        self._touch_down = False


class TouchEventStream:
    """
    触摸事件流

    从监听器获取原始事件，解析并输出结构化的触摸事件
    """

    def __init__(
        self,
        device_info: Optional[DeviceInfo] = None,
        parser: Optional[EventParser] = None,
    ):
        self.parser = parser or EventParser(device_info)
        self._touch_events: List[TouchEvent] = []
        self._last_timestamp: Optional[float] = None

    def feed_line(self, line: str) -> List[TouchEvent]:
        """
        喂入一行原始事件

        Args:
            line: getevent 输出行

        Returns:
            生成的触摸事件列表
        """
        events = []

        raw = self.parser.parse_line(line)
        if raw is None:
            return events

        for event in self.parser._process_raw_event(raw):
            events.append(event)
            self._touch_events.append(event)

        return events

    def feed_lines(self, lines: List[str]) -> List[TouchEvent]:
        """
        喂入多行原始事件

        Args:
            lines: getevent 输出行列表

        Returns:
            生成的触摸事件列表
        """
        all_events = []
        for line in lines:
            all_events.extend(self.feed_line(line))
        return all_events

    def get_events(self) -> List[TouchEvent]:
        """获取所有已解析的触摸事件"""
        return self._touch_events.copy()

    def clear(self):
        """清空已缓存的事件"""
        self._touch_events.clear()
        self.parser._reset_state()


def parse_event_lines(
    lines: List[str], device_info: Optional[DeviceInfo] = None
) -> List[TouchEvent]:
    """
    便捷函数：解析事件行列表

    Args:
        lines: getevent 输出行列表
        device_info: 设备信息（用于坐标转换）

    Returns:
        触摸事件列表
    """
    parser = EventParser(device_info)
    events = []
    for line in lines:
        raw = parser.parse_line(line)
        if raw:
            for event in parser._process_raw_event(raw):
                events.append(event)
    return events
