"""
配置文件

统一管理应用程序的配置参数。
"""

from typing import Dict, Any

# 应用程序配置
APP_CONFIG: Dict[str, Any] = {
    "name": "BiliReminder",
    "version": "1.0.0",
    "description": "哔哩哔哩提醒工具",
}

# 通知配置
NOTIFICATION_CONFIG: Dict[str, Any] = {
    "duration": 3000,  # 显示持续时间（毫秒）
    "width": 300,  # 窗口宽度
    "height": 60,  # 窗口高度
    "slide_speed": 5,  # 滑动速度
    "font_family": "Helvetica",
    "font_size": 16,
    "bg_color": "white",
    "text_color": "black",
}

# 托盘配置
TRAY_CONFIG: Dict[str, Any] = {"icon_size": (64, 64), "icon_colors": ("black", "red")}

# 定时器配置
TIMER_CONFIG: Dict[str, Any] = {
    "notification_interval": 30,  # 通知间隔（秒）
    "queue_check_interval": 100,  # 队列检查间隔（毫秒）
}
