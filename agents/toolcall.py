import importlib
from typing import Dict, Any, Type
import tomli

from agents.base_agent import BaseAgent # 导入BaseAgent，用于类型提示

class ToolCall:
    """AI代理调用管理类"""
    
    def __init__(self, config_path: str = "config/config.toml"):
        """
        初始化ToolCall
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.agent_map = self.config.get("agents", {}).get("supported_agents", {})

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """加载配置文件"""
        with open(config_path, "rb") as f:
            return tomli.load(f)

    def get_agent_class(self, agent_type: str) -> Type[BaseAgent]:
        """
        根据代理类型获取代理类
        
        Args:
            agent_type: 代理类型字符串 (例如: "embedding")
            
        Returns:
            Type[BaseAgent]: 代理类
            
        Raises:
            ValueError: 如果代理类型不支持或加载失败
        """
        agent_config = self.agent_map.get(agent_type)
        if not agent_config:
            raise ValueError(f"不支持的代理类型: {agent_type}")

        module_name = agent_config["module"]
        class_name = agent_config["class"]

        try:
            # 动态导入模块，例如 agents.embedding_agent
            module = importlib.import_module(f"agents.{module_name}")
            # 从模块中获取类，例如 EmbeddingAgent
            agent_class = getattr(module, class_name)
            if not issubclass(agent_class, BaseAgent):
                raise TypeError(f"代理类 {class_name} 必须继承自 BaseAgent")
            return agent_class
        except (ImportError, AttributeError, TypeError) as e:
            raise ValueError(f"加载代理 {agent_type} 失败: {e}")

    def get_agent_instance(self, agent_type: str, **kwargs) -> BaseAgent:
        """
        根据代理类型获取代理实例
        
        Args:
            agent_type: 代理类型字符串
            **kwargs: 传递给代理类构造函数的额外参数
            
        Returns:
            BaseAgent: 代理实例
        """
        agent_class = self.get_agent_class(agent_type)
        return agent_class(**kwargs)

    async def execute_agent(self, agent_type: str, request: str, **kwargs) -> str:
        """
        执行指定类型的AI代理的run方法
        
        Args:
            agent_type: 代理类型字符串
            request: 传递给代理run方法的请求字符串
            **kwargs: 传递给代理类构造函数的额外参数
            
        Returns:
            str: 代理执行结果
        """
        agent = self.get_agent_instance(agent_type, **kwargs)
        return await agent.run(request) 