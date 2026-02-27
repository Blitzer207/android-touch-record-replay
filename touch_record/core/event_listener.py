"""
事件监听器

监听 Android 设备的 getevent 输出，实时捕获原始触摸事件。
"""

import subprocess
from dataclasses import dataclass
from datetime import datetime
from queue import Empty, Queue
from threading import Event, Thread
from typing import Callable, Generator, List, Optional

from .device_info import DeviceInfo, DeviceInfoCollector


@dataclass
class ListenerConfig:
    """监听器配置"""

    adb_path: str = "adb"
    device_path: Optional[str] = None  # 监听特定设备，None 表示自动检测
    filter_touch_only: bool = True  # 只监听触摸事件
    buffer_size: int = 1000  # 事件队列缓冲大小


class EventListener:
    """getevent 事件监听器"""

    def __init__(self, config: Optional[ListenerConfig] = None):
        self.config = config or ListenerConfig()
        self._queue: Queue[str] = Queue(self.config.buffer_size)
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

        if self.config.filter_touch_only and self._device_info:
            touch_device = self._device_info.touch_device
            if touch_device:
                return touch_device.path

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
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # 行缓冲
            )

            while not self._stop_event.is_set():
                line = process.stdout.readline()
                if not line:
                    break

                line = line.strip()
                if line:
                    try:
                        self._queue.put_nowait(line)
                    except:
                        # 队列满，丢弃旧事件
                        try:
                            self._queue.get_nowait()
                            self._queue.put_nowait(line)
                        except:
                            pass

        except Exception as e:
            # 忽略异常，正常停止时会有错误
            pass
        finally:
            if hasattr(process, "terminate"):
                process.terminate()

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
        except Empty:
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

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()


class CallbackEventListener(EventListener):
    """支持回调的事件监听器"""

    def __init__(
        self,
        config: Optional[ListenerConfig] = None,
        on_event: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
    ):
        super().__init__(config)
        self._on_event = on_event
        self._on_error = on_error
        self._callback_thread: Optional[Thread] = None

    def start(self):
        """启动监听"""
        super().start()
        self._stop_event.clear()
        self._callback_thread = Thread(target=self._callback_loop, daemon=True)
        self._callback_thread.start()

    def stop(self):
        """停止监听"""
        self._stop_event.set()
        if self._callback_thread:
            self._callback_thread.join(timeout=2)
            self._callback_thread = None
        super().stop()

    def _callback_loop(self):
        """回调循环"""
        try:
            for line in self.lines():
                if self._on_event:
                    try:
                        self._on_event(line)
                    except Exception as e:
                        if self._on_error:
                            self._on_error(e)
        except Exception as e:
            if self._on_error:
                self._on_error(e)


class BufferedEventListener(EventListener):
    """缓冲事件监听器，按批次读取事件"""

    def __init__(self, config: Optional[ListenerConfig] = None):
        super().__init__(config)
        self._buffer: List[str] = []
        self._last_flush_time = datetime.now().timestamp()

    def flush(self) -> List[str]:
        """刷新并返回所有缓冲的事件"""
        events = self._buffer.copy()
        self._buffer.clear()
        return events

    def lines(self, timeout: float = 0.1) -> Generator[List[str], None, None]:
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
            if "0000 0000" in line:
                if self._buffer:
                    yield self.flush()


def listen_events(
    config: Optional[ListenerConfig] = None,
    callback: Optional[Callable[[str], None]] = None,
) -> EventListener:
    """
    便捷函数：创建并启动事件监听器

    Args:
        config: 监听器配置
        callback: 事件回调函数

    Returns:
        事件监听器
    """
    if callback:
        listener = CallbackEventListener(config, on_event=callback)
    else:
        listener = EventListener(config)

    listener.start()
    return listener
