#!/usr/bin/env python3
"""
录制命令

录制 Android 设备的触摸操作并生成脚本。
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

from touch_record.generator.adb_generator import AdbGenerator
from touch_record.recorder.batch_recorder import BatchRecorder
from touch_record.core.event_listener import ListenerConfig


@click.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="输出文件路径（默认：./scripts/timestamp.py）",
)
@click.option(
    "--device",
    "-d",
    type=str,
    default=None,
    help="指定设备序列号",
)
@click.option(
    "--duration",
    "-t",
    type=float,
    default=None,
    help="录制时长（秒），不指定则手动停止（Ctrl+C）",
)
def record(output: Optional[str], device: Optional[str],
          duration: Optional[float]):
    """录制触摸操作并生成脚本

    示例:
      touch-record record                          # 使用默认设置录制
      touch-record record -o my_script.py         # 指定输出文件
      touch-record record -t 10                    # 录制10秒
    """
    click.echo(f"🎬 开始录制触摸操作...")

    # 配置监听器
    adb_path = f"adb -s {device}" if device else "adb"
    config = ListenerConfig(adb_path=adb_path)

    # 确定输出文件
    if output is None:
        output_dir = Path("./scripts")
        output_dir.mkdir(exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = str(output_dir / f"recording_{timestamp}.py")
        click.echo(f"   输出: {output}")

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 选择生成器
    generator = AdbGenerator(adb_path=adb_path)

    # 选择录制器
    recorder = BatchRecorder(config)

    # 开始录制
    recorder.start_recording()

    try:
        if duration:
            # 定时录制
            click.echo(f"\n⏳ 录制中，将在 {duration} 秒后自动停止...")
            click.echo("   按 Ctrl+C 立即停止\n")
            time.sleep(duration)
        else:
            # 手动停止
            click.echo("\n⏳ 录制中... 按 Ctrl+C 停止\n")
            while True:
                time.sleep(0.1)

    except KeyboardInterrupt:
        click.echo("\n\n⏹️  录制已停止")
    except Exception as e:
        click.echo(f"\n❌ 录制失败: {e}", err=True)
        sys.exit(1)
    finally:
        # 停止录制
        recorder.stop_recording()

    # 获取手势
    gestures = recorder.get_gestures()

    # 生成脚本
    if not gestures:
        click.echo("\n⚠️  未检测到任何手势操作")
        sys.exit(0)

    click.echo(f"\n📊 识别到 {len(gestures)} 个手势:")
    for i, gesture in enumerate(gestures, 1):
        click.echo(f"   {i}. {gesture}")

    # 生成并保存脚本
    script = generator.generate_script(gestures, filename=str(output_path))
    generator.save_script(script, str(output_path))

    click.echo(f"\n✅ 脚本已保存到: {output_path}")
    click.echo(f"\n💡 回放命令:")
    click.echo(f"   touch-record replay {output_path}")


# 将命令注册到主 CLI
if __name__ == "__main__":
    record()
