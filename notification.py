"""
滑动通知模块

提供滑动通知窗口的实现，支持自定义样式和动画效果。
"""

import tkinter as tk
from typing import Optional, Callable
from abc import ABC, abstractmethod


class NotificationInterface(ABC):
    """通知接口，定义通知的基本行为"""

    @abstractmethod
    def show(self) -> None:
        """显示通知"""
        pass

    @abstractmethod
    def hide(self) -> None:
        """隐藏通知"""
        pass


class SlideNotification(tk.Toplevel, NotificationInterface):
    """滑动通知窗口类

    实现从屏幕顶部滑入的通知效果，支持自定义文本、持续时间、大小和动画速度。
    """

    def __init__(
        self,
        parent: tk.Tk,
        text: str,
        duration: int = 3000,
        width: int = 300,
        height: int = 60,
        slide_speed: int = 5,
        font_family: str = "Helvetica",
        font_size: int = 16,
        bg_color: str = "white",
        text_color: str = "black",
        on_close: Optional[Callable] = None,
    ):
        """初始化滑动通知窗口

        Args:
            parent: 父窗口
            text: 通知文本
            duration: 显示持续时间（毫秒）
            width: 窗口宽度
            height: 窗口高度
            slide_speed: 滑动速度（像素/帧）
            font_family: 字体家族
            font_size: 字体大小
            bg_color: 背景颜色
            text_color: 文字颜色
            on_close: 关闭回调函数
        """
        super().__init__(parent)

        # 配置参数
        self.width = width
        self.height = height
        self.slide_speed = slide_speed
        self.duration = duration
        self.text = text
        self.on_close = on_close

        # 位置参数
        self.start_y = -self.height
        self.end_y = 50
        self.screen_width = self.winfo_screenwidth()

        # 初始化窗口
        self._setup_window()
        self._setup_content(font_family, font_size, bg_color, text_color)
        self._setup_dpi()

        # 标记窗口状态
        self._is_showing = False
        self._is_hiding = False

    def _setup_window(self) -> None:
        """设置窗口属性"""
        self.overrideredirect(True)  # 去除边框
        self.attributes("-topmost", True)  # 置顶显示

        # 设置初始位置（屏幕外）
        x_pos = (self.screen_width - self.width) // 2
        self.geometry(f"{self.width}x{self.height}+{x_pos}+{self.start_y}")

    def _setup_content(
        self, font_family: str, font_size: int, bg_color: str, text_color: str
    ) -> None:
        """设置窗口内容"""
        self.configure(bg=bg_color)

        self.label = tk.Label(
            self,
            text=self.text,
            fg=text_color,
            bg=bg_color,
            font=(font_family, font_size),
            wraplength=self.width - 20,
            justify="center",
        )
        self.label.pack(expand=True, fill="both")

    def _setup_dpi(self) -> None:
        """设置DPI以提高清晰度 (Windows)"""
        try:
            from ctypes import windll

            windll.user32.SetProcessDPIAware()
        except (ImportError, AttributeError):
            pass  # 非Windows系统或无法设置DPI

    def show(self) -> None:
        """显示通知"""
        if not self._is_showing:
            self._is_showing = True
            self.after(100, self._slide_down)

    def hide(self) -> None:
        """隐藏通知"""
        if not self._is_hiding:
            self._is_hiding = True
            self._slide_up()

    def _slide_down(self) -> None:
        """向下滑动动画"""
        if self._is_hiding:
            return

        current_y = self.winfo_y()
        if current_y < self.end_y:
            new_y = current_y + self.slide_speed
            self.geometry(f"{self.width}x{self.height}+{self.winfo_x()}+{new_y}")
            self.after(10, self._slide_down)
        else:
            # 滑动完成，开始计时自动隐藏
            self.after(self.duration, self.hide)

    def _slide_up(self) -> None:
        """向上滑动动画"""
        current_y = self.winfo_y()
        if current_y > -self.height:
            new_y = current_y - self.slide_speed
            self.geometry(f"{self.width}x{self.height}+{self.winfo_x()}+{new_y}")
            self.after(10, self._slide_up)
        else:
            # 滑动完成，销毁窗口
            self._on_destroy()

    def _on_destroy(self) -> None:
        """销毁窗口前的清理工作"""
        if self.on_close:
            self.on_close()
        self.destroy()


class NotificationManager:
    """通知管理器

    管理通知的显示和队列，避免通知重叠。
    """

    def __init__(self, parent: tk.Tk):
        """初始化通知管理器

        Args:
            parent: 父窗口
        """
        self.parent = parent
        self.current_notification: Optional[SlideNotification] = None
        self.notification_queue: list = []

    def show_notification(self, text: str, **kwargs) -> None:
        """显示通知

        Args:
            text: 通知文本
            **kwargs: 其他通知参数
        """
        if self.current_notification is not None:
            # 如果有正在显示的通知，加入队列
            self.notification_queue.append((text, kwargs))
            return

        # 创建新通知
        self.current_notification = SlideNotification(
            self.parent, text, on_close=self._on_notification_close, **kwargs
        )
        self.current_notification.show()

    def _on_notification_close(self) -> None:
        """通知关闭回调"""
        self.current_notification = None

        # 显示队列中的下一个通知
        if self.notification_queue:
            text, kwargs = self.notification_queue.pop(0)
            self.show_notification(text, **kwargs)

    def clear_queue(self) -> None:
        """清空通知队列"""
        self.notification_queue.clear()

    def hide_current(self) -> None:
        """隐藏当前通知"""
        if self.current_notification:
            self.current_notification.hide()
