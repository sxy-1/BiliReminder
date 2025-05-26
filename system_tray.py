"""
系统托盘模块

提供系统托盘图标的创建和管理功能。
"""

import threading
from typing import List, Tuple, Callable, Optional
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from abc import ABC, abstractmethod


class TrayIconInterface(ABC):
    """托盘图标接口"""

    @abstractmethod
    def start(self) -> None:
        """启动托盘图标"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """停止托盘图标"""
        pass

    @abstractmethod
    def add_menu_item(self, label: str, action: Callable) -> None:
        """添加菜单项"""
        pass


class SystemTray(TrayIconInterface):
    """系统托盘类

    管理系统托盘图标和右键菜单。
    """

    def __init__(
        self,
        app_name: str = "BiliReminder",
        icon_size: Tuple[int, int] = (64, 64),
        icon_colors: Tuple[str, str] = ("black", "red"),
    ):
        """初始化系统托盘

        Args:
            app_name: 应用程序名称
            icon_size: 图标大小 (width, height)
            icon_colors: 图标颜色 (color1, color2)
        """
        self.app_name = app_name
        self.icon_size = icon_size
        self.icon_colors = icon_colors

        self.icon: Optional[pystray.Icon] = None
        self.menu_items: List[pystray.MenuItem] = []
        self.tray_thread: Optional[threading.Thread] = None
        self.is_running = False

        # 创建默认退出菜单
        self.add_menu_item("退出", self._default_exit_action)

    def _create_icon_image(self) -> Image.Image:
        """创建托盘图标图像

        Returns:
            PIL图像对象
        """
        width, height = self.icon_size
        color1, color2 = self.icon_colors

        image = Image.new("RGB", (width, height), color1)
        draw = ImageDraw.Draw(image)

        # 绘制简单的棋盘图案
        draw.rectangle((width // 2, 0, width, height // 2), fill=color2)
        draw.rectangle((0, height // 2, width // 2, height), fill=color2)

        return image

    def add_menu_item(self, label: str, action: Callable) -> None:
        """添加菜单项

        Args:
            label: 菜单项标签
            action: 菜单项点击回调函数
        """
        menu_item = item(label, action)
        self.menu_items.append(menu_item)

    def _default_exit_action(self, icon, item_obj) -> None:
        """默认退出操作"""
        self.stop()

    def start(self) -> None:
        """启动托盘图标"""
        if self.is_running:
            return

        image = self._create_icon_image()
        menu = tuple(self.menu_items)

        self.icon = pystray.Icon(self.app_name, image, self.app_name, menu)

        # 在单独线程中运行托盘
        self.tray_thread = threading.Thread(target=self._run_tray, daemon=True)
        self.is_running = True
        self.tray_thread.start()

    def _run_tray(self) -> None:
        """运行托盘图标"""
        if self.icon:
            self.icon.run()

    def stop(self) -> None:
        """停止托盘图标"""
        if self.icon and self.is_running:
            self.is_running = False
            self.icon.stop()

    def is_alive(self) -> bool:
        """检查托盘是否运行中

        Returns:
            是否运行中
        """
        return self.is_running and (
            self.tray_thread is not None and self.tray_thread.is_alive()
        )


class TrayManager:
    """托盘管理器

    提供更高级的托盘管理功能。
    """

    def __init__(self, app_name: str = "BiliReminder"):
        """初始化托盘管理器

        Args:
            app_name: 应用程序名称
        """
        self.app_name = app_name
        self.tray: Optional[SystemTray] = None
        self.exit_callbacks: List[Callable] = []

    def create_tray(self, **kwargs) -> SystemTray:
        """创建托盘

        Args:
            **kwargs: 托盘初始化参数

        Returns:
            系统托盘对象
        """
        if self.tray is not None:
            self.tray.stop()

        self.tray = SystemTray(self.app_name, **kwargs)

        # 重写退出操作
        self.tray.menu_items.clear()  # 清除默认退出菜单
        self.tray.add_menu_item("退出", self._handle_exit)

        return self.tray

    def add_exit_callback(self, callback: Callable) -> None:
        """添加退出回调函数

        Args:
            callback: 退出时调用的函数
        """
        self.exit_callbacks.append(callback)

    def _handle_exit(self, icon, item_obj) -> None:
        """处理退出操作"""
        # 执行所有退出回调
        for callback in self.exit_callbacks:
            try:
                callback()
            except Exception as e:
                print(f"退出回调执行出错: {e}")

        # 停止托盘
        if self.tray:
            self.tray.stop()

    def start(self) -> None:
        """启动托盘"""
        if self.tray:
            self.tray.start()

    def stop(self) -> None:
        """停止托盘"""
        if self.tray:
            self.tray.stop()
