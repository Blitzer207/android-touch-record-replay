# 使用说明

## 快速开始

### 1. 安装

```bash
# 从源码安装
cd touch-record-replay
pip install -e .

# 或安装开发依赖
pip install -e ".[dev]"
```

### 2. 连接设备

确保设备已连接并启用 USB 调试：

```bash
# 检查设备连接
adb devices

# 如果使用 uiautomator2，需要初始化
python3 -m uiautomator2 init
```

### 3. 录制触摸操作

```bash
# 使用默认设置录制
touch-record record

# 指定输出文件
touch-record record -o my_script.py

# 录制指定时长
touch-record record -t 10

# 使用 ADB 格式
touch-record record -f adb

# 批量模式录制
touch-record record -m batch
```

录制过程中，在设备上进行触摸操作。按 Ctrl+C 停止录制。

### 4. 回放脚本

```bash
# 自动检测格式回放
touch-record replay my_script.py

# 指定后端
touch-record replay my_script.py --backend adb
touch-record replay my_script.py --backend u2

# 调整回放速度
touch-record replay my_script.py --speed 2.0

# 测试回放
touch-record replay-test my_script.py
```

## 命令参考

### record 命令

```bash
touch-record record [OPTIONS]

选项:
  -m, --mode [realtime|batch]  录制模式
  -o, --output PATH           输出文件路径
  -f, --format [adb|u2|hybrid] 脚本格式
  -d, --device TEXT           设备序列号
  -t, --duration FLOAT        录制时长（秒）
  -v, --verbose               显示详细输出
  --help                      显示帮助
```

### replay 命令

```bash
touch-record replay SCRIPT [OPTIONS]

选项:
  -b, --backend [auto|adb|u2]  回放后端
  -s, --speed FLOAT             回放速度倍率
  -v, --verbose                 显示详细输出
  --help                        显示帮助
```

### replay-test 命令

```bash
touch-record replay-test SCRIPT [OPTIONS]

选项:
  -b, --backend [auto|adb|u2]  回放后端
  -n, --dry-run                 模拟运行，不实际执行
  -v, --verbose                 显示详细输出
  --help                        显示帮助
```

## 配置文件

编辑 `config/default.yaml` 自定义默认设置：

```yaml
# 设备配置
device:
  serial: null          # 自动检测
  touch_device: null    # 自动检测

# 录制配置
recording:
  mode: realtime        # realtime | batch
  output: ./scripts
  format: hybrid       # adb | u2 | hybrid

# 手势识别阈值
gesture:
  tap_threshold: 10.0      # 点击最大移动距离（像素）
  tap_duration: 0.3        # 点击最大持续时间（秒）
  long_press_duration: 0.5  # 长按最小持续时间（秒）
  swipe_threshold: 50.0     # 滑动最小距离（像素）

# 回放配置
replay:
  backend: auto       # auto | adb | u2
  speed: 1.0          # 回放速度倍率
```

## 支持的手势

### 点击 (Tap)

快速点击屏幕某处。

```python
# ADB
subprocess.run("adb shell input tap 500 500", shell=True)

# u2
d.click(500, 500)
```

### 滑动 (Swipe)

从一个点滑动到另一个点。

```python
# ADB
subprocess.run("adb shell input swipe 100 500 900 500 500", shell=True)

# u2
d.swipe(100, 500, 900, 500, duration=0.5)
```

### 长按 (LongPress)

按住屏幕某处一段时间。

```python
# ADB（通过原位滑动实现）
subprocess.run("adb shell input swipe 500 500 500 500 1000", shell=True)

# u2
d.long_click(500, 500, duration=1.0)
```

## 脚本格式对比

| 特性 | ADB | UIAutomator2 | 混合模式 |
|------|-----|--------------|----------|
| 速度 | 快 | 中等 | 快 |
| 精确度 | 一般 | 高 | 高 |
| 依赖 | 无 | uiautomator2 | 可选 |
| 适用场景 | 简单操作 | 复杂操作 | 混合使用 |

### ADB 格式

- 优点：无需额外依赖，执行快
- 缺点：复杂操作精度较差
- 适用：简单的点击和短滑动

### UIAutomator2 格式

- 优点：精度高，功能丰富
- 缺点：需要安装依赖，速度稍慢
- 适用：长滑动、长按等复杂操作

### 混合模式

- 优点：结合两者优点
- 缺点：脚本稍复杂
- 适用：复杂操作序列

## 常见问题

### Q: 录制后没有检测到任何手势？

A: 检查以下事项：
1. 确认设备已连接并启用 USB 调试
2. 确认设备支持 `getevent` 命令
3. 尝试使用批量模式 (`-m batch`)
4. 使用 `-v` 参数查看详细输出

### Q: 回放时操作位置不准确？

A: 可能是坐标系转换问题：
1. 确保录制和回放使用同一设备
2. 检查设备屏幕分辨率是否变化
3. 尝试重新获取设备信息

### Q: UIAutomator2 无法连接？

A: 检查以下事项：
1. 安装 uiautomator2: `pip install uiautomator2`
2. 初始化设备: `python3 -m uiautomator2 init`
3. 确认设备已通过 ADB 连接

### Q: 如何调整手势识别的灵敏度？

A: 编辑配置文件中的 `gesture` 部分：
- `tap_threshold`: 点击的移动距离阈值（像素）
- `tap_duration`: 点击的时间阈值（秒）
- `long_press_duration`: 长按的时间阈值（秒）
- `swipe_threshold`: 滑动的距离阈值（像素）

## 示例

### 示例 1：录制并回放

```bash
# 录制 10 秒
touch-record record -t 10 -o demo.py

# 回放
touch-record replay demo.py
```

### 示例 2：批量模式录制

```bash
# 批量录制，录制 5 秒
touch-record record -m batch -t 5 -o batch.py
```

### 示例 3：生成指定格式的脚本

```bash
# 生成 ADB 格式脚本
touch-record record -f adb -o adb_script.py

# 生成 u2 格式脚本
touch-record record -f u2 -o u2_script.py
```

### 示例 4：高速回放

```bash
# 2 倍速回放
touch-record replay demo.py --speed 2.0

# 0.5 倍速（慢速）回放
touch-record replay demo.py --speed 0.5
```

## 扩展开发

### 添加新手势识别

在 `touch_record/core/gesture_types.py` 中定义新手势类：

```python
@dataclass
class DoubleTap(Gesture):
    """双击手势"""
    x: float = 0.0
    y: float = 0.0
    interval: float = 0.0  # 两次点击的间隔
```

然后在 `gesture_recognizer.py` 中实现识别逻辑。

### 添加新生成器

继承 `BaseGenerator` 类并实现抽象方法：

```python
class CustomGenerator(BaseGenerator):
    def generate_script(self, gestures, filename=None):
        # 实现脚本生成逻辑
        pass
```

## 许可证

MIT License
