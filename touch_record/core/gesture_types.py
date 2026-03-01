"""
手势类型定义

定义从触摸事件序列识别出的手势类型。
"""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Gesture:
    """手势基类"""

    start_time: float = field(default_factory=lambda: datetime.now().timestamp())
    end_time: float = field(default_factory=lambda: datetime.now().timestamp())
    duration: float = 0.0
    delay_before: float = 0.0

    def __post_init__(self):
        """计算持续时间"""
        if self.end_time > self.start_time:
            self.duration = self.end_time - self.start_time


@dataclass
class Tap(Gesture):
    """点击手势"""

    x: float = 0.0
    y: float = 0.0


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


@dataclass
class LongPress(Gesture):
    """长按手势"""

    x: float = 0.0
    y: float = 0.0
