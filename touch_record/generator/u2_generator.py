"""
UIAutomator2 代码生成器

生成使用 uiautomator2 库的脚本。
"""

from typing import List, Optional

from .base_generator import BaseGenerator
from ..core.gesture_types import Gesture, LongPress, Swipe, Tap


class U2Generator(BaseGenerator):
    """
    UIAutomator2 代码生成器

    使用 uiautomator2 API：
    - 点击: d.click(x, y)
    - 滑动: d.swipe(x1, y1, x2, y2, duration)
    - 长按: d.long_click(x, y, duration)
    """

    def generate_script(
        self,
        gestures: List[Gesture],
        filename: Optional[str] = None,
    ) -> str:
        """生成完整的 uiautomator2 脚本"""
        lines = []

        # 头部
        lines.append(self.generate_header(filename))
        lines.append("")

        # 导入
        lines.append(self.generate_imports())
        lines.append("")

        # 设备连接
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
        return "import uiautomator2 as u2"
        # return "import uiautomator2 as u2\nimport time"

    def generate_header(self, filename: Optional[str] = None) -> str:
        """生成脚本头部"""
        lines = [
            '#!/usr/bin/env python3',
            '# -*- coding: utf-8 -*-',
            '#',
            '# Android 触摸操作回放脚本 (uiautomator2)',
            '# 由 touch-record-replay 生成',
        ]
        if filename:
            lines.append(f'# 文件名: {filename}')
        lines.append('#')
        lines.append('# 使用方法: python3 replay_script.py')
        lines.append('#')
        lines.append('# 前置条件:')
        lines.append('#   1. 安装 uiautomator2: pip install uiautomator2')
        lines.append('#   2. 连接设备: adb devices')
        lines.append('#   3. 初始化: python3 -m uiautomator2 init')
        lines.append('#')
        return "\n".join(lines)

    def generate_footer(self) -> str:
        """生成脚本尾部"""
        return "\n# 回放完成"

    def _generate_device_connect(self) -> str:
        """生成设备连接代码"""
        return f"{self.indent}d = u2.connect()"

    def generate_gesture(self, gesture: Gesture) -> str:
        """生成单个手势的代码"""
        if isinstance(gesture, Tap):
            return self._generate_tap(gesture)
        elif isinstance(gesture, Swipe):
            return self._generate_swipe(gesture)
        elif isinstance(gesture, LongPress):
            return self._generate_longpress(gesture)
        else:
            return f"# 未知手势类型: {gesture.__class__.__name__}"

    def _generate_delay(self, delay: float) -> str:
        """生成延迟代码"""
        if delay <= 0 or not self.delay_enabled:
            return ""
        return f"\n{self.indent}time.sleep({self.format_number(delay, 3)})"

    def _generate_tap(self, gesture: Tap) -> str:
        """生成点击代码"""
        x = int(round(gesture.x))
        y = int(round(gesture.y))
        delay = self._generate_delay(gesture.delay_before)

        code = f"{self.indent}d.click({x}, {y})"
        return code + delay

    def _generate_swipe(self, gesture: Swipe) -> str:
        """生成滑动代码"""
        x1 = int(round(gesture.start_x))
        y1 = int(round(gesture.start_y))
        x2 = int(round(gesture.end_x))
        y2 = int(round(gesture.end_y))
        duration = self.format_number(gesture.duration, 3)
        delay = self._generate_delay(gesture.delay_before)

        code = f"{self.indent}d.swipe({x1}, {y1}, {x2}, {y2}, duration={duration})"
        return code + delay

    def _generate_longpress(self, gesture: LongPress) -> str:
        """生成长按代码"""
        x = int(round(gesture.x))
        y = int(round(gesture.y))
        duration = self.format_number(gesture.duration, 3)
        delay = self._generate_delay(gesture.delay_before)

        # 使用 long_click 方法（u2 支持）
        code = f"{self.indent}d.long_click({x}, {y}, duration={duration})"
        return code + delay


def generate_u2_script(
    gestures: List[Gesture],
    filename: Optional[str] = None,
    output_file: Optional[str] = None,
) -> str:
    """
    便捷函数：生成 uiautomator2 脚本

    Args:
        gestures: 手势列表
        filename: 脚本文件名（用于注释）
        output_file: 输出文件路径，如果提供则自动保存

    Returns:
        生成的脚本内容
    """
    generator = U2Generator()
    script = generator.generate_script(gestures, filename)

    if output_file:
        generator.save_script(script, output_file)

    return script
