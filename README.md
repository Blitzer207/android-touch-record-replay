# Android 触摸录制回放框架

一套强大的 Android 触摸操作录制和回放框架，支持实时录制、多种后端和灵活的脚本生成。

## 功能特性

- 🎯 **实时录制** - 实时捕获触摸操作并转换为可执行脚本
- 🔌 **多后端支持** - 支持 adb、uiautomator2 和混合模式
- 👆 **手势识别** - 自动识别点击、滑动、长按等单指手势
- 🏗️ **可扩展架构** - 分层设计，便于添加多指手势等新功能
- ⏱️ **精确回放** - 保持原始时间间隔，实现真实的回放效果

## 安装

```bash
# 从源码安装
pip install -e .

# 或使用 pip（发布后）
pip install touch-record-replay
```

## 快速开始

### 录制触摸操作

```bash
# 录制到指定文件
touch-record record --output my_script.py

# 实时录制模式（默认）
touch-record record --mode realtime

# 批量录制模式
touch-record record --mode batch
```

### 回放脚本

```bash
# 使用 adb 后端回放
touch-record replay my_script.py --backend adb

# 使用 uiautomator2 后端回放
touch-record replay my_script.py --backend u2

# 调整回放速度
touch-record replay my_script.py --speed 1.5
```

### 测试回放

```bash
# 验证回放的正确性
touch-record replay-test my_script.py
```

## 项目结构

```
touch-record-replay/
├── touch_record/          # 核心模块
│   ├── core/              # 事件处理核心
│   ├── recorder/          # 录制模块
│   ├── generator/         # 代码生成器
│   ├── replayer/          # 回放模块
│   └── utils/             # 工具函数
├── cli/                   # 命令行工具
├── scripts/               # 生成的脚本
├── tests/                 # 测试
├── config/                # 配置文件
└── docs/                  # 文档
```

## 配置

编辑 `config/default.yaml` 自定义默认设置：

```yaml
device:
  serial: null  # 自动检测
  touch_device: null  # 自动检测

recording:
  mode: realtime  # realtime | batch
  output: ./scripts
  format: python  # python | json | yaml

replay:
  backend: adb  # adb | u2 | hybrid
  speed: 1.0

logging:
  level: INFO
  file: null
```

## 生成的脚本示例

### ADB 模式

```python
import time

time.sleep(0.5)
# adb shell input tap 500 500
time.sleep(0.3)
# adb shell input swipe 500 500 800 500 500
```

### UIAutomator2 模式

```python
import uiautomator2 as u2
import time

d = u2.connect()
time.sleep(0.5)
d.click(500, 500)
time.sleep(0.3)
d.swipe(500, 500, 800, 500, duration=0.5)
```

## 开发

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 代码格式化
black .
ruff check .
```

## 架构说明

框架采用分层架构设计：

1. **事件源层** - 使用 `getevent` 获取原始触摸事件
2. **核心层** - 解析事件并识别手势
3. **录制层** - 收集手势并生成脚本
4. **生成器层** - 将手势转换为特定后端的代码
5. **回放层** - 执行生成的脚本

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
