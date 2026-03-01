#!/usr/bin/env python3
"""
touch-record-replay 命令行入口

Android 触摸录制回放框架
"""

import sys
from pathlib import Path

import click

# 添加项目路径（支持直接运行）
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.record import record
from cli.replay import replay


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Android 触摸录制回放框架

    录制和回放 Android 设备的触摸操作。
    """
    pass


# 注册子命令
cli.add_command(record)
cli.add_command(replay)


if __name__ == "__main__":
    cli()
