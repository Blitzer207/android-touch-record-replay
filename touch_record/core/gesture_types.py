"""
手势类型定义

定义从触摸事件序列识别出的手势类型。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .event_types import TouchEvent, TouchDown, TouchUp, TouchMove


@dataclass
class Gesture:
    """手势基类"""

    start_time: float = field(default_factory=lambda: datetime.now().timestamp())
    end_time: float = field(default_factory=lambda: datetime.now().timestamp())
    duration: float = 0.0

    def __post_init__(self):
        """计算持续时间"""
        if self.end_time > self.start_time:
            self.duration = self.end_time - self.start_time

    @property
    def delay_before(self) -> float:
        """手势前的延迟时间（用于回放时保持时间间隔）"""
        return 0.0

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(duration={self.duration:.3f}s)"


@dataclass
class Tap(Gesture):
    """点击手势"""

    x: float = 0.0
    y: float = 0.0

    def __repr__(self) -> str:
        return (
            f"Tap(x={self.x:.1f}, y={self.y:.1f}, duration={self.duration:.3f}s, "
            f"delay={self.delay_before:.3f}s)"
        )


@dataclass
class Swipe(Gesture):
    """滑动手势"""

    start_x: float = 0.0
    start_y: float = 0.0
    end_x: float = 0.0
    end_y: float = 0.0

    @property
    def distance(self) -> float:
        """滑动距离（像素）"""
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y
        return (dx**2 + dy**2) ** 0.5

    @property
    def direction(self) -> str:
        """滑动方向"""
        dx = self.end_x - self.start_x
        dy = self.end_y - self.start_y

        if abs(dx) > abs(dy):
            return "right" if dx > 0 else "left"
        else:
            return "down" if dy > 0 else "up"

    def __repr__(self) -> str:
        return (
            f"Swipe({self.direction}, from=({self.start_x:.1f}, {self.start_y:.1f}), "
            f"to=({self.end_x:.1f}, {self.end_y:.1f}), duration={self.duration:.3f}s, "
            f"delay={self.delay_before:.3f}s)"
        )


@dataclass
class LongPress(Gesture):
    """长按手势"""

    x: float = 0.0
    y: float = 0.0
    min_duration: float = 0.5  # 最小长按时长（秒）

    def __repr__(self) -> str:
        return (
            f"LongPress(x={self.x:.1f}, y={self.y:.1f}, duration={self.duration:.3f}s, "
            f"delay={self.delay_before:.3f}s)"
        )


@dataclass
class Pinch(Gesture):
    """捏合/缩放手势（多指）"""

    center_x: float = 0.0
    center_y: float = 0.0
    start_distance: float = 0.0
    end_distance: float = 0.0

    @property
    def scale(self) -> float:
        """缩放比例"""
        if self.start_distance == 0:
            return 1.0
        return self.end_distance / self.start_distance

    def is_pinch_in(self) -> bool:
        """是否为捏合（缩小）"""
        return self.scale < 1.0

    def is_pinch_out(self) -> bool:
        """是否为张开（放大）"""
        return self.scale > 1.0

    def __repr__(self) -> str:
        direction = "out" if self.is_pinch_out() else "in"
        return (
            f"Pinch({direction}, center=({self.center_x:.1f}, {self.center_y:.1f}), "
            f"scale={self.scale:.2f}, duration={self.duration:.3f}s)"
        )
