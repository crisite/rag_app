from abc import ABC, abstractmethod
from typing import List, Dict, Any

class SplitRule(ABC):
    """文本切分规则基类"""
    
    @abstractmethod
    def can_handle(self, content: str, file_type: str) -> bool:
        """
        判断当前规则是否可以处理该内容
        
        Args:
            content: 文本内容
            file_type: 文件类型
            
        Returns:
            bool: 是否可以处理
        """
        pass
    
    @abstractmethod
    def process(self, content: str, file_type: str) -> List[Dict[str, Any]]:
        """
        处理内容并返回分割结果
        
        Args:
            content: 文本内容
            file_type: 文件类型
            
        Returns:
            List[Dict[str, Any]]: 分割后的文本块列表，每个块包含内容和元数据
        """
        pass 