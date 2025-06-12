import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings


class VectorStore:
    """向量数据库管理类"""
    
    def __init__(self, persist_directory: str = "data/vector_store"):
        """
        初始化向量数据库
        :param persist_directory: 持久化目录
        """
        self.persist_directory = persist_directory
        os.makedirs(persist_directory, exist_ok=True)
        
        # 初始化ChromaDB客户端
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
    
    def create_collection(self, collection_name: str) -> None:
        """
        创建集合
        :param collection_name: 集合名称
        """
        if collection_name not in [c.name for c in self.client.list_collections()]:
            self.client.create_collection(
                name=collection_name,
                metadata={"description": f"Collection for {collection_name}"}
            )
    
    def add_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> None:
        """
        添加文档到集合
        :param collection_name: 集合名称
        :param documents: 文档列表
        """
        collection = self.client.get_collection(collection_name)
        
        # 准备数据
        ids = [f"doc_{i}" for i in range(len(documents))]
        texts = [doc["content"] for doc in documents]
        metadatas = [doc["metadata"] for doc in documents]
        embeddings = [doc["vector"] for doc in documents]
        
        # 添加到集合
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
    
    def search(self, 
              collection_name: str, 
              query_vector: List[float], 
              n_results: int = 5,
              where: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        搜索相似文档
        :param collection_name: 集合名称
        :param query_vector: 查询向量
        :param n_results: 返回结果数量
        :param where: 过滤条件
        :return: 搜索结果
        """
        collection = self.client.get_collection(collection_name)
        
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
            where=where
        )
        
        return [
            {
                "content": doc,
                "metadata": meta,
                "distance": dist
            }
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
    
    def delete_collection(self, collection_name: str) -> None:
        """
        删除集合
        :param collection_name: 集合名称
        """
        self.client.delete_collection(collection_name)
    
    def list_collections(self) -> List[str]:
        """
        列出所有集合
        :return: 集合名称列表
        """
        return [c.name for c in self.client.list_collections()] 