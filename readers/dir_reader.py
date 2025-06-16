import os
import importlib
from typing import Dict, Any, List, Generator
import tomli
from .file_base_reader import FileBaseReader

class DirReader:
    """目录文件读取器"""
    
    def __init__(self, config_path: str = "config/config.toml"):
        """
        初始化目录读取器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.supported_types = self.config["reader"]["supported_types"]
        self.default_encoding = self.config["reader"]["default_encoding"]
        self.recursive = self.config["reader"]["recursive"]
        self.skip_hidden = self.config["reader"]["skip_hidden"]
        self.max_file_size = self.config["rag"]["document"]["max_file_size"]
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, "rb") as f:
            return tomli.load(f)
    
    def _is_hidden(self, path: str) -> bool:
        """判断是否为隐藏文件"""
        return os.path.basename(path).startswith('.')
    
    def _should_process_file(self, file_path: str) -> bool:
        """
        判断是否应该处理该文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否应该处理
        """
        # 检查文件大小
        if os.path.getsize(file_path) > self.max_file_size:
            return False
            
        # 检查是否为隐藏文件
        if self.skip_hidden and self._is_hidden(file_path):
            return False
            
        # 检查文件类型
        file_type = os.path.splitext(file_path)[1][1:].lower()
        return file_type in self.supported_types
    
    def read_directory(self, directory: str) -> Generator[Dict[str, Any], None, None]:
        """
        读取目录中的所有支持的文件
        
        Args:
            directory: 目录路径
            
        Yields:
            Dict[str, Any]: 文件内容和元数据
        """
        if not os.path.exists(directory):
            raise FileNotFoundError(f"目录不存在: {directory}")
            
        for root, _, files in os.walk(directory):
            # 如果不递归且不是根目录，跳过
            if not self.recursive and root != directory:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                
                # 检查是否应该处理该文件
                if not self._should_process_file(file_path):
                    continue
                    
                # 获取文件类型和对应的读取器类名
                file_type = os.path.splitext(file_path)[1][1:].lower()
                reader_class_name = self.supported_types.get(file_type)
                
                if reader_class_name:
                    try:
                        # 从readers包中导入对应的读取器类
                        module = importlib.import_module(f"readers.{file_type}_reader")
                        reader_class = getattr(module, reader_class_name)
                        
                        # 创建读取器实例并读取文件
                        reader = reader_class(file_path, encoding=self.default_encoding)
                        result = reader.read()
                        
                        # 添加相对路径信息
                        result["metadata"]["relative_path"] = os.path.relpath(file_path, directory)
                        
                        yield result
                    except Exception as e:
                        print(f"处理文件 {file_path} 时出错: {str(e)}")
    
    def read_all(self, directory: str) -> List[Dict[str, Any]]:
        """
        读取目录中的所有支持的文件并返回列表
        
        Args:
            directory: 目录路径
            
        Returns:
            List[Dict[str, Any]]: 所有文件的内容和元数据列表
        """
        return list(self.read_directory(directory)) 