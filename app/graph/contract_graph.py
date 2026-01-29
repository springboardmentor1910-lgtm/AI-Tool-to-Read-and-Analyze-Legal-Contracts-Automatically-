from langgraph.graph import StateGraph

def planner(state):
    return state

graph = StateGraph(dict)
graph.add_node("planner", planner)
graph.set_entry_point("planner")

contract_graph = graph.compile()
