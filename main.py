"""
BiliReminder 主程序

整合通知系统和托盘功能的主程序。
"""

import tkinter as tk
import threading
import queue
import sys
from typing import Optional

from notification import NotificationManager
from system_tray import TrayManager


class BiliReminderApp:
    """BiliReminder 应用程序主类"""

    def __init__(self):
        """初始化应用程序"""
        # 创建主窗口
        self.root = tk.Tk()
        self.root.withdraw()  # 隐藏主窗口

        # 初始化组件
        self.notification_manager = NotificationManager(self.root)
        self.tray_manager = TrayManager("BiliReminder")

        # 线程控制
        self.stop_event = threading.Event()
        self.notification_queue = queue.Queue()
        self.notification_thread: Optional[threading.Thread] = None

        # 设置托盘
        self._setup_tray()

        # 启动定时通知
        self._start_notification_timer()

        # 启动队列检查
        self._start_queue_checker()

    def _setup_tray(self) -> None:
        """设置系统托盘"""
        tray = self.tray_manager.create_tray()

        # 添加菜单项
        tray.add_menu_item("显示通知", self._show_test_notification)
        tray.add_menu_item("关于", self._show_about)

        # 添加退出回调
        self.tray_manager.add_exit_callback(self._on_exit)

    def _show_test_notification(self, icon, item_obj) -> None:
        """显示测试通知"""
        self.notification_queue.put("手动测试通知")

    def _show_about(self, icon, item_obj) -> None:
        """显示关于信息"""
        self.notification_queue.put("BiliReminder v1.0 - 哔哩哔哩提醒工具")

    def _start_notification_timer(self) -> None:
        """启动定时通知线程"""

        def notification_timer():
            """定时发送通知"""
            while not self.stop_event.is_set():
                self.notification_queue.put("定时提醒：该看B站了！")

                # 等待30秒或直到停止信号
                if self.stop_event.wait(30):
                    break

        self.notification_thread = threading.Thread(
            target=notification_timer, daemon=True
        )
        self.notification_thread.start()

    def _start_queue_checker(self) -> None:
        """启动队列检查器"""

        def check_queue():
            """检查通知队列"""
            try:
                while True:
                    message = self.notification_queue.get_nowait()
                    self.notification_manager.show_notification(message)
            except queue.Empty:
                pass

            # 如果没有停止，继续检查
            if not self.stop_event.is_set():
                self.root.after(100, check_queue)

        # 启动队列检查
        check_queue()

    def _on_exit(self) -> None:
        """退出处理"""
        print("正在关闭应用程序...")
        self.stop_event.set()

        # 清空通知队列
        self.notification_manager.clear_queue()

        # 退出主循环
        self.root.quit()

    def run(self) -> None:
        """运行应用程序"""
        try:
            # 启动托盘
            self.tray_manager.start()

            print("BiliReminder 已启动，请查看系统托盘")

            # 运行主循环
            self.root.mainloop()

        except KeyboardInterrupt:
            print("\n接收到中断信号，正在退出...")
        except Exception as e:
            print(f"应用程序运行出错: {e}")
        finally:
            self._cleanup()

    def _cleanup(self) -> None:
        """清理资源"""
        print("正在清理资源...")

        # 设置停止事件
        self.stop_event.set()

        # 停止托盘
        self.tray_manager.stop()

        # 等待线程结束
        if self.notification_thread and self.notification_thread.is_alive():
            self.notification_thread.join(timeout=1)

        print("资源清理完成")


def main():
    """主函数"""
    try:
        app = BiliReminderApp()
        app.run()
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
