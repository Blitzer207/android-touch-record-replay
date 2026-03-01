"""
设备信息处理

获取 Android 设备的输入设备信息和屏幕分辨率，处理坐标系转换。
"""

import re
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .constants import (
    EV_ABS,
    EV_KEY,
    ABS_MT_POSITION_X,
    ABS_MT_POSITION_Y,
    ABS_X,
    ABS_Y,
)


@dataclass
class InputDevice:
    """输入设备信息"""

    name: str = ""
    path: str = ""
    is_touch: bool = False
    is_keyboard: bool = False
    is_mouse: bool = False
    max_x: int = 0
    max_y: int = 0

    def __repr__(self) -> str:
        return (
            f"InputDevice(name='{self.name}', path='{self.path}', "
            f"is_touch={self.is_touch})"
        )


@dataclass
class DeviceInfo:
    """Android 设备信息"""

    serial: str = ""
    screen_width: int = 0
    screen_height: int = 0
    touch_device: Optional[InputDevice] = None
    touch_devices: List[InputDevice] = field(default_factory=list)
    device_map: Dict[str, InputDevice] = field(default_factory=dict)

    def __repr__(self) -> str:
        return (
            f"DeviceInfo(serial='{self.serial}', "
            f"screen=({self.screen_width}x{self.screen_height}), "
            f"touch_device={self.touch_device})"
        )


class DeviceInfoCollector:
    """设备信息收集器"""

    # 触摸设备常见名称模式
    TOUCH_PATTERNS = [
        r"touch",
        r"ts",
        r"ft5x0",
        r"goodix",
        r"focaltech",
        r"synaptics",
        r"atmel",
        r"elan",
    ]

    # getevent 事件类型码
    EV_ABS = 0x03
    EV_KEY = 0x01
    ABS_MT_POSITION_X = 0x35
    ABS_MT_POSITION_Y = 0x36
    ABS_X = 0x00
    ABS_Y = 0x01

    def __init__(self, adb_path: str = "adb"):
        self.adb_path = adb_path
        self._device_info: Optional[DeviceInfo] = None

    def collect(self) -> DeviceInfo:
        """收集设备信息"""
        if self._device_info is None:
            self._device_info = DeviceInfo()

            # 获取设备序列号
            self._device_info.serial = self._get_device_serial()

            # 获取屏幕分辨率
            self._device_info.screen_width, self._device_info.screen_height = (
                self._get_screen_resolution()
            )

            # 获取输入设备信息
            self._parse_input_devices()

        return self._device_info

    def _run_adb_command(self, command: str) -> str:
        """执行 adb 命令"""
        cmd = f"{self.adb_path} shell {command}"
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()

    def _get_device_serial(self) -> str:
        """获取设备序列号"""
        result = subprocess.run(
            f"{self.adb_path} get-serialno",
            shell=True,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip()

    def _get_screen_resolution(self) -> Tuple[int, int]:
        """获取屏幕分辨率"""
        output = self._run_adb_command("wm size")
        match = re.search(r"(\d+)x(\d+)", output)
        if match:
            return int(match.group(1)), int(match.group(2))

        # 备选方法：使用 dumpsys
        output = self._run_adb_command("dumpsys window displays")
        match = re.search(r"init=(\d+)x(\d+)", output)
        if match:
            return int(match.group(1)), int(match.group(2))

        return 0, 0

    def _parse_input_devices(self):
        """解析输入设备信息"""
        output = self._run_adb_command("getevent -p")

        # 使用 "add device" 作为分隔符
        # 这对模拟器和真机都适用
        blocks = []
        current_block = []

        for line in output.split("\n"):
            if line.startswith("add device"):
                # 新设备开始
                if current_block:
                    blocks.append("\n".join(current_block))
                current_block = [line]
            else:
                current_block.append(line)

        # 添加最后一个块
        if current_block:
            blocks.append("\n".join(current_block))

        # 解析每个设备块
        for block in blocks:
            if not block:
                continue

            device = self._parse_device_block(block)
            if device and device.path:
                self._device_info.device_map[device.path] = device
                self._device_info.touch_devices.append(device)

                if device.is_touch and self._device_info.touch_device is None:
                    self._device_info.touch_device = device

    def _parse_device_block(self, block: str) -> Optional[InputDevice]:
        """解析单个设备信息块"""
        lines = block.strip().split("\n")
        if not lines:
            return None

        device = InputDevice()

        # 第一行：设备路径和名称
        # 支持两种格式：
        # 格式1: /dev/input/event0:  name:     "xxx"
        # 格式2: add device 1: /dev/input/event0
        first_line = lines[0]

        # 尝试格式2 (模拟器使用此格式)
        match = re.search(r"add device \d+:\s*(/dev/input/event\d+)", first_line)
        if match:
            device.path = match.group(1)
            # 名称在下一行
            if len(lines) > 1:
                name_match = re.search(r'name:\s*"([^"]*)"', lines[1])
                if name_match:
                    device.name = name_match.group(1)
        else:
            # 尝试格式1 (真机使用此格式)
            match = re.search(r"^(/dev/input/event\d+):\s*(.+?)(?:\s|$)", first_line)
            if match:
                device.path = match.group(1)
                device.name = match.group(2)

        # 解析能力
        for line in lines[1:]:
            line = line.strip()

            # 检查是否为触摸设备
            if self._is_touch_capability(line):
                device.is_touch = True

            # 提取 X 轴最大值（支持名称和十六进制代码）
            # 名称格式: ABS_MT_POSITION_X : value 0, min 0, max 65535
            # 十六进制格式: 0000  : value 0, min 0, max 32767
            # 注意：需要非贪婪匹配十六进制代码后的数字
            x_match = re.search(r"(?:ABS_MT_POSITION_X|0000)\s*:\s*value \d+, min \d+, max (\d+)", line)
            if x_match:
                device.max_x = int(x_match.group(1))

            # 备选：ABS_X
            if device.max_x == 0:
                x_match = re.search(r"ABS_X\s*:\s*value \d+, min \d+, max (\d+)", line)
                if x_match:
                    device.max_x = int(x_match.group(1))

            # 提取 Y 轴最大值
            # 名称格式: ABS_MT_POSITION_Y : value 0, min 0, max 65535
            # 十六进制格式: 0001  : value 0, min 0, max 32767
            y_match = re.search(r"(?:ABS_MT_POSITION_Y|0001)\s*:\s*value \d+, min \d+, max (\d+)", line)
            if y_match:
                device.max_y = int(y_match.group(1))

            # 备选：ABS_Y
            if device.max_y == 0:
                y_match = re.search(r"ABS_Y\s*:\s*value \d+, min \d+, max (\d+)", line)
                if y_match:
                    device.max_y = int(y_match.group(1))

        # 通过设备名称判断
        if not device.is_touch:
            device.is_touch = self._is_touch_by_name(device.name)

        return device if device.path else None

    def _is_touch_capability(self, line: str) -> bool:
        """根据能力行判断是否为触摸设备"""
        # 检查是否有触摸相关事件类型
        if "EV_ABS" in line or "EV_KEY" in line:
            # 检查是否有 MT（Multi-Touch）能力
            if "ABS_MT" in line:
                return True
            # 检查是否有 BTN_TOUCH
            if "BTN_TOUCH" in line:
                return True

        return False

    def _is_touch_by_name(self, name: str) -> bool:
        """根据设备名称判断是否为触摸设备"""
        name_lower = name.lower()
        for pattern in self.TOUCH_PATTERNS:
            if re.search(pattern, name_lower):
                return True
        return False

    def get_device_by_path(self, path: str) -> Optional[InputDevice]:
        """根据路径获取设备信息"""
        info = self.collect()
        return info.device_map.get(path)

    def get_touch_device(self) -> Optional[InputDevice]:
        """获取触摸设备"""
        info = self.collect()
        return info.touch_device

    def convert_coordinates(
        self,
        x: int,
        y: int,
        from_device: Optional[InputDevice] = None,
    ) -> Tuple[float, float]:
        """
        坐标系转换：从设备输入坐标转换到屏幕坐标

        Args:
            x: 设备输入 X 坐标
            y: 设备输入 Y 坐标
            from_device: 设备信息（如果为 None，使用触摸设备）

        Returns:
            转换后的屏幕坐标 (screen_x, screen_y)
        """
        info = self.collect()

        if from_device is None:
            from_device = info.touch_device

        if not from_device:
            return float(x), float(y)

        # 如果设备最大坐标与屏幕分辨率相同，直接返回
        if from_device.max_x == info.screen_width and from_device.max_y == info.screen_height:
            return float(x), float(y)

        # 计算转换比例
        x_scale = info.screen_width / from_device.max_x if from_device.max_x > 0 else 1.0
        y_scale = info.screen_height / from_device.max_y if from_device.max_y > 0 else 1.0

        return float(x) * x_scale, float(y) * y_scale


def get_device_info(adb_path: str = "adb") -> DeviceInfo:
    """便捷函数：获取设备信息"""
    collector = DeviceInfoCollector(adb_path)
    return collector.collect()
