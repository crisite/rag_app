import os
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

class VectorStore:
    """向量数据库管理类，使用ChromaDB"""
    
    def __init__(self, persist_directory: str = "data/vector_store"):
        """
        初始化向量数据库
        
        Args:
            persist_directory: 持久化目录
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
        
        Args:
            collection_name: 集合名称
        """
        try:
            self.client.get_or_create_collection(collection_name)
            print(f"集合 '{collection_name}' 已存在或创建成功。")
        except Exception as e:
            print(f"创建或获取集合 '{collection_name}' 失败: {e}")
            raise
    
    def add_documents(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """
        添加文档到集合
        
        Args:
            collection_name: 集合名称
            documents: 包含 'content' 和 'vector' 的文档列表，以及可选的 'metadata'。
                       每个文档字典应至少包含 {"content": str, "vector": List[float]}。
                       可选地，可以包含 {"metadata": Dict[str, Any]}。
            
        Returns:
            List[str]: 添加的文档ID列表
        """
        collection = self.client.get_collection(collection_name)
        
        ids = []
        texts = []
        metadatas = []
        embeddings = []
        
        for i, doc in enumerate(documents):
            # 生成唯一ID，如果文档没有提供ID
            doc_id = doc.get("id")
            if not doc_id:
                # 使用UUID或者其他更健壮的ID生成方式在实际应用中更好
                # 这里为了简化，使用基于时间戳和索引的方式
                doc_id = f"{collection_name}_{len(collection.peek()) + i}"
            ids.append(doc_id)
            texts.append(doc["content"])
            embeddings.append(doc["vector"])
            metadatas.append(doc.get("metadata", {}))
            
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        print(f"成功向集合 '{collection_name}' 添加 {len(ids)} 个文档。")
        return ids
    
    def search(
        self,
        collection_name: str,
        query_vector: List[float],
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索相似文档
        
        Args:
            collection_name: 集合名称
            query_vector: 查询向量
            n_results: 返回结果数量
            where: 过滤条件
            
        Returns:
            List[Dict[str, Any]]: 搜索结果列表，包含 content, metadata, distance
        """
        collection = self.client.get_collection(collection_name)
        
        results = collection.query(
            query_embeddings=[query_vector],
            n_results=n_results,
            where=where
        )
        
        formatted_results = []
        if results["documents"] and results["embeddings"] and results["metadatas"] and results["distances"]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                formatted_results.append({
                    "content": doc,
                    "metadata": meta,
                    "distance": dist
                })
        return formatted_results
    
    def delete_collection(self, collection_name: str) -> None:
        """
        删除集合
        
        Args:
            collection_name: 集合名称
        """
        self.client.delete_collection(collection_name)
        print(f"集合 '{collection_name}' 已删除。")
    
    def list_collections(self) -> List[str]:
        """
        列出所有集合
        
        Returns:
            List[str]: 集合名称列表
        """
        return [c.name for c in self.client.list_collections()]
    
    def reset_db(self) -> None:
        """
        重置ChromaDB数据库，删除所有集合。
        """
        self.client.reset()
        print("ChromaDB数据库已重置。") 