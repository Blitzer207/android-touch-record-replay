"""
ADB 代码生成器

生成使用 adb shell input 命令的脚本。
"""

from typing import List, Optional

from .base_generator import BaseGenerator
from ..core.gesture_types import Gesture, LongPress, Swipe, Tap


class AdbGenerator(BaseGenerator):
    """
    ADB 代码生成器

    使用 adb shell input 命令：
    - 点击: adb shell input tap x y
    - 滑动: adb shell input swipe x1 y1 x2 y2 [duration]
    - 长按: adb shell input swipe x1 y1 x1 y1 duration
    """

    def generate_script(
        self,
        gestures: List[Gesture],
        filename: Optional[str] = None,
    ) -> str:
        """生成完整的 ADB 脚本"""
        lines = []

        # 头部
        lines.append(self.generate_header(filename))
        lines.append("")

        # 导入
        lines.append(self.generate_imports())
        lines.append("")

        # 手势代码
        lines.append(self.generate_gestures(gestures))
        lines.append("")

        # 尾部
        lines.append(self.generate_footer())

        return "\n".join(lines)

    def generate_imports(self) -> str:
        """生成导入语句"""
        return "import subprocess"
        # return "import subprocess\nimport time"

    def generate_header(self, filename: Optional[str] = None) -> str:
        """生成脚本头部"""
        lines = [
            '#!/usr/bin/env python3',
            '# -*- coding: utf-8 -*-',
            '#',
            '# Android 触摸操作回放脚本',
            '# 由 touch-record-replay 生成',
        ]
        if filename:
            lines.append(f'# 文件名: {filename}')
        lines.append('#')
        lines.append('# 使用方法: python3 replay_script.py')
        lines.append('#')
        return "\n".join(lines)

    def generate_footer(self) -> str:
        """生成脚本尾部"""
        return "\n# 回放完成"

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

        code = f'{self.indent}subprocess.run("adb shell input tap {x} {y}", shell=True)'
        return code + delay

    def _generate_swipe(self, gesture: Swipe) -> str:
        """生成滑动代码"""
        x1 = int(round(gesture.start_x))
        y1 = int(round(gesture.start_y))
        x2 = int(round(gesture.end_x))
        y2 = int(round(gesture.end_y))
        duration_ms = int(gesture.duration * 1000)
        delay = self._generate_delay(gesture.delay_before)

        code = (
            f'{self.indent}subprocess.run("adb shell input swipe '
            f'{x1} {y1} {x2} {y2} {duration_ms}", shell=True)'
        )
        return code + delay

    def _generate_longpress(self, gesture: LongPress) -> str:
        """生成长按代码"""
        # 长按通过原位滑动实现
        x = int(round(gesture.x))
        y = int(round(gesture.y))
        duration_ms = int(gesture.duration * 1000)
        delay = self._generate_delay(gesture.delay_before)

        code = (
            f'{self.indent}subprocess.run("adb shell input swipe '
            f'{x} {y} {x} {y} {duration_ms}", shell=True)'
        )
        return code + delay


def generate_adb_script(
    gestures: List[Gesture],
    filename: Optional[str] = None,
    output_file: Optional[str] = None,
) -> str:
    """
    便捷函数：生成 ADB 脚本

    Args:
        gestures: 手势列表
        filename: 脚本文件名（用于注释）
        output_file: 输出文件路径，如果提供则自动保存

    Returns:
        生成的脚本内容
    """
    generator = AdbGenerator()
    script = generator.generate_script(gestures, filename)

    if output_file:
        generator.save_script(script, output_file)

    return script
