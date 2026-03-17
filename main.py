"""
主应用入口
整合UI组件、AI服务、人设管理三大模块，处理核心业务逻辑
主类DeepSeekChatGUI仅负责模块协调和事件响应，具体实现 delegate 到其他模块
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from typing import Optional

# 导入拆分后的模块
from config import (
    APP_TITLE, WINDOW_SIZE, BACKGROUND_COLOR, API_KEY,
    load_api_key, save_api_key, FONT_TITLE, FONT_DEFAULT
)
from ai_service import init_ai_client, call_api_stream
from persona_manager import (
    load_personas, save_personas, add_or_update_persona,
    delete_persona, get_default_persona, is_persona_exist
)
from ui_components import (
    create_chat_frame, create_settings_frame, create_api_settings_frame,
    create_status_bar, refresh_persona_list
)


class DeepSeekChatGUI:
    """主应用类：协调所有模块，处理核心事件"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.is_closing = False  # 窗口关闭标志（用于中断API调用）
        
        # 1. 初始化依赖模块
        self._init_modules()
        
        # 2. 创建UI组件
        self._setup_ui()
        
        # 3. 绑定事件处理器
        self._setup_event_handlers()

    def _init_modules(self) -> None:
        """初始化AI服务、人设管理、对话历史"""
        # 初始化人设（从文件加载）
        self.personas = load_personas()
        self.ai_name, self.system_prompt = get_default_persona()
        
        # 加载API密钥
        self.saved_api_key = load_api_key()
        
        # 初始化AI客户端
        self.ai_client = init_ai_client(self.saved_api_key or API_KEY)
        
        # 初始化对话历史（包含系统提示）
        self.messages = [{"role": "system", "content": self.system_prompt}]

    def _setup_ui(self) -> None:
        """创建主窗口和所有UI组件"""
        # 配置主窗口
        self.root.title(APP_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(bg=BACKGROUND_COLOR)
        
        # 创建主框架（所有子框架的父容器）
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重（自适应窗口大小）
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=10)
        
        # 从ui_components导入并创建UI组件
        self.chat_frame = create_chat_frame(self.main_frame, self)
        self.settings_frame = create_settings_frame(self.main_frame, self)
        self.api_settings_frame = create_api_settings_frame(self.main_frame, self)
        create_status_bar(self.root, self)
        
        # 初始显示聊天界面
        self.show_chat_frame()

    def handle_enter_key(self, event: tk.Event) -> None:
        """处理Enter键和Shift+Enter组合键"""
        if event.state & 0x1:  # 检查Shift键是否被按下
            # Shift+Enter: 插入换行符
            self.input_field.insert(tk.INSERT, "\n")
            return "break"  # 阻止事件继续传播
        else:
            # 普通Enter: 发送消息
            self.send_message()
            return "break"  # 阻止默认行为（避免插入额外换行）

    def _setup_event_handlers(self) -> None:
        """绑定窗口关闭事件"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    # ---------------------- 界面切换逻辑 ----------------------
    def show_chat_frame(self) -> None:
        """显示聊天界面，隐藏设置界面"""
        self.settings_frame.grid_forget()
        self.api_settings_frame.grid_forget()
        self.chat_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        # 更新聊天标题（显示当前AI名称）
        self.chat_title_label.config(text=f"Chat with {self.ai_name}")
        self.input_field.focus()  # 聚焦输入框

    def show_settings_frame(self) -> None:
        """显示设置界面，隐藏聊天界面"""
        self.chat_frame.grid_forget()
        self.api_settings_frame.grid_forget()
        self.settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        refresh_persona_list(self.persona_listbox, self.personas)  # 刷新人设列表

    def show_api_settings_frame(self) -> None:
        """显示API设置界面，隐藏其他界面"""
        self.chat_frame.grid_forget()
        self.settings_frame.grid_forget()
        self.api_settings_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # ---------------------- 人设操作逻辑 ----------------------
    def on_persona_select(self, event: tk.Event) -> None:
        """选择列表中的人设时，更新编辑区内容"""
        selection = self.persona_listbox.curselection()
        if not selection:
            return
        
        selected_name = self.persona_listbox.get(selection[0])
        # 更新AI名称输入框
        self.ai_name_entry.delete(0, tk.END)
        self.ai_name_entry.insert(0, selected_name)
        # 更新人设提示词输入框
        self.persona_text.delete("1.0", tk.END)
        self.persona_text.insert(tk.END, self.personas[selected_name])

    def load_selected_persona(self) -> None:
        """加载选中的人设到当前会话（并清空现有聊天）"""
        selection = self.persona_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个人设！")
            return
        
        selected_name = self.persona_listbox.get(selection[0])
        # 更新当前人设信息
        self.ai_name = selected_name
        self.system_prompt = self.personas[selected_name]
        # 更新对话历史（仅保留新的系统提示，清空原有聊天记录）
        self.messages = [{"role": "system", "content": self.system_prompt}]
        # 清空UI聊天显示区
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        # 更新编辑区显示
        self.ai_name_entry.delete(0, tk.END)
        self.ai_name_entry.insert(0, self.ai_name)
        self.persona_text.delete("1.0", tk.END)
        self.persona_text.insert(tk.END, self.system_prompt)
        
        messagebox.showinfo("成功", f"已加载人设：{self.ai_name}\n现有聊天已清空")

    def delete_selected_persona(self) -> None:
        """删除选中的人设"""
        selection = self.persona_listbox.curselection()
        if not selection:
            messagebox.showinfo("提示", "请先选择一个人设！")
            return
        
        selected_name = self.persona_listbox.get(selection[0])
        if not messagebox.askyesno("确认删除", f"确定要删除人设「{selected_name}」吗？"):
            return
        
        # 删除人设（内存+文件）
        if delete_persona(self.personas, selected_name):
            save_personas(self.personas)
            refresh_persona_list(self.persona_listbox, self.personas)
            
            # 若删除的是当前人设，重置为默认
            if selected_name == self.ai_name:
                self.ai_name, self.system_prompt = get_default_persona()
                self.ai_name_entry.delete(0, tk.END)
                self.ai_name_entry.insert(0, self.ai_name)
                self.persona_text.delete("1.0", tk.END)
                self.persona_text.insert(tk.END, self.system_prompt)

    def create_new_persona(self) -> None:
        """创建新人设（从默认提示词开始）"""
        new_name = simpledialog.askstring("新建人设", "请输入新人设名称：")
        if not new_name:
            return
        
        new_name = new_name.strip()
        if is_persona_exist(self.personas, new_name):
            messagebox.showerror("错误", f"人设「{new_name}」已存在！")
            return
        
        # 初始化编辑区为默认人设
        self.ai_name_entry.delete(0, tk.END)
        self.ai_name_entry.insert(0, new_name)
        self.persona_text.delete("1.0", tk.END)
        # 聚焦输入框，方便用户修改
        self.ai_name_entry.focus()

    def save_current_persona(self) -> None:
        """保存当前编辑的人设（新增或更新）"""
        new_name = self.ai_name_entry.get().strip()
        new_prompt = self.persona_text.get("1.0", tk.END).strip()
        
        # 新增/更新人设（内存）
        if not add_or_update_persona(self.personas, new_name, new_prompt):
            return
        
        # 保存到文件
        if save_personas(self.personas):
            # 更新当前会话的人设
            self.ai_name = new_name
            self.system_prompt = new_prompt
            self.messages[0] = {"role": "system", "content": self.system_prompt}
            # 刷新列表并选中当前人设
            refresh_persona_list(self.persona_listbox, self.personas)
            for i, name in enumerate(self.personas.keys()):
                if name == new_name:
                    self.persona_listbox.selection_set(i)
                    self.persona_listbox.see(i)
                    break
            
            messagebox.showinfo("成功", f"已保存人设：{new_name}")

    # ---------------------- API设置逻辑 ----------------------
    def save_api_key(self) -> None:
        """保存API密钥到配置"""
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showinfo("提示", "请输入API密钥！")
            return
        
        if save_api_key(api_key):
            self.saved_api_key = api_key
            self.ai_client = init_ai_client(api_key)
            messagebox.showinfo("成功", "API密钥已保存")
        else:
            messagebox.showerror("错误", "保存API密钥失败")

    def delete_api_key(self) -> None:
        """删除保存的API密钥"""
        if not self.saved_api_key:
            messagebox.showinfo("提示", "没有保存的API密钥")
            return
        
        if messagebox.askyesno("确认", "确定要删除API密钥吗？"):
            if save_api_key(""):
                self.saved_api_key = ""
                self.api_key_entry.delete(0, tk.END)
                self.ai_client = init_ai_client(None)
                messagebox.showinfo("成功", "API密钥已删除")
            else:
                messagebox.showerror("错误", "删除API密钥失败")

    # ---------------------- 聊天交互逻辑 ----------------------
    def send_message(self, event: Optional[tk.Event] = None) -> None:
        """发送用户消息，触发AI响应（在新线程中调用API）"""
        if self.is_closing or not self.ai_client:
            messagebox.showwarning("警告", "请先配置有效的API密钥")
            return
        
        # 获取并验证用户输入（从多行文本框获取）
        user_input = self.input_field.get("1.0", tk.END).strip()
        if not user_input:
            return
        
        # 清空输入框
        self.input_field.delete("1.0", tk.END)
        # 禁用输入控件，防止重复发送
        self._disable_input()
        # 更新状态和对话历史
        self.status_var.set("Thinking...")
        self.messages.append({"role": "user", "content": user_input})
        self.display_message("You", user_input)
        
        # 在新线程中调用AI API（避免阻塞UI）
        threading.Thread(
            target=self._handle_ai_response,
            args=(user_input,),
            daemon=True
        ).start()

    def _handle_ai_response(self, user_input: str) -> None:
        """处理AI的流式响应，更新聊天界面"""
        # 显示AI回复前缀（如“Lanchester: ”）
        self.root.after(0, self._display_ai_prefix)
        
        # 调用AI服务（流式）
        ai_response = ""
        for chunk in call_api_stream(self.ai_client, self.messages, self.is_closing):
            if self.is_closing:
                break
            ai_response += chunk
            # 在主线程更新UI（避免线程安全问题）
            self.root.after(0, self.update_response, chunk)
        
        # 若未关闭，添加AI回复到对话历史
        if not self.is_closing and ai_response.strip():
            self.messages.append({"role": "assistant", "content": ai_response.strip()})
        
        # 完成后清理UI状态
        self.root.after(0, self._finish_ai_response)

    def display_message(self, sender: str, content: str) -> None:
        """显示消息到聊天区（通用方法）"""
        if self.is_closing:
            return
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: {content}\n\n")
        self.chat_display.see(tk.END)  # 滚动到最新消息
        self.chat_display.config(state=tk.DISABLED)

    def _display_ai_prefix(self) -> None:
        """显示AI回复的前缀（如“Lanchester: ”）"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{self.ai_name}: ")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def update_response(self, content: str) -> None:
        """流式更新AI回复内容到聊天区"""
        if self.is_closing:
            return
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, content)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def _finish_ai_response(self) -> None:
        """AI回复完成后，恢复UI状态"""
        if self.is_closing:
            return
        
        # 添加消息分隔符
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.config(state=tk.DISABLED)
        # 恢复输入控件
        self._enable_input()
        self.status_var.set("Ready")

    def start_new_conversation(self) -> None:
        """开始新对话，清空历史记录但保留当前人设"""
        # 重置对话历史（仅保留系统提示）
        self.messages = [{"role": "system", "content": self.system_prompt}]
        # 清空聊天显示区
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        # 聚焦输入框
        self.input_field.focus()
        # 更新状态
        self.status_var.set("Ready")

    # ---------------------- 辅助方法 ----------------------
    def _disable_input(self) -> None:
        """禁用输入控件（防止重复发送）"""
        self.send_button.config(state=tk.DISABLED)
        self.new_chat_button.config(state=tk.DISABLED)
        self.input_field.config(state=tk.DISABLED)

    def _enable_input(self) -> None:
        """启用输入控件"""
        self.send_button.config(state=tk.NORMAL)
        self.new_chat_button.config(state=tk.NORMAL)
        self.input_field.config(state=tk.NORMAL)
        self.input_field.focus()

    # ---------------------- 窗口关闭逻辑 ----------------------
    def on_closing(self) -> None:
        """处理窗口关闭（中断API调用，清理资源）"""
        self.is_closing = True
        self._disable_input()
        self.status_var.set("Closing...")
        # 延迟关闭，给API调用中断留出时间
        self.root.after(500, self.root.destroy)


def main() -> None:
    """应用入口函数"""
    root = tk.Tk()
    app = DeepSeekChatGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()