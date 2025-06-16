from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from .agent_types import ROLE_TYPE

class Message(BaseModel):
    """代表代理对话中的单个消息"""
    id: str = Field(default_factory=lambda: datetime.now().isoformat(), description="消息的唯一ID")
    role: ROLE_TYPE = Field(..., description="消息发送者的角色")
    content: str = Field(..., description="消息内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="消息时间戳")
    base64_image: Optional[str] = Field(None, description="可选的Base64编码图片内容")
    tool_call_id: Optional[str] = Field(None, description="工具调用消息的工具调用ID")

    @classmethod
    def user_message(cls, content: str, base64_image: Optional[str] = None) -> "Message":
        return cls(role="user", content=content, base64_image=base64_image)

    @classmethod
    def system_message(cls, content: str) -> "Message":
        return cls(role="system", content=content)

    @classmethod
    def assistant_message(cls, content: str) -> "Message":
        return cls(role="assistant", content=content)

    @classmethod
    def tool_message(cls, content: str, tool_call_id: str) -> "Message":
        return cls(role="tool", content=content, tool_call_id=tool_call_id)

class Memory(BaseModel):
    """管理代理的消息历史"""
    messages: List[Message] = Field(default_factory=list, description="消息列表")

    def add_message(self, message: Message) -> None:
        """添加消息到历史记录"""
        self.messages.append(message)

    def get_messages(self) -> List[Message]:
        """获取所有消息"""
        return self.messages

    def clear(self) -> None:
        """清空消息历史"""
        self.messages = []

    def __len__(self) -> int:
        return len(self.messages)

    def __getitem__(self, index) -> Message:
        return self.messages[index]

    class Config:
        arbitrary_types_allowed = True 