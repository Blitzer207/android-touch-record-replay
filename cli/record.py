#!/usr/bin/env python3
"""
录制命令

录制 Android 设备的触摸操作并生成脚本。
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from touch_record.generator.adb_generator import AdbGenerator
from touch_record.generator.hybrid_generator import HybridGenerator
from touch_record.generator.u2_generator import U2Generator
from touch_record.recorder.batch_recorder import BatchRecorder
from touch_record.recorder.realtime_recorder import RealtimeRecorder
from touch_record.recorder.base_recorder import ListenerConfig


@click.command()
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["realtime", "batch"], case_sensitive=False),
    default="realtime",
    help="录制模式: realtime（实时生成）或 batch（批量生成）",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="输出文件路径（默认：./scripts/timestamp.py）",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["adb", "u2", "hybrid"], case_sensitive=False),
    default="hybrid",
    help="脚本格式: adb、u2（uiautomator2）或 hybrid（混合模式）",
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
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="显示详细输出",
)
def record(mode: str, output: Optional[str], format: str, device: Optional[str],
          duration: Optional[float], verbose: bool):
    """录制触摸操作并生成脚本

    示例:
      touch-record record                          # 使用默认设置录制
      touch-record record -o my_script.py         # 指定输出文件
      touch-record record -f adb -m batch -t 10    # ADB 格式，批量模式，录制10秒
    """
    click.echo(f"🎬 开始录制触摸操作...")
    click.echo(f"   模式: {mode}")
    click.echo(f"   格式: {format}")
    if device:
        click.echo(f"   设备: {device}")
    if duration:
        click.echo(f"   时长: {duration}秒")

    # 配置监听器
    config = ListenerConfig(adb_path="adb")

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
    generator_map = {
        "adb": AdbGenerator(),
        "u2": U2Generator(),
        "hybrid": HybridGenerator(),
    }
    generator = generator_map[format]

    # 选择录制器
    if mode == "realtime":
        recorder = RealtimeRecorder(config)
    else:
        recorder = BatchRecorder(config)

    # 收集手势
    gestures = []

    def on_gesture(gesture):
        """实时模式下的手势回调"""
        gestures.append(gesture)
        if verbose:
            click.echo(f"   ✨ {gesture}")

    try:
        recorder.start_recording()

        if duration:
            # 定时录制
            click.echo(f"\n⏳ 录制中，将在 {duration} 秒后自动停止...")
            click.echo("   按 Ctrl+C 立即停止\n")

            import time
            time.sleep(duration)
        else:
            # 手动停止
            click.echo("\n⏳ 录制中... 按 Ctrl+C 停止\n")

            if mode == "realtime":
                # 实时模式：持续监听直到手动停止
                try:
                    while True:
                        import time
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    pass
            else:
                # 批量模式：也支持手动停止
                try:
                    while True:
                        import time
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    pass

        # 停止录制
        recorder.stop_recording()

        if mode == "batch":
            # 批量模式获取识别的手势
            gestures = recorder.get_gestures()

    except KeyboardInterrupt:
        click.echo("\n\n⏹️  录制已停止")
        recorder.stop_recording()
        if mode == "batch":
            gestures = recorder.get_gestures()
    except Exception as e:
        click.echo(f"\n❌ 录制失败: {e}", err=True)
        sys.exit(1)

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
else:
    from cli.main import cli
    cli.add_command(record)
