from typing import Any, Dict, List, Tuple, Union
import tiktoken
from loguru import logger

class TokenCounter:
    """Token计数工具类"""
    
    def __init__(self, model: str):
        """
        初始化Token计数器
        
        Args:
            model: 使用的模型名称
        """
        # 初始化分词器
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except Exception:
            logger.warning(f"无法找到模型 {model} 的分词器，使用默认分词器")
            self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: Any) -> int:
        """
        计算文本的 token 数量
        
        Args:
            text: 要计算的文本，可以是字符串或其他格式（如列表、字典）
            
        Returns:
            token 数量
        """
        if not text:
            return 0
            
        # 处理多模态内容（列表或字典）
        if isinstance(text, (list, dict)):
            return self._count_multimodal_tokens(text)
            
        # 确保文本是字符串
        if not isinstance(text, str):
            text = str(text)
            
        return len(self.encoding.encode(text))
        
    def _count_multimodal_tokens(self, content: Union[List, Dict]) -> int:
        """
        计算多模态内容的 token 数量
        
        Args:
            content: 多模态内容，可以是列表或字典
            
        Returns:
            预估的 token 数量
        """
        if isinstance(content, dict):
            # 处理字典格式
            tokens = 0
            for key, value in content.items():
                tokens += self.count_tokens(key)
                tokens += self.count_tokens(value)
            return tokens
            
        elif isinstance(content, list):
            # 处理列表格式
            tokens = 0
            for item in content:
                if isinstance(item, dict):
                    # 特殊处理多模态项
                    if item.get("type") == "text" and "text" in item:
                        # 文本项
                        tokens += self.count_tokens(item["text"])
                    elif item.get("type") == "image_url" and "image_url" in item:
                        # 图片项 - 每张图片估算固定 token 量 (根据模型不同而变化，这里使用保守估计)
                        tokens += 85  # GPT-4V 图片基础 token 消耗估计
                    else:
                        # 其他字典项
                        tokens += self._count_multimodal_tokens(item)
                else:
                    # 非字典项
                    tokens += self.count_tokens(item)
            return tokens
            
        # 不应该到达这里
        return 0

    def count_message_tokens(self, messages: List[Dict]) -> Tuple[int, int]:
        """
        计算消息列表的输入和输出 token 数量
        
        Args:
            messages: 消息列表
            
        Returns:
            (输入token数, 输出token数) 元组
        """
        input_tokens = output_tokens = 0

        for message in messages:
            content = message.content
            if content:
                input_tokens += self.count_tokens(content)

        return input_tokens, output_tokens
