from langgraph.graph import StateGraph, START, END
from typing import TypedDict
from agent_tools.get_key import get_key
from agent_tools.send_key import sendCodeTest
from agent_tools.get_youtube_query import get_youtube_query
from agent_tools.get_youtube_link import get_youtube_link
from agent_tools.send_link import sendLinkTest
from agent_tools.get_platform import get_tvshow_plattform
from agent_tools.get_recommendations import get_recommendations
from agent_tools.set_show import setShowName
from agent_tools.planner import planner
import asyncio
from typing import Optional

# Creating state For the agent
class TVAgentState(TypedDict):
    current_task: str
    current_task_command: Optional[str]
    repeat: int
    youtube_query: str
    app_link: str
    status: str
    show_name: str
    target_show_name: str
    recommendations: list
    platform_info: list
    edges: list
    task_number: int

# async funtion configuration
def run_send_code(state):
    return asyncio.run(sendCodeTest(state))
def run_send_link(state):
    return asyncio.run(sendLinkTest(state))

# Create state graph
graph = StateGraph(TVAgentState)

# add nodes to the graph
graph.add_node('planner', planner) # get key code
graph.add_node('get_key', get_key) # get key code
graph.add_node('set_show_name', setShowName) # set show name
graph.add_node('send_code', run_send_code) # send key code
graph.add_node('get_youtube_query', get_youtube_query) # get youtube query
graph.add_node('get_youtube_link', get_youtube_link) # get youtube link
graph.add_node('send_link', run_send_link) # send link
graph.add_node('get_platform', get_tvshow_plattform) # get platform info
graph.add_node('get_recommendations', get_recommendations) # get recommendations

# edge creation logic
def route_next_step(state):
    task_number = state['task_number']
    steps = state['edges']
    return steps[task_number]


# Corrected edge creation logic
def route_next_step(state: TVAgentState):
    task_number = state['task_number']
    steps = state['edges']

    if task_number < len(steps):
        next_node = steps[task_number]
        # Increment task_number for the *next* time route_next_step is called
        # This update needs to be captured by the graph
        state['task_number'] += 1
        return next_node
    else:
        return END

# add edges to the graph
graph.add_edge(START, 'planner')

# The planner determines the initial sequence.
# After planner, we use route_next_step to transition to the first task.
graph.add_conditional_edges(
    'planner',
    route_next_step,
    # This dictionary maps the output of route_next_step to the actual node name.
    # Since route_next_step directly returns the node name, we list all possible node names.
    # LangGraph will automatically match the returned string to the node.
    # This is a more explicit way to define the mapping.
    # Alternatively, if route_next_step just returned 'get_key', LangGraph would look for a node named 'get_key'.
    # This setup is useful if route_next_step had more complex conditions that might lead to different paths.
    # However, for simply executing 'steps[task_number]', listing all nodes is a common pattern.
    {"get_key": "get_key",
     "set_show_name": "set_show_name",
     "send_code": "send_code",
     "get_youtube_query": "get_youtube_query",
     "get_youtube_link": "get_youtube_link",
     "send_link": "send_link",
     "get_platform": "get_platform",
     "get_recommendations": "get_recommendations",
     END: END # Ensure END is also a possible return from route_next_step
    }
)

# Now, for every functional node that *could* be part of a multi-step plan,
# we add a conditional edge back to `route_next_step`.
# This ensures the graph continues executing the planned steps.

edge_variable = {"get_key": "get_key", "set_show_name": "set_show_name", "send_code": "send_code",
     "get_youtube_query": "get_youtube_query", "get_youtube_link": "get_youtube_link",
     "send_link": "send_link", "get_platform": "get_platform",
     "get_recommendations": "get_recommendations", END: END}

graph.add_conditional_edges(
    'get_key',
    route_next_step,
    edge_variable
)
graph.add_conditional_edges(
    'set_show_name',
    route_next_step,
    edge_variable
)
graph.add_conditional_edges(
    'send_code',
    route_next_step,
    edge_variable
)
graph.add_conditional_edges(
    'get_youtube_query',
    route_next_step,
    edge_variable
)
graph.add_conditional_edges(
    'get_youtube_link',
    route_next_step,
    edge_variable
)
graph.add_conditional_edges(
    'send_link',
    route_next_step,
    edge_variable
)
graph.add_conditional_edges(
    'get_platform',
    route_next_step,
    edge_variable
)
graph.add_conditional_edges(
    'get_recommendations',
    route_next_step,
    edge_variable
)

app = graph.compile()

if __name__ == "__main__":
    initial_state = {"current_task": "i want to watch game of thronse", "task_number": 0}
    result = app.invoke(initial_state)
    print(result)