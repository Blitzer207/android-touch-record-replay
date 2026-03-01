"""
事件监听器

监听 Android 设备的 getevent 输出，捕获原始触摸事件。
"""

import queue
import re
import subprocess
from dataclasses import dataclass
from threading import Event, Thread
from typing import Generator, List, Optional

from .device_info import DeviceInfo, DeviceInfoCollector


@dataclass
class ListenerConfig:
    """监听器配置"""

    adb_path: str = "adb"
    device_path: Optional[str] = None  # 监听特定设备，None 表示自动检测
    buffer_size: int = 1000  # 事件队列缓冲大小


# SYN_REPORT 检测正则：匹配 "0000 0000" 前后有空格或在行尾
SYN_REPORT_PATTERN = re.compile(r'\s0000\s+0000(?:\s|$)')


class EventListener:
    """getevent 事件监听器"""

    def __init__(self, config: Optional[ListenerConfig] = None):
        self.config = config or ListenerConfig()
        self._queue: queue.Queue[str] = queue.Queue(self.config.buffer_size)
        self._stop_event = Event()
        self._thread: Optional[Thread] = None
        self._device_info: Optional[DeviceInfo] = None

    def start(self):
        """启动监听"""
        if self._thread and self._thread.is_alive():
            raise RuntimeError("Listener is already running")

        self._stop_event.clear()

        # 获取设备信息
        collector = DeviceInfoCollector(self.config.adb_path)
        self._device_info = collector.collect()

        # 确定要监听的设备
        device_path = self._get_device_path()

        # 构建命令
        cmd = self._build_command(device_path)

        # 启动监听线程
        self._thread = Thread(target=self._listen, args=(cmd,), daemon=True)
        self._thread.start()

    def stop(self):
        """停止监听"""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
            self._thread = None

    def _get_device_path(self) -> str:
        """获取要监听的设备路径"""
        if self.config.device_path:
            return self.config.device_path

        if self._device_info and self._device_info.touch_device:
            return self._device_info.touch_device.path

        # 监听所有设备
        return ""

    def _build_command(self, device_path: str) -> str:
        """构建 getevent 命令"""
        adb = self.config.adb_path

        if device_path:
            # 监听特定设备
            return f"{adb} shell getevent {device_path}"
        else:
            # 监听所有设备
            return f"{adb} shell getevent"

    def _listen(self, command: str):
        """监听事件（在独立线程中运行）"""
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # 行缓冲
        )

        try:
            while not self._stop_event.is_set():
                line = process.stdout.readline()
                if not line:
                    break

                line = line.strip()
                if line:
                    try:
                        self._queue.put_nowait(line)
                    except queue.Full:
                        # 队列满，丢弃旧事件
                        try:
                            self._queue.get_nowait()
                            self._queue.put_nowait(line)
                        except (queue.Empty, queue.Full):
                            pass
        except OSError:
            pass
        finally:
            process.terminate()
            process.wait()

    def read_line(self, timeout: float = 0.1) -> Optional[str]:
        """
        读取一行事件输出

        Args:
            timeout: 超时时间（秒）

        Returns:
            事件行，超时返回 None
        """
        try:
            return self._queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def lines(self, timeout: float = 0.1) -> Generator[str, None, None]:
        """
        生成器：持续读取事件行

        Args:
            timeout: 单次读取超时

        Yields:
            事件行
        """
        while not self._stop_event.is_set():
            line = self.read_line(timeout)
            if line is None:
                continue
            yield line

    @property
    def device_info(self) -> Optional[DeviceInfo]:
        """获取设备信息"""
        return self._device_info

    @property
    def is_running(self) -> bool:
        """是否正在运行"""
        return self._thread is not None and self._thread.is_alive()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()


class BufferedEventListener(EventListener):
    """缓冲事件监听器，收集所有事件"""

    def __init__(self, config: Optional[ListenerConfig] = None):
        super().__init__(config)
        self._buffer: List[str] = []

    def flush(self) -> List[str]:
        """刷新并返回所有缓冲的事件"""
        events = self._buffer.copy()
        self._buffer.clear()
        return events

    def collect_lines(self, timeout: float = 0.1) -> Generator[List[str], None, None]:
        """
        生成器：持续读取事件批次

        Yields:
            事件列表
        """
        while not self._stop_event.is_set():
            line = self.read_line(timeout)
            if line is None:
                # 超时，返回当前批次
                if self._buffer:
                    yield self.flush()
                continue

            self._buffer.append(line)

            # 遇到 SYN_REPORT 时返回批次
            if SYN_REPORT_PATTERN.search(line):
                if self._buffer:
                    yield self.flush()
