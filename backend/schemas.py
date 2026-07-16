from enum import Enum
from pydantic import BaseModel, Field


class ToolName(str, Enum):
    web_search = "web_search"
    calculator = "calculator"
    finish = "finish"


class AgentAction(BaseModel):
    thought: str = Field(..., description="Brief reasoning for this action")
    tool: ToolName
    tool_input: str