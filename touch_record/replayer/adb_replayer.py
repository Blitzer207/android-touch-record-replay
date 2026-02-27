"""
ADB 回放器

使用 adb shell input 命令回放手势。
"""

import subprocess
import time
from typing import List

from .base_replayer import BaseReplayer
from ..core.gesture_types import Gesture, LongPress, Swipe, Tap


class AdbReplayer(BaseReplayer):
    """
    ADB 回放器

    使用 adb shell input 命令执行手势操作
    """

    def replay(self, gestures: List[Gesture]):
        """回放手势"""
        for gesture in gestures:
            self._replay_gesture(gesture)

    def replay_from_file(self, filename: str):
        """
        从文件回放手势

        直接执行脚本文件
        """
        subprocess.run(["python3", filename], check=True)

    def _replay_gesture(self, gesture: Gesture):
        """回放单个手势"""
        if isinstance(gesture, Tap):
            self._replay_tap(gesture)
        elif isinstance(gesture, Swipe):
            self._replay_swipe(gesture)
        elif isinstance(gesture, LongPress):
            self._replay_longpress(gesture)

    def _replay_tap(self, gesture: Tap):
        """回放点击"""
        x = int(round(gesture.x))
        y = int(round(gesture.y))
        cmd = f"{self.adb_path} shell input tap {x} {y}"

        # 应用延迟
        time.sleep(self.adjust_delay(gesture.delay_before))
        subprocess.run(cmd, shell=True, check=True)

    def _replay_swipe(self, gesture: Swipe):
        """回放滑动"""
        x1 = int(round(gesture.start_x))
        y1 = int(round(gesture.start_y))
        x2 = int(round(gesture.end_x))
        y2 = int(round(gesture.end_y))
        duration_ms = int(gesture.duration * 1000)

        # 调整滑动时长
        duration_ms = int(duration_ms / self.speed)

        cmd = f"{self.adb_path} shell input swipe {x1} {y1} {x2} {y2} {duration_ms}"

        time.sleep(self.adjust_delay(gesture.delay_before))
        subprocess.run(cmd, shell=True, check=True)

    def _replay_longpress(self, gesture: LongPress):
        """回放长按"""
        x = int(round(gesture.x))
        y = int(round(gesture.y))
        duration_ms = int(gesture.duration * 1000)

        # 调整长按时长
        duration_ms = int(duration_ms / self.speed)

        # 长按通过原位滑动实现
        cmd = f"{self.adb_path} shell input swipe {x} {y} {x} {y} {duration_ms}"

        time.sleep(self.adjust_delay(gesture.delay_before))
        subprocess.run(cmd, shell=True, check=True)


def replay_with_adb(
    gestures: List[Gesture],
    speed: float = 1.0,
    adb_path: str = "adb",
):
    """
    便捷函数：使用 ADB 回放手势

    Args:
        gestures: 手势列表
        speed: 回放速度倍率
        adb_path: adb 命令路径
    """
    replayer = AdbReplayer(speed=speed, adb_path=adb_path)
    replayer.replay(gestures)
