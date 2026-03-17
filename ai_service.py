"""
AI服务模块
处理OpenAI风格API的交互（客户端初始化、流式调用），与UI逻辑完全分离
API调用支持中断（通过is_closing标志），避免窗口关闭时仍占用资源
"""

from openai import OpenAI
from openai.types.chat import ChatCompletionChunk
from typing import Generator, Optional
from config import API_BASE_URL, API_MODEL
from tkinter import messagebox


def init_ai_client(api_key: str, base_url: str = API_BASE_URL) -> Optional[OpenAI]:
    """
    初始化OpenAI风格客户端
    
    Args:
        api_key: API密钥（从config或环境变量获取）
        base_url: API基础地址，默认使用config中的API_BASE_URL
    
    Returns:
        Optional[OpenAI]: 初始化成功的客户端实例，失败返回None
    """
    try:
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        return client
    except Exception as e:
        messagebox.showerror("AI客户端初始化失败", f"无法连接AI服务: {str(e)}")
        return None


def call_api_stream(
    client: OpenAI,
    messages: list[dict],
    is_closing: bool,  # 非默认参数移到默认参数前面
    model: str = API_MODEL  # 默认参数放在最后
) -> Generator[str, None, None]:
    """
    流式调用AI API，逐段返回响应内容
    
    Args:
        client: 已初始化的OpenAI客户端
        messages: 对话历史，格式 [{role: str, content: str}, ...]
        is_closing: 中断标志（窗口关闭时设为True，终止API调用）
        model: 使用的AI模型，默认使用config中的API_MODEL
    
    Yields:
        str: 流式返回的每段文本内容
    """
    try:
        response: Generator[ChatCompletionChunk, None, None] = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True
        )
        
        # 逐段处理响应
        for chunk in response:
            # 检查是否需要中断（窗口关闭）
            if is_closing:
                yield "[API调用已中断]"
                return
            
            # 提取有效文本片段
            content = chunk.choices[0].delta.content
            if content:
                yield content
        
    except Exception as e:
        if not is_closing:  # 非关闭导致的异常才提示
            yield f"\n[AI服务错误: {str(e)}]"