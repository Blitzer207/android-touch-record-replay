#!/usr/bin/env python3
"""
回放测试命令

验证回放的正确性。
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
    "--dry-run",
    "-n",
    is_flag=True,
    help="模拟运行，不实际执行",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="显示详细输出",
)
def replay_test(script: str, backend: str, dry_run: bool, verbose: bool):
    """测试回放脚本的正确性

    SCRIPT: 要测试的脚本文件路径

    示例:
      touch-record replay-test my_script.py          # 完整测试
      touch-record replay-test my_script.py -n      # 模拟运行
    """
    script_path = Path(script)

    click.echo(f"🧪 测试脚本: {script_path.name}")

    # 检查文件格式
    content = script_path.read_text()

    # 自动检测后端
    if backend == "auto":
        if "import uiautomator2" in content or "u2.connect()" in content:
            backend = "u2"
        else:
            backend = "adb"

    click.echo(f"   格式: {backend}")

    # 检查脚本语法
    try:
        import ast
        ast.parse(content)
        click.echo("   ✅ 语法正确")
    except SyntaxError as e:
        click.echo(f"   ❌ 语法错误: {e}")
        sys.exit(1)

    # 检查必需的导入
    if backend == "u2":
        if "import uiautomator2" not in content:
            click.echo("   ⚠️  缺少 uiautomator2 导入")
    elif backend == "adb":
        if "import subprocess" not in content:
            click.echo("   ⚠️  缺少 subprocess 导入")

    # 检查是否有手势操作
    import re

    tap_count = len(re.findall(r"input tap|\.click\(|d\.click\(", content))
    swipe_count = len(re.findall(r"input swipe|\.swipe\(|d\.swipe\(", content))

    click.echo(f"   点击操作: {tap_count}")
    click.echo(f"   滑动操作: {swipe_count}")

    if tap_count == 0 and swipe_count == 0:
        click.echo("   ⚠️  未检测到任何触摸操作")

    if dry_run:
        click.echo("\n🎭 模拟运行模式 - 不会实际执行操作")
        return

    # 实际回放测试
    click.echo("\n▶️  开始实际回放测试...")
    click.echo("   警告: 这将在设备上执行操作！")
    click.echo("   按 Ctrl+C 立即停止\n")

    try:
        input("按 Enter 继续回放测试...")
    except KeyboardInterrupt:
        click.echo("\n\n⏹️  测试已取消")
        sys.exit(0)

    try:
        if backend == "adb":
            replayer = AdbReplayer()
        else:
            replayer = U2Replayer()

        replayer.replay_from_file(str(script_path))
        click.echo("\n✅ 回放测试完成")
    except KeyboardInterrupt:
        click.echo("\n\n⏹️  测试已停止")
    except Exception as e:
        click.echo(f"\n❌ 回放测试失败: {e}", err=True)
        sys.exit(1)


# 将命令注册到主 CLI
if __name__ == "__main__":
    replay_test()
else:
    from cli.main import cli
    cli.add_command(replay_test)
