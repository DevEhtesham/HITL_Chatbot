from fastapi import APIRouter, HTTPException
from langchain_core.messages import HumanMessage, ToolMessage
from app.models.schemas import ChatRequest, ChatResponse, ActionRequest
from app.services.agent import graph
import json

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    thread_id = req.thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    # Send user message
    messages = [HumanMessage(content=req.message)]
    
    # Run the graph
    for event in graph.stream({"messages": messages}, config, stream_mode="values"):
        pass # Wait for graph to finish or hit an interrupt
        
    state = graph.get_state(config)
    
    # Check if graph is interrupted
    if state.next and "tools" in state.next:
        last_msg = state.values["messages"][-1]
        tool_call = last_msg.tool_calls[0] if last_msg.tool_calls else None
        
        if tool_call:
            return ChatResponse(
                response="Action pending approval.",
                status="pending_approval",
                pending_tool=tool_call["name"],
                tool_args=tool_call["args"]
            )
            
    # If not interrupted, return the last agent message
    last_msg = state.values["messages"][-1]
    return ChatResponse(
        response=last_msg.content,
        status="completed"
    )

@router.post("/action", response_model=ChatResponse)
async def action_endpoint(req: ActionRequest):
    thread_id = req.thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    state = graph.get_state(config)
    
    if not state.next or "tools" not in state.next:
        raise HTTPException(status_code=400, detail="No pending actions for this thread.")
        
    last_msg = state.values["messages"][-1]
    
    if req.action == "approve":
        # Resume the graph, it will execute the tool
        for event in graph.stream(None, config, stream_mode="values"):
            pass
            
        final_state = graph.get_state(config)
        
        # Check if the graph interrupted again (e.g. model made another tool call)
        if final_state.next and "tools" in final_state.next:
            last_msg = final_state.values["messages"][-1]
            tool_call = last_msg.tool_calls[0] if last_msg.tool_calls else None
            if tool_call:
                return ChatResponse(
                    response="Action pending approval.",
                    status="pending_approval",
                    pending_tool=tool_call["name"],
                    tool_args=tool_call["args"]
                )
                
        final_msg = final_state.values["messages"][-1]
        return ChatResponse(
            response=final_msg.content,
            status="completed"
        )
        
    elif req.action == "reject":
        # Inject a rejection tool message into state to keep conversation history consistent
        tool_calls = last_msg.tool_calls
        if not tool_calls:
            raise HTTPException(status_code=400, detail="No tool calls found in the pending state.")
            
        tool_call_id = tool_calls[0]["id"]
        tool_name = tool_calls[0]["name"]
        
        rejection_msg = ToolMessage(
            content=f"User rejected the execution of '{tool_name}'.",
            tool_call_id=tool_call_id
        )
        
        # Update state with rejection (for memory consistency) but DO NOT run the LLM again.
        # Return a clean, hardcoded response directly to avoid the LLM misinterpreting the rejection.
        graph.update_state(config, {"messages": [rejection_msg]}, as_node="tools")
        
        return ChatResponse(
            response="Understood, I won't proceed with that action. Is there anything else I can help you with?",
            status="completed"
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'approve' or 'reject'.")
