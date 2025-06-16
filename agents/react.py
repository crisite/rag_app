from abc import abstractmethod
from typing import Any

class ReActMixin:
    """ReAct工作流程Mixin，提供think和act抽象方法"""
    
    @abstractmethod
    async def think(self) -> bool:
        """Process current state and decide next action"""

    @abstractmethod
    async def act(self) -> str:
        """Execute decided actions"""

    async def step(self) -> str:
        """Execute a single step: think and act.
        This method overrides the step method from BaseAgent.
        """
        should_act = await self.think()
        if not should_act:
            return "Thinking complete - no action needed"
        return await self.act() 