from typing import List, Dict, Union, Optional

class MessageFormatter:
    """消息格式化工具类"""
    
    def format_multimodal_message(self, user_message: str, image_data: Optional[List[str]] = None) -> Union[str, List[Dict]]:
        """
        格式化多模态消息，支持文本和图片
        
        Args:
            user_message: 用户文本消息
            image_data: 图片的base64编码列表
            
        Returns:
            格式化后的消息内容
        """
        if not image_data:
            return user_message

        content = [{"type": "text", "text": user_message}]

        for img in image_data:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"{img}"
                }
            })

        return content

    def prepare_system_content(self, system_prompt: str, rag_content: str) -> str:
        """
        准备系统内容
        
        Args:
            system_prompt: 系统提示
            rag_content: RAG 上下文内容
            
        Returns:
            格式化后的系统内容
        """
        # 处理可能包含格式化占位符的 rag_content
        safe_rag_content = rag_content.replace('{', '{{').replace('}', '}}')
        return f"{system_prompt}, Here is some context: {safe_rag_content}"
