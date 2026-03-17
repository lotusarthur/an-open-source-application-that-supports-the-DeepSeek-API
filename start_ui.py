import tkinter as tk
from tkinter import ttk, font
import time
import threading
# 导入主应用类
from main import DeepSeekChatGUI
from config import APP_TITLE  # 复用主应用的标题配置

# 修改字体为SimKai（正楷）
FONT_DEFAULT = ('SimKai', 10)
FONT_TITLE = ('SimKai', 12, 'bold')
FONT_SPLASH_TITLE = ('SimKai', 20, 'bold')
FONT_CREATOR = ('SimKai', 14)
FONT_VERSE = ('SimKai', 12, 'italic')  # 诗句字体

# 颜色主题（与主应用保持一致）
primary_color = "#F2EDD0"       # 主色调：米白色（背景基础）
secondary_color = "#FFFFFF"     # 辅助色1：（人设背景）
accent_color = "#D39D8A"        # 强调色1：（按钮常态）
highlight_color = "#D4CFB6"     # 强调色2：（按钮交互态/边框）
text_color = "#261911"          # 文本色：深棕色（文字）

class SplashScreen(tk.Toplevel):
    def __init__(self, parent, app_title="AI Assistant", duration=3):
        super().__init__(parent)
        self.parent = parent
        self.duration = duration  # 启动界面显示时间（秒）
        self.app_title = app_title
        self.stop_thread = False  # 初始化线程停止标志
        
        # 配置窗口
        self.setup_window()
        
        # 创建界面元素
        self.create_widgets()
        
        # 启动计时器
        self.start_timer()
        
        # 显示窗口
        self.center_window()
        self.grab_set()  # 使启动界面成为模态窗口

    def setup_window(self):
        """配置启动窗口的基本属性"""
        self.title("Loading...")
        self.overrideredirect(True)  # 无边框窗口
        self.configure(bg=primary_color)
        
        # 不再设置全局字体，避免影响主应用
        # 只设置启动界面自身的字体
        self.option_add("*Font", FONT_DEFAULT)
        
        # 配置样式
        self.configure_styles()

    def configure_styles(self):
        """配置TTK控件样式"""
        style = ttk.Style()
        
        # 只配置启动界面使用的样式，不影响主应用
        style.configure("SplashTitle.TLabel", 
                       font=FONT_SPLASH_TITLE, 
                       background=primary_color, 
                       foreground=text_color)
        style.configure("Creator.TLabel", 
                       font=FONT_CREATOR, 
                       background=primary_color, 
                       foreground=text_color)
        style.configure("Status.TLabel", 
                       font=FONT_DEFAULT, 
                       background=primary_color, 
                       foreground=text_color)
        # 诗句样式
        style.configure("Verse.TLabel",
                       font=FONT_VERSE,
                       background=primary_color,
                       foreground=text_color)
        
        # 配置进度条样式
        style.configure("Splash.Horizontal.TProgressbar",
                       troughcolor=secondary_color,
                       background=accent_color,
                       bordercolor=highlight_color,
                       borderwidth=1)

    def create_widgets(self):
        """创建启动界面的所有控件"""
        # 创建主容器
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=40, pady=30)
        
        # 应用标题
        ttk.Label(
            container, 
            text=self.app_title, 
            style="SplashTitle.TLabel"
        ).pack(pady=(20, 40))
        
        # 制作人信息
        ttk.Label(
            container, 
            text=f"代码编写: LI JINQIU", 
            style="Creator.TLabel"
        ).pack(pady=(0, 40))
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(
            container,
            variable=self.progress_var,
            length=300,
            mode='determinate',
            style="Splash.Horizontal.TProgressbar"
        )
        progress_bar.pack(pady=(20, 10))
        
        # 状态标签
        self.status_label = ttk.Label(
            container, 
            text="Loading application...", 
            style="Status.TLabel"
        )
        self.status_label.pack(pady=(10, 20))
        
        # 诗句标识（居中底部）
        verse_label = ttk.Label(
            self,
            text="*´∀`)´∀`)*´∀`)*´∀`)",
            style="Verse.TLabel"
        )
        verse_label.place(relx=0.5, rely=0.95, anchor=tk.CENTER)

    def center_window(self):
        """将窗口居中显示在屏幕上"""
        self.update_idletasks()
        width = 400
        height = 300
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def start_timer(self):
        """启动计时器，控制启动界面的显示时间"""
        # 启动进度更新线程
        self.stop_thread = False
        threading.Thread(target=self.update_progress, daemon=True).start()
        
        # 设置自动关闭计时器
        self.after(self.duration * 1000, self.close_splash)

    def update_progress(self):
        """更新进度条"""
        progress = 0
        status_messages = [
            "Initializing components...",
            "Loading resources...",
            "Setting up interface...",
            "Almost ready..."
        ]
        
        while progress < 100 and not self.stop_thread:
            # 使用线程安全的方式更新UI
            self.after(0, self._update_progress, progress, status_messages)
            
            progress += 1
            time.sleep(self.duration / 100)  # 根据总时长调整进度速度

    def _update_progress(self, progress, status_messages):
        """线程安全的UI更新方法"""
        if self.stop_thread:
            return
            
        self.progress_var.set(progress)
        
        # 更新状态消息
        msg_index = min(int(progress / 25), len(status_messages) - 1)
        self.status_label.config(text=status_messages[msg_index])

    def close_splash(self):
        """关闭启动界面并启动主应用"""
        self.stop_thread = True  # 设置停止标志
        self.destroy()
        # 显示主窗口并初始化主应用
        self.parent.deiconify()
        DeepSeekChatGUI(self.parent)


def main():
    """应用入口：先显示启动界面，再加载主应用"""
    root = tk.Tk()
    root.withdraw()  # 初始隐藏主窗口
    root.title(APP_TITLE)  # 使用主应用的标题
    
    # 创建并显示启动界面，持续1秒
    splash = SplashScreen(root, app_title=APP_TITLE, duration=1)
    
    root.mainloop()


if __name__ == "__main__":
    main()