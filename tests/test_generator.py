"""
测试代码生成器
"""

import pytest

from touch_record.generator.adb_generator import AdbGenerator, generate_adb_script
from touch_record.generator.u2_generator import U2Generator, generate_u2_script
from touch_record.generator.hybrid_generator import HybridGenerator, generate_hybrid_script
from touch_record.gesture_types import LongPress, Swipe, Tap


class TestAdbGenerator:
    """测试 ADB 生成器"""

    def test_generate_tap(self):
        """测试生成点击代码"""
        generator = AdbGenerator()
        gesture = Tap(x=500, y=1000, duration=0.2, delay_before=0.5)

        code = generator.generate_gesture(gesture)

        assert "input tap 500 1000" in code
        assert "time.sleep(0.5)" in code

    def test_generate_swipe(self):
        """测试生成滑动代码"""
        generator = AdbGenerator()
        gesture = Swipe(
            start_x=100, start_y=500,
            end_x=900, end_y=500,
            duration=0.5, delay_before=0.3
        )

        code = generator.generate_gesture(gesture)

        assert "input swipe 100 500 900 500 500" in code
        assert "time.sleep(0.3)" in code

    def test_generate_longpress(self):
        """测试生成长按代码"""
        generator = AdbGenerator()
        gesture = LongPress(x=500, y=1000, duration=1.0, delay_before=0.2)

        code = generator.generate_gesture(gesture)

        # 长按通过原位滑动实现
        assert "input swipe 500 1000 500 1000" in code
        assert "time.sleep(0.2)" in code

    def test_generate_full_script(self):
        """测试生成完整脚本"""
        generator = AdbGenerator()
        gestures = [
            Tap(x=500, y=500, duration=0.2, delay_before=0.5),
            Swipe(start_x=100, start_y=500, end_x=900, end_y=500, duration=0.5, delay_before=0.3),
        ]

        script = generator.generate_script(gestures, "test.py")

        assert "import subprocess" in script
        assert "input tap 500 500" in script
        assert "input swipe 100 500 900 500" in script
        assert "touch-record-replay" in script


class TestU2Generator:
    """测试 UIAutomator2 生成器"""

    def test_generate_tap(self):
        """测试生成点击代码"""
        generator = U2Generator()
        gesture = Tap(x=500, y=1000, duration=0.2, delay_before=0.5)

        code = generator.generate_gesture(gesture)

        assert "d.click(500, 1000)" in code
        assert "time.sleep(0.5)" in code

    def test_generate_swipe(self):
        """测试生成滑动代码"""
        generator = U2Generator()
        gesture = Swipe(
            start_x=100, start_y=500,
            end_x=900, end_y=500,
            duration=0.5, delay_before=0.3
        )

        code = generator.generate_gesture(gesture)

        assert "d.swipe(100, 500, 900, 500" in code
        assert "duration=0.5" in code
        assert "time.sleep(0.3)" in code

    def test_generate_longpress(self):
        """测试生成长按代码"""
        generator = U2Generator()
        gesture = LongPress(x=500, y=1000, duration=1.0, delay_before=0.2)

        code = generator.generate_gesture(gesture)

        assert "d.long_click(500, 1000" in code
        assert "duration=1.0" in code
        assert "time.sleep(0.2)" in code

    def test_generate_full_script(self):
        """测试生成完整脚本"""
        generator = U2Generator()
        gestures = [
            Tap(x=500, y=500, duration=0.2, delay_before=0.5),
            Swipe(start_x=100, start_y=500, end_x=900, end_y=500, duration=0.5, delay_before=0.3),
        ]

        script = generator.generate_script(gestures, "test.py")

        assert "import uiautomator2 as u2" in script
        assert "d = u2.connect()" in script
        assert "d.click(500, 500)" in script
        assert "d.swipe(100, 500, 900, 500" in script


class TestHybridGenerator:
    """测试混合模式生成器"""

    def test_tap_uses_adb(self):
        """测试点击使用 ADB"""
        generator = HybridGenerator()
        gesture = Tap(x=500, y=500, duration=0.2)

        code = generator.generate_gesture(gesture)

        # 点击应该使用 subprocess (adb)
        assert "subprocess.run" in code
        assert "input tap" in code

    def test_short_swipe_uses_adb(self):
        """测试短滑动使用 ADB"""
        generator = HybridGenerator()
        # 短滑动（< 100px）
        gesture = Swipe(
            start_x=400, start_y=500,
            end_x=450, end_y=500,  # 50px
            duration=0.3
        )

        code = generator.generate_gesture(gesture)

        assert "subprocess.run" in code
        assert "input swipe" in code

    def test_long_swipe_uses_u2(self):
        """测试长滑动使用 U2"""
        generator = HybridGenerator()
        # 长滑动（> 100px）
        gesture = Swipe(
            start_x=100, start_y=500,
            end_x=900, end_y=500,  # 800px
            duration=0.5
        )

        code = generator.generate_gesture(gesture)

        assert "get_u2_device()" in code or "u2.connect()" in code
        assert ".swipe(" in code

    def test_long_press_uses_u2(self):
        """测试长按使用 U2"""
        generator = HybridGenerator()
        gesture = LongPress(x=500, y=500, duration=1.5)  # > 1s

        code = generator.generate_gesture(gesture)

        assert "get_u2_device()" in code or "u2.connect()" in code
        assert ".long_click(" in code

    def test_short_long_press_uses_adb(self):
        """测试短长按使用 ADB"""
        generator = HybridGenerator()
        gesture = LongPress(x=500, y=500, duration=0.6)  # < 1s

        code = generator.generate_gesture(gesture)

        assert "subprocess.run" in code
        assert "input swipe" in code

    def test_generate_full_script(self):
        """测试生成完整混合脚本"""
        generator = HybridGenerator()
        gestures = [
            Tap(x=500, y=500, duration=0.2, delay_before=0.1),  # ADB
            Swipe(start_x=100, start_y=500, end_x=900, end_y=500, duration=0.5),  # U2
        ]

        script = generator.generate_script(gestures, "test.py")

        assert "import subprocess" in script
        assert "import uiautomator2 as u2" in script
        assert "get_u2_device()" in script


def test_convenience_functions():
    """测试便捷函数"""
    gestures = [Tap(x=500, y=500, duration=0.2)]

    adb_script = generate_adb_script(gestures)
    assert "input tap" in adb_script

    u2_script = generate_u2_script(gestures)
    assert "d.click" in u2_script

    hybrid_script = generate_hybrid_script(gestures)
    assert "subprocess.run" in hybrid_script
