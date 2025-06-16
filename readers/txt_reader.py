from typing import Dict, Any
import os
from .file_base_reader import FileBaseReader

class TxtReader(FileBaseReader):
    """TXT文件读取器"""
    
    def __init__(self, file_path: str, encoding: str = 'utf-8'):
        """
        初始化TXT文件读取器
        
        Args:
            file_path: 文件路径
            encoding: 文件编码，默认utf-8
        """
        super().__init__(file_path)
        self.encoding = encoding
    
    def read(self) -> Dict[str, Any]:
        """
        读取TXT文件内容
        
        Returns:
            Dict[str, Any]: 包含文件内容和元数据的字典
        """
        if not self.validate():
            raise ValueError(f"无效的文件: {self.file_path}")
        
        try:
            with open(self.file_path, 'r', encoding=self.encoding) as f:
                content = f.read()
            
            # 获取文件元数据
            metadata = self.get_metadata()
            
            # 添加TXT特有的元数据
            metadata.update({
                "line_count": len(content.splitlines()),
                "encoding": self.encoding,
                "has_bom": content.startswith('\ufeff')  # 检查是否有BOM标记
            })
            
            # 如果文件有BOM标记，移除它
            if metadata["has_bom"]:
                content = content[1:]
            
            return {
                "content": content,
                "metadata": metadata
            }
            
        except UnicodeDecodeError:
            # 如果UTF-8解码失败，尝试其他编码
            encodings = ['gbk', 'gb2312', 'gb18030', 'big5']
            for enc in encodings:
                try:
                    with open(self.file_path, 'r', encoding=enc) as f:
                        content = f.read()
                    
                    # 更新元数据
                    metadata = self.get_metadata()
                    metadata.update({
                        "line_count": len(content.splitlines()),
                        "encoding": enc,
                        "has_bom": content.startswith('\ufeff')
                    })
                    
                    if metadata["has_bom"]:
                        content = content[1:]
                    
                    return {
                        "content": content,
                        "metadata": metadata
                    }
                except UnicodeDecodeError:
                    continue
            
            raise ValueError(f"无法解码文件: {self.file_path}，请检查文件编码") 