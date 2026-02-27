#!/usr/bin/env python3
"""
回放命令

回放录制的触摸操作脚本。
"""

import sys
from pathlib import Path

import click

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from touch_record.replayer.adb_replayer import AdbReplayer
from touch_record.replayer.u2_replayer import U2Replayer


@click.command()
@click.argument("script", type=click.Path(exists=True))
@click.option(
    "--backend",
    "-b",
    type=click.Choice(["auto", "adb", "u2"], case_sensitive=False),
    default="auto",
    help="回放后端: auto（自动检测）、adb 或 u2",
)
@click.option(
    "--speed",
    "-s",
    type=float,
    default=1.0,
    help="回放速度倍率（默认: 1.0）",
    show_default=True,
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="显示详细输出",
)
def replay(script: str, backend: str, speed: float, verbose: bool):
    """回放录制的触摸操作脚本

    SCRIPT: 要回放的脚本文件路径

    示例:
      touch-record replay my_script.py              # 自动检测后端
      touch-record replay my_script.py --backend adb  # 使用 ADB 后端
      touch-record replay my_script.py --speed 2.0    # 2倍速回放
    """
    script_path = Path(script)

    click.echo(f"▶️  回放脚本: {script_path.name}")
    click.echo(f"   速度: {speed}x")

    # 自动检测后端
    if backend == "auto":
        content = script_path.read_text()
        if "import uiautomator2" in content or "u2.connect()" in content:
            backend = "u2"
            click.echo(f"   后端: 自动检测为 u2")
        else:
            backend = "adb"
            click.echo(f"   后端: 自动检测为 adb")

    # 创建回放器
    if backend == "adb":
        replayer = AdbReplayer(speed=speed)
    elif backend == "u2":
        replayer = U2Replayer(speed=speed)

    # 尝试解析脚本文件获取手势信息
    try:
        from touch_record.recorder.batch_recorder import BatchRecorder
        from touch_record.core.event_parser import EventParser

        # 注意：这里简化处理，直接执行脚本
        # 实际应用中可以解析脚本内容提取手势信息
        pass
    except Exception:
        pass

    click.echo("\n⏳ 开始回放...")
    click.echo("   按 Ctrl+C 停止\n")

    try:
        replayer.replay_from_file(str(script_path))
        click.echo("\n✅ 回放完成")
    except KeyboardInterrupt:
        click.echo("\n\n⏹️  回放已停止")
    except Exception as e:
        click.echo(f"\n❌ 回放失败: {e}", err=True)
        sys.exit(1)


# 将命令注册到主 CLI
if __name__ == "__main__":
    replay()
else:
    from cli.main import cli
    cli.add_command(replay)
