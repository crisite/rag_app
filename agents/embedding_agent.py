import logging
from typing import List, Dict, Any

from agents.base_agent import BaseAgent
from agents.react import ReActMixin
from utils.llm import LLM
from utils.agent_types import AgentState
from tools.vector_store import VectorStore

logger = logging.getLogger(__name__)

class EmbeddingAgent(BaseAgent, ReActMixin):
    """负责将文本内容转换为向量嵌入并存储的代理。"""
    name: str = "embedding_agent"  # 添加默认的 name 属性
    llm: LLM
    vector_store: VectorStore

    def __init__(self, **data: Any):
        super().__init__(**data)
        logger.info("EmbeddingAgent 初始化完成。")

    async def think(self) -> bool:
        """
        实现 ReActMixin 的 think 抽象方法。
        在此阶段，处理输入并进行思考，决定是否需要执行 act 步骤。
        """
        logger.info("进入 EmbeddingAgent 的 think 阶段。")

        # Input Stage Logic
        if not self.state.get("document_chunks"):
            logger.warning("在 EmbeddingAgent 的 think 阶段找不到需要处理的文档块。")
            self.state["embedding_result"] = {"status": "skipped", "reason": "没有文档块可处理"}
            self.state = AgentState.FINISHED # Mark as finished if nothing to do
            return False # No action needed

        logger.info(f"think 阶段开始。找到 {len(self.state['document_chunks'])} 个文档块。")

        # Think Stage Logic
        self.state["current_task"] = "embedding_documents"
        logger.info(f"think 阶段完成。当前任务设置为: {self.state['current_task']}")
        return True # Action is needed

    async def act(self) -> str:
        """
        实现 ReActMixin 的 act 抽象方法。
        在此阶段，执行嵌入操作并将结果存储到向量数据库，并处理输出。
        """
        logger.info("进入 EmbeddingAgent 的 act 阶段。")
        document_chunks = self.state.get("document_chunks", [])
        if not document_chunks:
            logger.warning("没有文档块需要嵌入。跳过 act 阶段。")
            self.state["embedding_result"] = {"status": "skipped", "reason": "没有文档块可嵌入"}
            self.state = AgentState.FINISHED # Mark as finished if nothing to do
            return "No documents to embed."

        embedded_documents = []
        for i, chunk in enumerate(document_chunks):
            try:
                logger.debug(f"正在嵌入文档块 {i+1}/{len(document_chunks)}: {chunk['content'][:50]}...")
                embedding = self.llm.embed(chunk["content"])
                embedded_documents.append({
                    "id": chunk.get("id"),
                    "content": chunk["content"],
                    "embedding": embedding,
                    "metadata": chunk.get("metadata", {})
                })
                logger.debug(f"文档块 {i+1} 嵌入成功。向量维度: {len(embedding)}")
            except Exception as e:
                logger.error(f"嵌入文档块 {i+1} 失败: {e}")
                continue
        
        logger.info(f"成功嵌入 {len(embedded_documents)} 个文档块。准备存储到向量数据库。")
        if embedded_documents:
            try:
                self.vector_store.add_documents(embedded_documents)
                logger.info(f"已将 {len(embedded_documents)} 个文档添加到向量数据库。")
                self.state["embedding_result"] = {"status": "success", "count": len(embedded_documents)}
            except Exception as e:
                logger.error(f"将嵌入文档添加到向量数据库失败: {e}")
                self.state["embedding_result"] = {"status": "failed", "error": str(e)}
        else:
            logger.info("没有嵌入的文档块可供存储。")
            self.state["embedding_result"] = {"status": "skipped", "reason": "没有嵌入的文档块"}
        
        # Output Stage Logic
        logger.info("进入 EmbeddingAgent 的 output 阶段。")
        embedding_result = self.state.get("embedding_result")
        if embedding_result and embedding_result.get("status") == "success":
            logger.info(f"文档嵌入和存储完成。成功处理 {embedding_result['count']} 个文档块。")
            self.state = AgentState.FINISHED # Mark as finished on success
            return f"Embedding and storage completed. Processed {embedding_result['count']} document chunks."
        elif embedding_result and embedding_result.get("status") == "failed":
            logger.error(f"文档嵌入或存储失败: {embedding_result.get('error')}")
            self.state = AgentState.ERROR # Mark as error
            return f"Embedding or storage failed: {embedding_result.get('error')}"
        else:
            logger.info("文档嵌入阶段已跳过或未完成。")
            self.state = AgentState.FINISHED # Mark as finished if skipped
            return "Embedding stage skipped or not completed."

    async def step(self) -> str:
        """
        Override BaseAgent 的 step 方法，使用 ReAct 模式。
        """
        logger.info("EmbeddingAgent 执行 step 方法 (ReAct 模式)。")
        # 调用 ReActMixin 中的 step 方法，它会按顺序调用 think 和 act
        return await super().step() 