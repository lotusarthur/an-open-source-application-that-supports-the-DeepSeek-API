import tkinter as tk
from tkinter import scrolledtext, ttk, simpledialog

# 假设这些字体配置在config.py中
FONT_DEFAULT = ('Source Han Sans CN Light', 10)
FONT_TITLE = ('Source Han Sans CN Light', 12, 'bold')

# 配置颜色主题（使用指定色值，#F2EDD0为主色调）
def configure_styles():
    """配置应用的颜色主题（修复按钮样式问题）"""
    style = ttk.Style()
    
    # 配置整体样式
    style.configure(".", 
                   background=primary_color,
                   foreground=text_color,
                   font=FONT_DEFAULT)
    
    # 配置框架样式
    style.configure("TFrame", background=primary_color)
    
    # 配置标签样式
    style.configure("TLabel", background=primary_color, foreground=text_color)
    style.configure("Title.TLabel", font=FONT_TITLE, background=primary_color, foreground=text_color)
    
    # 配置按钮样式 - 修复"蒙白布"效果
    # 对于不同平台的按钮样式进行适配
    if 'clam' in style.theme_names():
        style.theme_use('clam')  # 使用clam主题以获得更好的样式控制
    
    style.configure("TButton", 
                   background=accent_color,
                   foreground=text_color,
                   padding=5,
                   borderwidth=1,
                   relief=tk.RAISED)  # 使用RAISED替代FLAT，增强按钮质感
    
    # 关键修复：确保按钮在各种状态下正确显示背景色
    style.map("TButton",
             background=[("active", highlight_color),  # 悬浮
                         ("pressed", secondary_color), # 按压
                         ("disabled", "#CCCCCC")],      # 禁用状态
             foreground=[("active", text_color),
                         ("pressed", text_color),
                         ("disabled", "#888888")],
             relief=[("pressed", tk.SUNKEN),           # 按压时凹陷
                     ("!pressed", tk.RAISED)])         # 常态时凸起
    
    # 配置输入框样式
    style.configure("TEntry", 
                   fieldbackground=secondary_color,
                   foreground=text_color,
                   padding=5,
                   borderwidth=1,
                   relief=tk.FLAT)
    
    # 配置标签框架样式
    style.configure("TLabelFrame", 
                   background=primary_color,
                   foreground=text_color,
                   borderwidth=1)
    style.configure("TLabelFrame.Label", 
                   background=primary_color,
                   foreground=text_color,
                   font=FONT_DEFAULT)
    
    # 状态栏专属样式
    style.configure("Status.TLabel",
                   background=primary_color,    # 状态栏背景（主色调）
                   foreground=text_color,       # 状态栏文本（深棕色）
                   borderwidth=1,               # 边框宽度
                   relief=tk.SUNKEN,            # 凹陷效果（符合状态栏视觉）
                   bordercolor=highlight_color) # 边框颜色（强调色2）


def create_chat_frame(parent: ttk.Frame, app) -> ttk.Frame:
    configure_styles()
    chat_frame = ttk.Frame(parent)
    
    # 1. 聊天标题栏
    chat_header = ttk.Frame(chat_frame)
    chat_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
    
    app.chat_title_label = ttk.Label(
        chat_header,
        text=f"Chat with {getattr(app, 'ai_name', 'AI')}",
        style="Title.TLabel"
    )
    app.chat_title_label.pack(side=tk.LEFT)
    
    ttk.Button(
        chat_header,
        text="AI人设与api选择",
        command=lambda: app.show_settings_frame() if hasattr(app, 'show_settings_frame') else None
    ).pack(side=tk.RIGHT)
    
    # 2. 聊天消息显示区
    app.chat_display = scrolledtext.ScrolledText(
        chat_frame,
        wrap=tk.WORD,
        width=70,
        height=25,
        font=FONT_DEFAULT,
        bg=secondary_color,  # 辅助色1
        fg=text_color,       # 深棕色文本
        relief=tk.FLAT,
        borderwidth=1
    )
    app.chat_display.grid(
        row=1,
        column=0,
        sticky=(tk.W, tk.E, tk.N, tk.S),
        pady=(0, 10)
    )
    app.chat_display.config(state=tk.DISABLED)
    
    # 3. 用户输入区（修改核心区域）
    input_frame = ttk.Frame(chat_frame)
    input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))
    input_frame.columnconfigure(0, weight=1)
    input_frame.columnconfigure(1, weight=0)
    
    # 多行输入框 - 固定高度，始终显示滚轴
    app.input_field = scrolledtext.ScrolledText(
        input_frame, 
        wrap=tk.WORD,
        width=65,          # 输入栏宽度
        height=10,          # 固定高度
        font=FONT_DEFAULT,
        bg=secondary_color,  
        fg=text_color,       
        relief=tk.FLAT,
        highlightthickness=1,
        highlightbackground=highlight_color  # 聚焦边框
    )
    app.input_field.grid(
        row=0, 
        column=0, 
        sticky=(tk.W, tk.E), 
        padx=(0, 10),
        pady=2
    )
    
    # 2. 输入逻辑修改：Enter发送，Shift+Enter换行
    def handle_enter(event):
        if event.state & 0x0001:  # 检测Shift键是否按下（0x0001为Shift键状态码）
            # Shift+Enter：插入换行符
            app.input_field.insert(tk.INSERT, '\n')
            return "break"  # 阻止默认行为（避免触发其他绑定）
        else:
            # Enter：调用发送消息函数
            if hasattr(app, 'send_message'):
                app.send_message()
            return "break"  # 阻止默认行为（避免输入框换行）
    
    app.input_field.bind("<Return>", handle_enter)  # 绑定Enter键处理函数
    
    # 按钮容器
    button_container = ttk.Frame(input_frame)
    button_container.grid(row=0, column=1, sticky=tk.N)
    
    app.send_button = ttk.Button(
        button_container,
        text="Send",
        command=lambda: app.send_message() if hasattr(app, 'send_message') else None
    )
    app.send_button.pack(side=tk.TOP, pady=(0, 5))
    
    app.new_chat_button = ttk.Button(
        button_container,
        text="New Chat",
        command=lambda: app.start_new_conversation() if hasattr(app, 'start_new_conversation') else None
    )
    app.new_chat_button.pack(side=tk.TOP)
    
    # 网格权重配置
    chat_frame.columnconfigure(0, weight=1)
    chat_frame.rowconfigure(1, weight=1)
    
    return chat_frame


def create_settings_frame(parent: ttk.Frame, app) -> ttk.Frame:
    configure_styles()
    settings_frame = ttk.Frame(parent)
    
    # 1. 设置标题栏
    settings_header = ttk.Frame(settings_frame)
    settings_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
    
    ttk.Label(
        settings_header,
        text="AI Assistant Settings",
        style="Title.TLabel"
    ).pack(side=tk.LEFT)
    
    ttk.Button(
        settings_header,
        text="API Settings",
        command=lambda: app.show_api_settings_frame() if hasattr(app, 'show_api_settings_frame') else None
    ).pack(side=tk.RIGHT, padx=(0, 10))
    
    ttk.Button(
        settings_header,
        text="Back to Chat",
        command=lambda: app.show_chat_frame() if hasattr(app, 'show_chat_frame') else None
    ).pack(side=tk.RIGHT)
    
    # 2. 设置内容区
    settings_content = ttk.Frame(settings_frame)
    settings_content.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    settings_content.columnconfigure(0, weight=1)
    settings_content.columnconfigure(1, weight=1)
    settings_content.rowconfigure(0, weight=1)
    
    # 左侧：人设列表
    persona_list_frame = ttk.LabelFrame(settings_content, text="Saved Personas")
    persona_list_frame.grid(
        row=0,
        column=0,
        sticky=(tk.W, tk.E, tk.N, tk.S),
        padx=(0, 10),
        pady=(10, 0)
    )
    persona_list_frame.columnconfigure(0, weight=1)
    persona_list_frame.rowconfigure(0, weight=1)
    
    app.persona_listbox = tk.Listbox(
        persona_list_frame, 
        font=FONT_DEFAULT,
        bg=secondary_color,          # 辅助色1
        fg=text_color,
        highlightbackground=highlight_color,
        highlightcolor=highlight_color,
        selectbackground=accent_color,    # 选中背景（强调色1）
        selectforeground=primary_color    # 选中文本（主色调）
    )
    app.persona_listbox.grid(
        row=0,
        column=0,
        sticky=(tk.W, tk.E, tk.N, tk.S),
        padx=5,
        pady=5
    )
    app.persona_listbox.bind('<<ListboxSelect>>', lambda e: app.on_persona_select(e) if hasattr(app, 'on_persona_select') else None)
    
    # 人设操作按钮
    persona_buttons = ttk.Frame(persona_list_frame)
    persona_buttons.grid(row=1, column=0, sticky=tk.EW, padx=5, pady=5)
    
    ttk.Button(persona_buttons, text="Load", command=lambda: app.load_selected_persona() if hasattr(app, 'load_selected_persona') else None).pack(side=tk.LEFT, padx=2)
    ttk.Button(persona_buttons, text="Delete", command=lambda: app.delete_selected_persona() if hasattr(app, 'delete_selected_persona') else None).pack(side=tk.LEFT, padx=2)
    ttk.Button(persona_buttons, text="New", command=lambda: app.create_new_persona() if hasattr(app, 'create_new_persona') else None).pack(side=tk.LEFT, padx=2)
    
    # 右侧：当前人设编辑
    current_persona_frame = ttk.LabelFrame(settings_content, text="Current Persona")
    current_persona_frame.grid(
        row=0,
        column=1,
        sticky=(tk.W, tk.E, tk.N, tk.S),
        pady=(10, 0)
    )
    current_persona_frame.columnconfigure(0, weight=1)
    current_persona_frame.rowconfigure(3, weight=1)
    
    # AI名称输入
    ttk.Label(
        current_persona_frame,
        text="AI Assistant Name:",
        font=FONT_DEFAULT
    ).grid(row=0, column=0, sticky=tk.W, pady=(10, 5), padx=5)
    
    app.ai_name_entry = ttk.Entry(current_persona_frame, font=FONT_DEFAULT)
    app.ai_name_entry.insert(0, getattr(app, 'ai_name', 'AI Assistant'))
    app.ai_name_entry.grid(
        row=1,
        column=0,
        sticky=(tk.W, tk.E),
        pady=(0, 10),
        padx=5
    )
    
    # 人设提示词输入
    ttk.Label(
        current_persona_frame,
        text="Persona Description:",
        font=FONT_DEFAULT
    ).grid(row=2, column=0, sticky=tk.W, pady=(10, 5), padx=5)
    
    app.persona_text = scrolledtext.ScrolledText(
        current_persona_frame,
        wrap=tk.WORD,
        width=40,
        height=15,
        font=FONT_DEFAULT,
        bg=secondary_color,  # 辅助色1
        fg=text_color,       # 深棕色文本
        relief=tk.FLAT,
        borderwidth=1
    )
    app.persona_text.grid(
        row=3,
        column=0,
        sticky=(tk.W, tk.E, tk.N, tk.S),
        pady=(0, 10),
        padx=5
    )
    app.persona_text.insert(tk.END, getattr(app, 'system_prompt', ''))
    
    # 保存按钮
    app.save_button = ttk.Button(
        current_persona_frame,
        text="Save Current Persona",
        command=lambda: app.save_current_persona() if hasattr(app, 'save_current_persona') else None
    )
    app.save_button.grid(row=4, column=0, pady=10, padx=5)
    
    # 网格权重配置
    settings_frame.columnconfigure(0, weight=1)
    settings_frame.rowconfigure(1, weight=1)
    
    return settings_frame


def create_api_settings_frame(parent: ttk.Frame, app) -> ttk.Frame:
    configure_styles()
    api_frame = ttk.Frame(parent)
    
    # 1. API设置标题栏
    api_header = ttk.Frame(api_frame)
    api_header.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
    
    ttk.Label(
        api_header,
        text="API Configuration",
        style="Title.TLabel"
    ).pack(side=tk.LEFT)
    
    ttk.Button(
        api_header,
        text="Back to Settings",
        command=lambda: app.show_settings_frame() if hasattr(app, 'show_settings_frame') else None
    ).pack(side=tk.RIGHT)
    
    # 2. API设置内容区
    api_content = ttk.Frame(api_frame)
    api_content.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=20, pady=20)
    api_content.columnconfigure(0, weight=1)
    
    # API密钥输入
    ttk.Label(
        api_content,
        text="API Key:",
        font=FONT_DEFAULT
    ).grid(row=0, column=0, sticky=tk.W, pady=(10, 5))
    
    app.api_key_entry = ttk.Entry(api_content, font=FONT_DEFAULT)
    app.api_key_entry.grid(
        row=1,
        column=0,
        sticky=(tk.W, tk.E),
        pady=(0, 20)
    )
    if hasattr(app, 'saved_api_key') and app.saved_api_key:
        app.api_key_entry.insert(0, app.saved_api_key)
    
    # API说明文本
    ttk.Label(
        api_content,
        text="Enter your API key for accessing the AI service. "
             "The key will be stored securely in the application settings.",
        font=FONT_DEFAULT,
        wraplength=500,
        foreground=text_color
    ).grid(row=2, column=0, sticky=tk.W, pady=(0, 20))
    
    # 操作按钮区
    button_frame = ttk.Frame(api_content)
    button_frame.grid(row=3, column=0, sticky=tk.E, pady=10)
    
    ttk.Button(
        button_frame,
        text="Delete API Key",
        command=lambda: app.delete_api_key() if hasattr(app, 'delete_api_key') else None
    ).pack(side=tk.LEFT, padx=10)
    
    ttk.Button(
        button_frame,
        text="Save API Key",
        command=lambda: app.save_api_key() if hasattr(app, 'save_api_key') else None
    ).pack(side=tk.LEFT)
    
    # 网格权重配置
    api_frame.columnconfigure(0, weight=1)
    api_frame.rowconfigure(1, weight=1)
    
    return api_frame


def create_status_bar(parent: tk.Tk, app) -> None:
    """创建状态栏（使用专属TTK样式）"""
    configure_styles()
    
    app.status_var = tk.StringVar()
    app.status_var.set("Ready")
    
    # 使用在configure_styles中定义的"Status.TLabel"样式
    status_bar = ttk.Label(
        parent,
        textvariable=app.status_var,
        style="Status.TLabel",  # 应用专属样式（包含边框颜色、背景等）
        anchor=tk.W  # 文本左对齐
    )
    status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))


def refresh_persona_list(listbox: tk.Listbox, personas: dict) -> None:
    listbox.delete(0, tk.END)
    for ai_name in personas.keys():
        listbox.insert(tk.END, ai_name)

# 全局颜色变量
primary_color = "#F2EDD0"       # 主色调：米白色（背景基础）
secondary_color = "#FFFFFF"     # 辅助色1：（人设背景）
accent_color = "#D39D8A"        # 强调色1：（按钮常态）
highlight_color = "#D4CFB6"     # 强调色2：（按钮交互态/边框）
text_color = "#261911"          # 文本色：深棕色（文字）