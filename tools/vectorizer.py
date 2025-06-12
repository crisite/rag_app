import os
import json
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer


class Vectorizer:
    """文本向量化工具"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        初始化向量化工具
        :param model_name: 使用的模型名称
        """
        self.model = SentenceTransformer(model_name)
        self.vector_size = self.model.get_sentence_embedding_dimension()
    
    def vectorize(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将文本块转换为向量
        :param chunks: 文本块列表
        :return: 包含向量的文本块列表
        """
        # 提取文本内容
        texts = [chunk["content"] for chunk in chunks]
        
        # 生成向量
        vectors = self.model.encode(texts)
        
        # 将向量添加到文本块中
        for chunk, vector in zip(chunks, vectors):
            chunk["vector"] = vector.tolist()
        
        return chunks
    
    def save_vectors(self, chunks: List[Dict[str, Any]], file_path: str) -> None:
        """
        保存向量数据
        :param chunks: 包含向量的文本块列表
        :param file_path: 保存路径
        """
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 保存数据
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
    
    def load_vectors(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载向量数据
        :param file_path: 文件路径
        :return: 包含向量的文本块列表
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f) 