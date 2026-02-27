#!/usr/bin/env python3
"""
touch-record-replay 命令行入口

Android 触摸录制回放框架
"""

import click

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Android 触摸录制回放框架

    录制和回放 Android 设备的触摸操作。
    """
    pass


if __name__ == "__main__":
    cli()
