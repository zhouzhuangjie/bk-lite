from typing import List, Optional
from langserve import CustomUserType


class ChatHistory(CustomUserType):
    event: str
    text: str
    image_data: List[str] = []