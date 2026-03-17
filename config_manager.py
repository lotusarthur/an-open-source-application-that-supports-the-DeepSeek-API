# config_manager.py
"""
应用配置管理器
处理API Key等敏感信息的存储和读取
"""
import json
import os
from tkinter import messagebox

def load_api_key(config_file: str) -> str:
    """加载保存的API Key"""
    try:
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('api_key', '')
        return ''
    except Exception as e:
        messagebox.showerror("配置加载错误", f"加载API Key失败: {str(e)}")
        return ''

def save_api_key(api_key: str, config_file: str) -> bool:
    """保存API Key到配置文件"""
    try:
        config = {'api_key': api_key.strip()}
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("配置保存错误", f"保存API Key失败: {str(e)}")
        return False