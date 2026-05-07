from app.services.agent import graph

config = {"configurable": {"thread_id": "thread_123"}}
state = graph.get_state(config)
for message in state.values["messages"]:
    print(f"{message.type}: {message.content}")
