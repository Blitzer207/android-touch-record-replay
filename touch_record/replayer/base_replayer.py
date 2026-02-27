"""
基础回放器接口

定义回放器的抽象基类。
"""

from abc import ABC, abstractmethod
from typing import List

from ..core.gesture_types import Gesture


class BaseReplayer(ABC):
    """
    回放器抽象基类

    定义回放的通用接口。
    """

    def __init__(self, speed: float = 1.0, adb_path: str = "adb"):
        self.speed = speed
        self.adb_path = adb_path

    @abstractmethod
    def replay(self, gestures: List[Gesture]):
        """
        回放手势

        Args:
            gestures: 手势列表
        """
        pass

    @abstractmethod
    def replay_from_file(self, filename: str):
        """
        从文件回放手势

        Args:
            filename: 脚本文件名
        """
        pass

    def adjust_delay(self, delay: float) -> float:
        """根据速度调整延迟"""
        return delay / self.speed

    def execute_with_delay(self, action, delay: float):
        """
        执行操作并延迟

        Args:
            action: 要执行的可调用对象
            delay: 延迟时间（秒）
        """
        import time

        action()
        if delay > 0:
            time.sleep(self.adjust_delay(delay))
