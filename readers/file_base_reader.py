from abc import ABC, abstractmethod
from typing import Dict, Any
import os

class FileBaseReader(ABC):
    """文件读取基类"""
    
    def __init__(self, file_path: str):
        """
        初始化文件读取器
        
        Args:
            file_path: 文件路径
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        self.file_path = file_path
        self.content = None
    
    @abstractmethod
    def read(self) -> Dict[str, Any]:
        """
        读取文件内容
        
        Returns:
            Dict[str, Any]: 包含文件内容和元数据的字典
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取文件元数据
        
        Returns:
            Dict[str, Any]: 文件元数据，包含文件名、大小、创建时间等
        """
        file_stat = os.stat(self.file_path)
        return {
            "file_name": os.path.basename(self.file_path),
            "file_size": file_stat.st_size,
            "created_time": file_stat.st_ctime,
            "modified_time": file_stat.st_mtime,
            "file_type": os.path.splitext(self.file_path)[1][1:].lower()
        }
    
    def validate(self) -> bool:
        """
        验证文件是否有效
        
        Returns:
            bool: 文件是否有效
        """
        return os.path.isfile(self.file_path) and os.path.getsize(self.file_path) > 0 