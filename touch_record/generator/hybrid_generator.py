"""
混合模式代码生成器

结合 adb 和 uiautomator2 的优点，简单操作用 adb，复杂操作用 u2。
"""

from typing import List, Optional

from .adb_generator import AdbGenerator
from .base_generator import BaseGenerator
from .u2_generator import U2Generator
from ..core.gesture_types import Gesture, LongPress, Swipe, Tap


class HybridGenerator(BaseGenerator):
    """
    混合模式代码生成器

    策略：
    - 点击：使用 adb（更快，无依赖）
    - 短滑动：使用 adb（更快）
    - 长滑动/长按：使用 uiautomator2（更精确）
    """

    # 滑动距离阈值，超过此值使用 u2
    SWIPE_THRESHOLD = 100.0
    # 长按时长阈值，超过此值使用 u2
    LONG_PRESS_THRESHOLD = 1.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._adb_generator = AdbGenerator(
            indent=self.indent, delay_enabled=self.delay_enabled
        )
        self._u2_generator = U2Generator(
            indent=self.indent, delay_enabled=self.delay_enabled
        )

    def generate_script(
        self,
        gestures: List[Gesture],
        filename: Optional[str] = None,
    ) -> str:
        """生成完整的混合模式脚本"""
        lines = []

        # 头部
        lines.append(self.generate_header(filename))
        lines.append("")

        # 导入（需要同时导入两个库）
        lines.append(self.generate_imports())
        lines.append("")

        # 设备连接（仅 u2 需要）
        lines.append(self._generate_device_connect())
        lines.append("")

        # 手势代码
        lines.append(self.generate_gestures(gestures))
        lines.append("")

        # 尾部
        lines.append(self.generate_footer())

        return "\n".join(lines)

    def generate_imports(self) -> str:
        """生成导入语句"""
        lines = [
            "import subprocess",
            "import uiautomator2 as u2",
            "",
            "# 初始化 uiautomator2（可选，仅在需要时连接）",
            "_d = None",
            "",
            "def get_u2_device():",
            '    """获取 u2 设备连接，延迟初始化"""',
            "    global _d",
            "    if _d is None:",
            "        _d = u2.connect()",
            "    return _d",
        ]
        return "\n".join(lines)

    def generate_header(self, filename: Optional[str] = None) -> str:
        """生成脚本头部"""
        lines = [
            '#!/usr/bin/env python3',
            '# -*- coding: utf-8 -*-',
            '#',
            '# Android 触摸操作回放脚本 (混合模式)',
            '# 由 touch-record-replay 生成',
        ]
        if filename:
            lines.append(f'# 文件名: {filename}')
        lines.append('#')
        lines.append('# 使用方法: python3 replay_script.py')
        lines.append('#')
        lines.append('# 混合模式说明:')
        lines.append('#   - 简单操作（点击、短滑动）使用 adb')
        lines.append('#   - 复杂操作（长滑动、长按）使用 uiautomator2')
        lines.append('#')
        lines.append('# 前置条件（仅使用 u2 操作时需要）:')
        lines.append('#   1. 安装 uiautomator2: pip install uiautomator2')
        lines.append('#   2. 连接设备: adb devices')
        lines.append('#   3. 初始化: python3 -m uiautomator2 init')
        lines.append('#')
        return "\n".join(lines)

    def generate_footer(self) -> str:
        """生成脚本尾部"""
        return "\n# 回放完成"

    def _generate_device_connect(self) -> str:
        """生成设备连接代码（注释说明）"""
        return f"{self.indent}# uiautomator2 设备连接在需要时自动初始化"

    def generate_gesture(self, gesture: Gesture) -> str:
        """生成单个手势的代码"""
        if isinstance(gesture, Tap):
            # 点击使用 adb
            return self._adb_generator._generate_tap(gesture)
        elif isinstance(gesture, Swipe):
            # 根据滑动距离选择后端
            if gesture.distance >= self.SWIPE_THRESHOLD:
                return self._generate_u2_swipe(gesture)
            else:
                return self._adb_generator._generate_swipe(gesture)
        elif isinstance(gesture, LongPress):
            # 根据时长选择后端
            if gesture.duration >= self.LONG_PRESS_THRESHOLD:
                return self._generate_u2_longpress(gesture)
            else:
                return self._adb_generator._generate_longpress(gesture)
        else:
            return f"# 未知手势类型: {gesture.__class__.__name__}"

    def _generate_u2_swipe(self, gesture: Swipe) -> str:
        """生成 u2 滑动代码"""
        x1 = int(round(gesture.start_x))
        y1 = int(round(gesture.start_y))
        x2 = int(round(gesture.end_x))
        y2 = int(round(gesture.end_y))
        duration = self.format_number(gesture.duration, 3)
        delay = self._generate_delay(gesture.delay_before)

        code = f"{self.indent}get_u2_device().swipe({x1}, {y1}, {x2}, {y2}, duration={duration})"
        return code + delay

    def _generate_u2_longpress(self, gesture: LongPress) -> str:
        """生成 u2 长按代码"""
        x = int(round(gesture.x))
        y = int(round(gesture.y))
        duration = self.format_number(gesture.duration, 3)
        delay = self._generate_delay(gesture.delay_before)

        code = f"{self.indent}get_u2_device().long_click({x}, {y}, duration={duration})"
        return code + delay

    def _generate_delay(self, delay: float) -> str:
        """生成延迟代码"""
        if delay <= 0 or not self.delay_enabled:
            return ""
        return f"\n{self.indent}time.sleep({self.format_number(delay, 3)})"


def generate_hybrid_script(
    gestures: List[Gesture],
    filename: Optional[str] = None,
    output_file: Optional[str] = None,
    swipe_threshold: float = 100.0,
    long_press_threshold: float = 1.0,
) -> str:
    """
    便捷函数：生成混合模式脚本

    Args:
        gestures: 手势列表
        filename: 脚本文件名（用于注释）
        output_file: 输出文件路径，如果提供则自动保存
        swipe_threshold: 滑动距离阈值，超过此值使用 u2
        long_press_threshold: 长按时长阈值，超过此值使用 u2

    Returns:
        生成的脚本内容
    """
    generator = HybridGenerator()
    generator.SWIPE_THRESHOLD = swipe_threshold
    generator.LONG_PRESS_THRESHOLD = long_press_threshold

    script = generator.generate_script(gestures, filename)

    if output_file:
        generator.save_script(script, output_file)

    return script
