# persona_manager.py
"""
人设数据管理器
独立处理人设的加载、保存、新增、删除等操作，与UI逻辑完全分离
所有函数均处理异常并返回状态，方便调用者处理结果
"""

import json
import os
from tkinter import messagebox
from config import DEFAULT_AI_NAME, DEFAULT_SYSTEM_PROMPT, PERSONAS_FILE


def load_personas(file_path: str = PERSONAS_FILE) -> dict:
    """
    加载人设数据（从JSON文件）
    
    Args:
        file_path: 人设文件路径，默认使用config中的PERSONAS_FILE
    
    Returns:
        dict: 人设字典，格式 {ai_name: system_prompt, ...}
              若文件不存在/异常，返回包含默认人设的字典
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                personas = json.load(f)
        else:
            personas = {}  # 文件不存在时初始化空字典
        
        # 确保至少有默认人设
        if not personas:
            personas[DEFAULT_AI_NAME] = DEFAULT_SYSTEM_PROMPT
            save_personas(personas, file_path)  # 保存默认人设到文件
        
        return personas
    
    except Exception as e:
        messagebox.showerror("人设加载错误", f"加载人设失败: {str(e)}")
        return {DEFAULT_AI_NAME: DEFAULT_SYSTEM_PROMPT}  # 异常时返回默认值


def save_personas(personas: dict, file_path: str = PERSONAS_FILE) -> bool:
    """
    保存人设数据到JSON文件
    
    Args:
        personas: 待保存的人设字典（{ai_name: system_prompt}）
        file_path: 保存路径，默认使用config中的PERSONAS_FILE
    
    Returns:
        bool: 保存成功返回True，失败返回False
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(personas, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        messagebox.showerror("人设保存错误", f"保存人设失败: {str(e)}")
        return False


def add_or_update_persona(personas: dict, ai_name: str, system_prompt: str) -> bool:
    """
    新增或更新人设（内存中）
    
    Args:
        personas: 当前人设字典
        ai_name: 人设名称（唯一标识）
        system_prompt: 人设提示词
    
    Returns:
        bool: 操作成功返回True（名称/提示词非空），失败返回False
    """
    if not ai_name.strip() or not system_prompt.strip():
        messagebox.showerror("输入错误", "AI名称和人设提示词不能为空！")
        return False
    
    personas[ai_name.strip()] = system_prompt.strip()
    return True


def delete_persona(personas: dict, ai_name: str) -> bool:
    """
    删除指定人设（内存中）
    
    Args:
        personas: 当前人设字典
        ai_name: 要删除的人设名称
    
    Returns:
        bool: 存在该人设并删除成功返回True，否则返回False
    """
    if ai_name in personas:
        del personas[ai_name]
        return True
    messagebox.showwarning("删除失败", f"人设「{ai_name}」不存在！")
    return False


def get_default_persona() -> tuple[str, str]:
    """
    获取默认人设（名称+提示词）
    
    Returns:
        tuple: (默认AI名称, 默认提示词)
    """
    return DEFAULT_AI_NAME, DEFAULT_SYSTEM_PROMPT


def is_persona_exist(personas: dict, ai_name: str) -> bool:
    """
    检查人设名称是否已存在
    
    Args:
        personas: 当前人设字典
        ai_name: 要检查的人设名称
    
    Returns:
        bool: 存在返回True，不存在返回False
    """
    return ai_name.strip() in personas