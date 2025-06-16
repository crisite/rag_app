import os
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, model_validator
import tomli
import ollama
import logging

logger = logging.getLogger(__name__)

class LLM(BaseModel):
    """语言模型接口抽象类。"""
    # 这些字段将从 config.toml 中填充
    model: str = Field("", description="用于文本生成的主要LLM模型名称")
    base_url: str = Field("", description="LLM API基础URL")
    api_key: str = Field("ollama", description="LLM API Key")
    max_tokens: int = Field(4096, description="LLM最大生成tokens")
    temperature: float = Field(0.0, description="LLM生成温度")

    # 嵌入特定设置，将从 [llm.embedding] 中填充
    embedding_model: str = Field("", description="用于文本嵌入的LLM模型名称")
    embedding_base_url: str = Field("", description="嵌入API基础URL")
    embedding_api_key: str = Field("ollama", description="嵌入API Key")

    ollama_gen_client: Optional[ollama.Client] = Field(None, exclude=True)
    ollama_embed_client: Optional[ollama.Client] = Field(None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    @model_validator(mode="after")
    def initialize_llm_clients(self) -> "LLM":
        """初始化LLM实例，从配置加载参数并初始化Ollama客户端。"""
        # 加载全局配置
        config_data = self._load_global_config()

        # 填充主LLM设置
        llm_config = config_data.get("llm", {})
        self.model = llm_config.get("model", self.model)
        self.base_url = llm_config.get("base_url", self.base_url)
        self.api_key = llm_config.get("api_key", self.api_key)
        self.max_tokens = llm_config.get("max_tokens", self.max_tokens)
        self.temperature = llm_config.get("temperature", self.temperature)

        # 填充嵌入LLM设置
        embedding_config = llm_config.get("embedding", {})
        self.embedding_model = embedding_config.get("model", self.embedding_model)
        self.embedding_base_url = embedding_config.get("base_url", self.embedding_base_url)
        self.embedding_api_key = embedding_config.get("api_key", self.embedding_api_key)

        logger.info(f"初始化LLM: 模型={self.model}, URL={self.base_url}")
        logger.info(f"初始化嵌入LLM: 模型={self.embedding_model}, URL={self.embedding_base_url}")

        # 如果提供了 base_url，初始化 Ollama 生成客户端
        if self.base_url:
            self.ollama_gen_client = ollama.Client(host=self.base_url)

        # 如果提供了 embedding_base_url，初始化 Ollama 嵌入客户端
        if self.embedding_base_url:
            self.ollama_embed_client = ollama.Client(host=self.embedding_base_url)
        
        return self

    def _load_global_config(self) -> Dict[str, Any]:
        """加载全局配置文件。"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = os.path.join(script_dir, "..") # 从 'utils' 目录向上到项目根目录
        config_path = os.path.join(root_dir, "config", "config.toml")

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件未找到: {config_path}。请确保它存在。")

        with open(config_path, "rb") as f:
            return tomli.load(f)

    def generate(self, prompt: str, **kwargs) -> str:
        """
        根据给定的提示生成响应。
        Args:
            prompt: 输入提示。
            **kwargs: 额外参数（例如：temperature, max_tokens）。
        Returns:
            生成的文本响应。
        """
        if not self.ollama_gen_client:
            raise RuntimeError("Ollama 生成客户端未初始化。请检查 LLM 配置。")
        
        logger.debug(f"LLM生成请求: 模型={self.model}, 提示={prompt[:100]}...")
        try:
            response = self.ollama_gen_client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "temperature": kwargs.get("temperature", self.temperature),
                    "num_predict": kwargs.get("max_tokens", self.max_tokens)
                }
            )
            generated_text = response.get("response", "")
            logger.debug(f"LLM生成响应 (部分): {generated_text[:100]}...")
            logger.info(f"LLM生成响应 (完整): {generated_text}")
            return generated_text
        except Exception as e:
            logger.error(f"LLM生成失败: {e}")
            raise RuntimeError(f"LLM生成失败: {e}")

    def embed(self, text: str) -> List[float]:
        """
        生成文本的嵌入向量。
        Args:
            text: 输入文本。
        Returns:
            文本的嵌入向量。
        """
        if not self.ollama_embed_client:
            raise RuntimeError("Ollama 嵌入客户端未初始化。请检查嵌入配置。")
        
        logger.debug(f"LLM嵌入请求: 模型={self.embedding_model}, 文本={text[:100]}...")
        try:
            response = self.ollama_embed_client.embeddings(
                model=self.embedding_model,
                prompt=text
            )
            embedding = response.get("embedding", [])
            logger.debug(f"LLM嵌入响应: 向量维度={len(embedding)}")
            logger.info(f"LLM嵌入响应 (完整): {embedding}")
            return embedding
        except Exception as e:
            logger.error(f"LLM嵌入失败: {e}")
            raise RuntimeError(f"LLM嵌入失败: {e}") 