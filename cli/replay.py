#!/usr/bin/env python3
"""
回放命令

回放录制的触摸操作脚本。
"""

import sys
from pathlib import Path

import click

from touch_record.replayer.adb_replayer import AdbReplayer


@click.command()
@click.argument("script", type=click.Path(exists=True))
@click.option(
    "--speed",
    "-s",
    type=float,
    default=1.0,
    help="回放速度倍率（默认: 1.0）",
    show_default=True,
)
def replay(script: str, speed: float):
    """回放录制的触摸操作脚本

    SCRIPT: 要回放的脚本文件路径

    示例:
      touch-record replay my_script.py              # 默认速度回放
      touch-record replay my_script.py --speed 2.0    # 2倍速回放
    """
    script_path = Path(script)

    click.echo(f"▶️  回放脚本: {script_path.name}")
    click.echo(f"   速度: {speed}x")

    # 创建回放器
    replayer = AdbReplayer(speed=speed)

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
