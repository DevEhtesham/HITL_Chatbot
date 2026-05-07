from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    message: str
    thread_id: str

class ChatResponse(BaseModel):
    response: str
    status: str
    pending_tool: Optional[str] = None
    tool_args: Optional[Dict[str, Any]] = None

class ActionRequest(BaseModel):
    action: str  # 'approve' or 'reject'
    thread_id: str
