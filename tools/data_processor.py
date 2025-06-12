import os
from typing import List, Dict, Any, Optional
from rules.split_chain import SplitChain
from .vectorizer import Vectorizer
from .vector_store import VectorStore


class DataProcessor:
    """数据处理工具"""
    
    def __init__(self, vectorizer: Vectorizer = None, vector_store: VectorStore = None):
        """
        初始化数据处理工具
        :param vectorizer: 向量化工具实例
        :param vector_store: 向量数据库实例
        """
        self.split_chain = SplitChain()
        self.vectorizer = vectorizer or Vectorizer()
        self.vector_store = vector_store or VectorStore()
    
    def process_file(self, 
                    content: str, 
                    file_type: str, 
                    collection_name: str,
                    output_path: Optional[str] = None) -> None:
        """
        处理文件：分割文本、向量化并存储
        :param content: 文件内容
        :param file_type: 文件类型
        :param collection_name: 集合名称
        :param output_path: 输出路径（可选）
        """
        # 分割文本
        chunks = self.split_chain.process(content, file_type)
        
        # 向量化
        vectorized_chunks = self.vectorizer.vectorize(chunks)
        
        # 创建集合（如果不存在）
        self.vector_store.create_collection(collection_name)
        
        # 添加到向量数据库
        self.vector_store.add_documents(collection_name, vectorized_chunks)
        
        # 如果指定了输出路径，保存到文件
        if output_path:
            self.vectorizer.save_vectors(vectorized_chunks, output_path)
    
    def search_similar(self, 
                      collection_name: str,
                      query_text: str,
                      n_results: int = 5,
                      where: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        搜索相似文档
        :param collection_name: 集合名称
        :param query_text: 查询文本
        :param n_results: 返回结果数量
        :param where: 过滤条件
        :return: 搜索结果
        """
        # 将查询文本转换为向量
        query_vector = self.vectorizer.vectorize([{"content": query_text}])[0]["vector"]
        
        # 搜索相似文档
        return self.vector_store.search(
            collection_name=collection_name,
            query_vector=query_vector,
            n_results=n_results,
            where=where
        )
    
    def load_processed_data(self, file_path: str) -> List[Dict[str, Any]]:
        """
        加载处理后的数据
        :param file_path: 文件路径
        :return: 处理后的数据
        """
        return self.vectorizer.load_vectors(file_path) 