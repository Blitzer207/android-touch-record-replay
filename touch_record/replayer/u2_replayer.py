"""
UIAutomator2 回放器

使用 uiautomator2 库回放手势。
"""

import time
from typing import List

from .base_replayer import BaseReplayer
from ..core.gesture_types import Gesture, LongPress, Swipe, Tap


class U2Replayer(BaseReplayer):
    """
    UIAutomator2 回放器

    使用 uiautomator2 API 执行手势操作
    """

    def __init__(self, speed: float = 1.0, adb_path: str = "adb"):
        super().__init__(speed, adb_path)
        self._device = None

    def _get_device(self):
        """获取设备连接（延迟初始化）"""
        if self._device is None:
            import uiautomator2 as u2

            self._device = u2.connect()
        return self._device

    def replay(self, gestures: List[Gesture]):
        """回放手势"""
        d = self._get_device()
        for gesture in gestures:
            self._replay_gesture(d, gesture)

    def replay_from_file(self, filename: str):
        """
        从文件回放手势

        直接执行脚本文件
        """
        import subprocess

        subprocess.run(["python3", filename], check=True)

    def _replay_gesture(self, device, gesture: Gesture):
        """回放单个手势"""
        if isinstance(gesture, Tap):
            self._replay_tap(device, gesture)
        elif isinstance(gesture, Swipe):
            self._replay_swipe(device, gesture)
        elif isinstance(gesture, LongPress):
            self._replay_longpress(device, gesture)

    def _replay_tap(self, device, gesture: Tap):
        """回放点击"""
        x = int(round(gesture.x))
        y = int(round(gesture.y))

        time.sleep(self.adjust_delay(gesture.delay_before))
        device.click(x, y)

    def _replay_swipe(self, device, gesture: Swipe):
        """回放滑动"""
        x1 = int(round(gesture.start_x))
        y1 = int(round(gesture.start_y))
        x2 = int(round(gesture.end_x))
        y2 = int(round(gesture.end_y))
        duration = gesture.duration / self.speed

        time.sleep(self.adjust_delay(gesture.delay_before))
        device.swipe(x1, y1, x2, y2, duration=duration)

    def _replay_longpress(self, device, gesture: LongPress):
        """回放长按"""
        x = int(round(gesture.x))
        y = int(round(gesture.y))
        duration = gesture.duration / self.speed

        time.sleep(self.adjust_delay(gesture.delay_before))
        device.long_click(x, y, duration=duration)


def replay_with_u2(
    gestures: List[Gesture],
    speed: float = 1.0,
    adb_path: str = "adb",
):
    """
    便捷函数：使用 uiautomator2 回放手势

    Args:
        gestures: 手势列表
        speed: 回放速度倍率
        adb_path: adb 命令路径
    """
    replayer = U2Replayer(speed=speed, adb_path=adb_path)
    replayer.replay(gestures)
