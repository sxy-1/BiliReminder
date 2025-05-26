import tkinter as tk
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import threading
import queue


class SlideNotification(tk.Toplevel):
    def __init__(self, root, text, duration=3000, width=300, height=60, slide_speed=5):
        super().__init__(root)
        self.overrideredirect(True)  # 去除边框
        self.width = width
        self.height = height
        self.slide_speed = slide_speed
        self.duration = duration
        self.text = text
        self.start_y = -self.height
        self.end_y = 50  # 弹窗滑动到显示位置时的目标y坐标

        # 获取屏幕宽度和高度
        screen_width = self.winfo_screenwidth()
        self.geometry(
            f"{self.width}x{self.height}+{(screen_width - self.width) // 2}+{self.start_y}"
        )

        # 背景与文本
        self.configure(bg="white")
        label = tk.Label(
            self,
            text=text,
            fg="black",
            bg="white",
            font=("Helvetica", 16),  # 修改字体为Helvetica，大小为16
            wraplength=self.width - 20,  # 设置文本自动换行
            justify="center",  # 文本居中对齐
        )
        label.pack(expand=True, fill="both")

        # 设置DPI以提高清晰度 (Windows)
        try:
            from ctypes import windll

            windll.user32.SetProcessDPIAware()
        except OSError:
            print("无法设置DPI，可能不是在Windows上运行。")

        # 开始动画
        self.after(100, self.slide_down)  # 需要用 after 来延迟动画

    def slide_down(self):
        y = self.winfo_y()
        if y < self.end_y:
            self.geometry(
                f"{self.width}x{self.height}+{self.winfo_x()}+{y + self.slide_speed}"
            )
            self.after(10, self.slide_down)  # 循环动画
        else:
            self.after(self.duration, self.slide_up)  # 停留一段时间后滑上去

    def slide_up(self):
        y = self.winfo_y()
        if y > -self.height:
            self.geometry(
                f"{self.width}x{self.height}+{self.winfo_x()}+{y - self.slide_speed}"
            )
            self.after(10, self.slide_up)  # 循环动画
        else:
            self.destroy()  # 结束后销毁弹窗


def show_notification(root):
    SlideNotification(root, "这是一个通知消息", duration=3000)


def exit_action(icon, item):
    icon.stop()


def create_image(width, height, color1, color2):
    # Generate an image and draw a pattern
    image = Image.new("RGB", (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2), fill=color2
    )  # Corrected coordinates
    dc.rectangle(
        (0, height // 2, width // 2, height), fill=color2
    )  # Corrected coordinates
    return image


def setup_tray(root):
    image = create_image(64, 64, "black", "red")
    menu = (item("退出", lambda icon, item: (icon.stop(), root.quit())),)
    icon = pystray.Icon("BiliReminder", image, "BiliReminder", menu)
    return icon


def show_notification_loop(root, stop_event):
    while not stop_event.is_set():
        # 使用队列安全地在主线程中调用 GUI 操作
        root.after_idle(lambda: show_notification(root))
        if stop_event.wait(30):  # 等待30秒或直到收到停止信号
            break


def check_queue(root, notification_queue, stop_event):
    """检查队列中的通知请求"""
    try:
        while True:
            notification_queue.get_nowait()
            show_notification(root)
    except queue.Empty:
        pass

    if not stop_event.is_set():
        root.after(100, lambda: check_queue(root, notification_queue, stop_event))


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 创建停止事件和通知队列
    stop_event = threading.Event()
    notification_queue = queue.Queue()

    icon = setup_tray(root)

    # 修改线程函数
    def notification_timer():
        while not stop_event.is_set():
            notification_queue.put("notification")  # 向队列添加通知请求
            if stop_event.wait(30):  # 每30秒或直到停止
                break

    notification_thread = threading.Thread(target=notification_timer, daemon=True)
    notification_thread.start()

    # 启动队列检查
    check_queue(root, notification_queue, stop_event)

    # 在单独线程中运行托盘图标
    def run_tray():
        icon.run()

    tray_thread = threading.Thread(target=run_tray, daemon=True)
    tray_thread.start()

    try:
        root.mainloop()
    finally:
        stop_event.set()
        icon.stop()
