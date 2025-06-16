import os
from typing import List, Dict, Any, Type
import tomli
import importlib

from readers.dir_reader import DirReader
from readers.file_base_reader import FileBaseReader
from rules.split_base_rule import SplitRule
from rules.txt_split_rule import TxtSplitRule # 示例：需要导入具体的切分规则实现类
from agents.toolcall import ToolCall
from tools.vector_store import VectorStore
from utils.llm import LLM # 导入 LLM 类

class DataProcessor:
    """数据处理工具，整合文件读取、切分、向量化和存储的流程"""

    def __init__(self, config_path: str = "config/config.toml"):
        """
        初始化数据处理工具

        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.dir_reader = DirReader(config_path=config_path)
        self.tool_call = ToolCall(config_path=config_path)
        self.vector_store = VectorStore(persist_directory=self.config["rag"]["persist_directory"])
        # 初始化用于 Embedding 的 LLM 实例
        self.llm = LLM() # 不需要在这里传入配置，LLM类内部会自行加载
        
        # 初始化切分规则链
        self.split_rules: Dict[str, SplitRule] = {
            "txt": TxtSplitRule(max_chunk_size=1000, min_chunk_size=200, sentence_threshold=500),
            # 在这里添加其他文件类型的切分规则实例
        }

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, "rb") as f:
            return tomli.load(f)

    def _get_file_reader_class(self, file_type: str) -> Type[FileBaseReader]:
        """
        根据文件类型获取对应的文件读取器类。
        """
        reader_class_name = self.config["reader"]["supported_types"].get(file_type)
        if not reader_class_name:
            raise ValueError(f"不支持的文件读取类型: {file_type}")
        
        try:
            module = importlib.import_module(f"readers.{file_type}_reader")
            reader_class = getattr(module, reader_class_name)
            if not issubclass(reader_class, FileBaseReader):
                raise TypeError(f"读取器类 {reader_class_name} 必须继承自 FileBaseReader")
            return reader_class
        except (ImportError, AttributeError, TypeError) as e:
            raise RuntimeError(f"加载文件读取器 {file_type} 失败: {e}")

    def _process_file_content(self, file_data: Dict[str, Any], collection_name: str) -> None:
        """
        内部方法：处理单个文件内容的切分、向量化和存储。
        Args:
            file_data: 包含文件内容和元数据的字典。
            collection_name: 向量数据库集合名称。
        """
        content = file_data["content"]
        metadata = file_data["metadata"]
        file_type = metadata["file_type"]
        file_name = metadata["file_name"]

        print(f"处理文件: {file_name} ({file_type})")

        # 1. 文本切分
        splitter = self.split_rules.get(file_type)
        if not splitter:
            print(f"不支持的切分规则类型: {file_type}，跳过文件: {file_name}")
            return

        chunks = splitter.process(content, file_type)
        print(f"文件 {file_name} 切分完成，生成 {len(chunks)} 个文本块。")

        # 2. 文本向量化
        texts_to_embed = [chunk["content"] for chunk in chunks]
        embeddings_list = []

        try:
            print("开始创建 EmbeddingAgent 实例...")
            print(f"当前 tool_call 实例: {self.tool_call}")
            print(f"当前 vector_store 实例: {self.vector_store}")
            
            # 创建 embedding agent 实例，传入必需的参数
            embedding_agent = self.tool_call.get_agent_instance(
                "embedding",
                name="embedding_agent",
                llm=self.llm,  # 直接使用 DataProcessor 中的 llm 实例
                vector_store=self.vector_store
            )
            print(f"EmbeddingAgent 实例创建成功: {embedding_agent}")
            print(f"EmbeddingAgent 的 llm 实例: {embedding_agent.llm}")
            print(f"EmbeddingAgent 的 vector_store 实例: {embedding_agent.vector_store}")
            
            for text in texts_to_embed:
                embeddings_list.append(embedding_agent.llm.embed(text))
            print(f"文件 {file_name} 向量化完成。")

        except Exception as e:
            print(f"文件 {file_name} 向量化失败: {e}，跳过存储。")
            import traceback
            print(f"详细错误信息: {traceback.format_exc()}")
            return

        # 3. 准备文档存储
        documents_to_add = []
        for i, chunk in enumerate(chunks):
            if i < len(embeddings_list) and embeddings_list[i]: # 确保有对应的嵌入向量
                doc_id = f"{file_name}_{metadata.get("relative_path", "").replace("/", "_")}_{i}"
                doc_metadata = metadata.copy()
                doc_metadata.update(chunk["metadata"])
                doc_metadata["chunk_id"] = doc_id

                documents_to_add.append({
                    "id": doc_id,
                    "content": chunk["content"],
                    "vector": embeddings_list[i],
                    "metadata": doc_metadata
                })
        
        if documents_to_add:
            self.vector_store.add_documents(collection_name, documents_to_add)
        else:
            print(f"文件 {file_name} 没有生成可存储的文档。")

    def process_single_document(self, file_path: str, collection_name: str) -> None:
        """
        处理单个文档，并将其向量化后存储到向量数据库中。

        Args:
            file_path: 文档路径。
            collection_name: 向量数据库中用于存储文档的集合名称。
        """
        print(f"开始处理单个文件: {file_path}")
        self.vector_store.create_collection(collection_name)

        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            print(f"文件不存在或不是有效文件: {file_path}")
            return

        file_type = os.path.splitext(file_path)[1][1:].lower()
        if file_type not in self.config["rag"]["document"]["supported_formats"]:
            print(f"不支持的文件类型: {file_type}，跳过文件: {file_path}")
            return
        
        # 检查文件大小
        if os.path.getsize(file_path) > self.config["rag"]["document"]["max_file_size"]:
            print(f"文件过大: {file_path}")
            return

        try:
            reader_class = self._get_file_reader_class(file_type)
            reader = reader_class(file_path, encoding=self.config["reader"]["default_encoding"])
            file_data = reader.read()
            # 添加相对路径信息（对于单个文件，相对路径就是文件名本身）
            file_data["metadata"]["relative_path"] = os.path.basename(file_path)
            self._process_file_content(file_data, collection_name)
            print(f"文件 {file_path} 处理完成。")
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {e}")

    def process_document_directory(self, directory_path: str, collection_name: str) -> None:
        """
        处理指定目录下的所有文档，并将其向量化后存储到向量数据库中。

        Args:
            directory_path: 包含文档的目录路径。
            collection_name: 向量数据库中用于存储文档的集合名称。
        """
        print(f"开始处理目录: {directory_path}")
        self.vector_store.create_collection(collection_name)

        for file_data in self.dir_reader.read_directory(directory_path):
            self._process_file_content(file_data, collection_name)

        print(f"目录 {directory_path} 处理完成。") 