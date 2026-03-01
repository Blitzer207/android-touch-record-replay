"""
触摸事件类型定义

定义从 getevent 解析出的原始触摸事件类型。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from .constants import (
    EV_ABS,
    EV_KEY,
    EV_SYN,
    ABS_MT_POSITION_X,
    ABS_MT_POSITION_Y,
    ABS_MT_TRACKING_ID,
)


@dataclass
class TouchEvent:
    """触摸事件基类"""

    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    device: str = ""
    tracking_id: Optional[int] = None

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        return f"{cls_name}(timestamp={self.timestamp:.3f}, device={self.device})"


@dataclass
class TouchDown(TouchEvent):
    """触摸按下事件"""

    x: float = 0.0
    y: float = 0.0
    pressure: float = 0.0

    def __repr__(self) -> str:
        return (
            f"TouchDown(timestamp={self.timestamp:.3f}, x={self.x:.1f}, "
            f"y={self.y:.1f}, pressure={self.pressure:.2f})"
        )


@dataclass
class TouchUp(TouchEvent):
    """触摸抬起事件"""

    x: float = 0.0
    y: float = 0.0

    def __repr__(self) -> str:
        return (
            f"TouchUp(timestamp={self.timestamp:.3f}, x={self.x:.1f}, "
            f"y={self.y:.1f})"
        )


@dataclass
class TouchMove(TouchEvent):
    """触摸移动事件"""

    x: float = 0.0
    y: float = 0.0
    pressure: float = 0.0

    def __repr__(self) -> str:
        return (
            f"TouchMove(timestamp={self.timestamp:.3f}, x={self.x:.1f}, "
            f"y={self.y:.1f}, pressure={self.pressure:.2f})"
        )


@dataclass
class RawEvent:
    """原始 getevent 事件"""

    device: str
    type_code: int
    code: int
    value: int
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())

    def is_touch_event(self) -> bool:
        """判断是否为触摸相关事件"""
        return self.type_code in (EV_KEY, EV_ABS)

    def is_x_position(self) -> bool:
        """判断是否为 X 坐标事件"""
        return self.type_code == EV_ABS and self.code == ABS_MT_POSITION_X

    def is_y_position(self) -> bool:
        """判断是否为 Y 坐标事件"""
        return self.type_code == EV_ABS and self.code == ABS_MT_POSITION_Y

    def is_tracking_id(self) -> bool:
        """判断是否为追踪 ID 事件"""
        return self.type_code == EV_ABS and self.code == ABS_MT_TRACKING_ID

    def is_pressure(self) -> bool:
        """判断是否为压力事件 (ABS_MT_PRESSURE = 0x3a = 58)"""
        return self.type_code == EV_ABS and self.code == 0x3A

    def is_syn_report(self) -> bool:
        """判断是否为同步报告事件"""
        return self.type_code == EV_SYN

    def __repr__(self) -> str:
        return (
            f"RawEvent(device={self.device}, type=0x{self.type_code:02x}, "
            f"code=0x{self.code:02x}, value=0x{self.value:08x})"
        )
