from abc import ABC, abstractmethod
from typing import List, Dict, Any


class SplitRule(ABC):
    """文件分割规则基类"""
    
    @abstractmethod
    def can_handle(self, content: str, file_type: str) -> bool:
        """判断当前规则是否可以处理该内容"""
        pass
    
    @abstractmethod
    def process(self, content: str, file_type: str) -> List[Dict[str, Any]]:
        """处理内容并返回分割结果"""
        pass 