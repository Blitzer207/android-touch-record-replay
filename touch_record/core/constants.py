"""
Android 输入事件常数定义

集中定义所有 Linux input subsystem 事件类型和事件码常数。
"""

# 事件类型 (Event Types)
EV_SYN = 0       # 同步事件
EV_KEY = 0x01    # 按键事件
EV_ABS = 3       # 绝对坐标事件

# EV_SYN 子码
SYN_REPORT = 0   # 同步报告

# EV_ABS 多点触控子码 (ABS_MT_*)
ABS_MT_SLOT          = 0x2F  # 触摸槽位
ABS_MT_TOUCH_MAJOR   = 0x30  # 触摸面积主轴
ABS_MT_POSITION_X    = 0x35  # X 坐标
ABS_MT_POSITION_Y    = 0x36  # Y 坐标
ABS_MT_TRACKING_ID   = 0x39  # 追踪 ID

# EV_ABS 单点触控子码
ABS_X = 0x00  # X 坐标（单点）
ABS_Y = 0x01  # Y 坐标（单点）
