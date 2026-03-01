"""
ADB 代码生成器

生成使用 adb shell input 命令的脚本。
"""

from typing import List, Optional

from ..core.gesture_types import Gesture, LongPress, Swipe, Tap


class AdbGenerator:
    """
    ADB 代码生成器

    使用 adb shell input 命令：
    - 点击: adb shell input tap x y
    - 滑动: adb shell input swipe x1 y1 x2 y2 [duration]
    - 长按: adb shell input swipe x1 y1 x1 y1 duration
    """

    def __init__(self, indent: str = "    ", delay_enabled: bool = True, adb_path: str = "adb"):
        self.indent = indent
        self.delay_enabled = delay_enabled
        self.adb_path = adb_path

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
        lines.append("import subprocess")
        lines.append("import time")

        # 主函数
        lines.append("def main():")
        lines.append(self.generate_gestures(gestures))
        lines.append("")
        lines.append("")
        lines.append("if __name__ == \"__main__\":")
        lines.append("    main()")
        lines.append("")

        # 尾部
        lines.append("# 回放完成")

        return "\n".join(lines)

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
        lines.append('')
        lines.append(f'ADB_PATH = "{self.adb_path}"')
        return "\n".join(lines)

    def generate_gestures(self, gestures: List[Gesture]) -> str:
        """生成所有手势的代码"""
        lines = []
        for gesture in gestures:
            code = self.generate_gesture(gesture)
            if code:
                lines.append(code)
        return "\n".join(lines)

    def generate_gesture(self, gesture: Gesture) -> str:
        """生成单个手势的代码"""
        if isinstance(gesture, Tap):
            return self._generate_tap(gesture)
        elif isinstance(gesture, Swipe):
            return self._generate_swipe(gesture)
        elif isinstance(gesture, LongPress):
            return self._generate_longpress(gesture)
        return ""

    def _generate_delay(self, delay: float) -> str:
        """生成延迟代码"""
        if delay <= 0 or not self.delay_enabled:
            return ""
        return f"{self.indent}time.sleep({delay:.3f})"

    def _generate_tap(self, gesture: Tap) -> str:
        """生成点击代码"""
        x = int(round(gesture.x))
        y = int(round(gesture.y))
        delay = self._generate_delay(gesture.delay_before)
        code = f'{self.indent}subprocess.run(f"{{ADB_PATH}} shell input tap {x} {y}", shell=True)'
        if delay:
            return delay + "\n" + code
        return code

    def _generate_swipe(self, gesture: Swipe) -> str:
        """生成滑动代码"""
        x1 = int(round(gesture.start_x))
        y1 = int(round(gesture.start_y))
        x2 = int(round(gesture.end_x))
        y2 = int(round(gesture.end_y))
        duration_ms = int(gesture.duration * 1000)
        delay = self._generate_delay(gesture.delay_before)
        code = (
            f'{self.indent}subprocess.run(f"{{ADB_PATH}} shell input swipe '
            f'{x1} {y1} {x2} {y2} {duration_ms}", shell=True)'
        )
        if delay:
            return delay + "\n" + code
        return code

    def _generate_longpress(self, gesture: LongPress) -> str:
        """生成长按代码"""
        x = int(round(gesture.x))
        y = int(round(gesture.y))
        duration_ms = int(gesture.duration * 1000)
        delay = self._generate_delay(gesture.delay_before)
        code = (
            f'{self.indent}subprocess.run(f"{{ADB_PATH}} shell input swipe '
            f'{x} {y} {x} {y} {duration_ms}", shell=True)'
        )
        if delay:
            return delay + "\n" + code
        return code

    def save_script(self, content: str, filename: str):
        """保存脚本到文件"""
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)


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
