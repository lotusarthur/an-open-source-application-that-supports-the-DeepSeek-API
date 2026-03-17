# config.py
"""
全局配置文件
存储应用常量、API信息、路径配置等，所有模块共享此配置
"""
import json
import os
from typing import Optional

# ---------------------- 应用基础配置 ----------------------
APP_TITLE = "DeepSeek Chat"  # 应用窗口标题
WINDOW_SIZE = "800x600"                       # 初始窗口大小
BACKGROUND_COLOR = '#f0f0f0'                  # 背景色
FONT_DEFAULT = ("Arial", 11)                  # 默认字体
FONT_TITLE = ("Arial", 16, "bold")            # 标题字体

# ---------------------- AI服务配置 ----------------------
API_BASE_URL = "https://api.deepseek.com"     # DeepSeek API基础地址
API_MODEL = "deepseek-reasoner"               # 使用的AI模型
# 不再使用硬编码的API密钥，改为从配置文件读取
API_CONFIG_FILE = "api_config.json"           # API配置存储文件路径

# ---------------------- 人设配置 ----------------------
DEFAULT_AI_NAME = "默认小助手"                # 默认AI名称
DEFAULT_SYSTEM_PROMPT = (                     # 默认人设提示词
    "你是一位乐于助人的小助手. You need to be thorough, "
    "answer questions, and support your arguments with solid evidence."
)
PERSONAS_FILE = "ai_personas.json"            # 人设存储JSON文件路径

# 从配置文件加载API密钥
def load_api_key() -> Optional[str]:
    """从配置文件加载API密钥"""
    try:
        if os.path.exists(API_CONFIG_FILE):
            with open(API_CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get('api_key')
        return None
    except (json.JSONDecodeError, IOError) as e:
        print(f"加载API密钥失败: {e}")
        return None

def save_api_key(api_key: str) -> bool:
    """保存API密钥到配置文件"""
    try:
        with open(API_CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump({'api_key': api_key}, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        print(f"保存API密钥失败: {e}")
        return False

# 从配置文件加载API密钥
API_KEY = load_api_key()