from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
import sqlite3
import os

from app.services.tools import tools_list

class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Create database for checkpointer
db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'checkpoints.sqlite')
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)
memory.setup()

# Use Groq for open source model
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
llm_with_tools = llm.bind_tools(tools_list)

tool_node = ToolNode(tools_list)

sys_msg = SystemMessage(content="You are a professional AI assistant. Your job is to help users crawl GitHub and LinkedIn data. When a tool returns data, you MUST present ALL of it clearly and in detail. Do NOT skip any information.")

def chatbot(state: State):
    messages = [sys_msg] + state["messages"]
    
    # Dynamic forceful reminder based on which tool was just called
    if messages[-1].type == "tool":
        tool_name = messages[-1].name
        if tool_name == "github_repo_crawl":
            messages.append(HumanMessage(content="I have the GitHub data above. I will now present ALL details (Description, Stars, Forks, Language, and README snippet) to the user exactly as they appear."))
        elif tool_name == "linkedin_profile_crawl":
            messages.append(HumanMessage(content="I have the LinkedIn data above. I will now present ALL details (Name, Headline, Location, Current Position, Experience History, and Skills) to the user exactly as they appear."))

    response = llm_with_tools.invoke(messages)
    print(f"DEBUG - Agent Output: {response.content}")
    return {"messages": [response]}

graph_builder = StateGraph(State)
graph_builder.add_node("agent", chatbot)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "agent")

# We want to conditionally go to tools if the agent returns a tool call
def should_continue(state: State):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", END: END}
)

graph_builder.add_edge("tools", "agent")

# Compile with interrupt before tools
graph = graph_builder.compile(
    checkpointer=memory,
    interrupt_before=["tools"]
)
