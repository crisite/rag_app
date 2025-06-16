from enum import Enum
from typing import Literal

class AgentState(str, Enum):
    """代理的当前状态"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"
    ERROR = "error"
    
ROLE_TYPE = Literal["user", "system", "assistant", "tool"] 