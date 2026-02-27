"""
基础生成器接口

定义代码生成器的抽象基类。
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from ..core.gesture_types import Gesture


class BaseGenerator(ABC):
    """
    代码生成器抽象基类

    定义代码生成的通用接口。
    """

    def __init__(self, indent: str = "    ", delay_enabled: bool = True):
        self.indent = indent
        self.delay_enabled = delay_enabled

    @abstractmethod
    def generate_script(
        self,
        gestures: List[Gesture],
        filename: Optional[str] = None,
    ) -> str:
        """
        生成脚本

        Args:
            gestures: 手势列表
            filename: 输出文件名（可选，用于添加注释）

        Returns:
            生成的脚本内容
        """
        pass

    @abstractmethod
    def generate_imports(self) -> str:
        """生成导入语句"""
        pass

    @abstractmethod
    def generate_header(self, filename: Optional[str] = None) -> str:
        """生成脚本头部注释"""
        pass

    @abstractmethod
    def generate_footer(self) -> str:
        """生成脚本尾部"""
        pass

    @abstractmethod
    def generate_gesture(self, gesture: Gesture) -> str:
        """生成单个手势的代码"""
        pass

    def generate_gestures(self, gestures: List[Gesture]) -> str:
        """生成所有手势的代码"""
        lines = []
        for gesture in gestures:
            code = self.generate_gesture(gesture)
            if code:
                lines.append(code)
        return "\n".join(lines)

    def save_script(self, content: str, filename: str):
        """
        保存脚本到文件

        Args:
            content: 脚本内容
            filename: 文件名
        """
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

    def format_number(self, value: float, precision: int = 1) -> str:
        """格式化数字"""
        return f"{value:.{precision}f}"
