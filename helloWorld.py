from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from typing import Dict, TypedDict, Optional, Literal

load_dotenv()

# GraphState inherits from TypedDict
class GraphState(TypedDict):
    init_input: Optional[str] = None
    first_word: Optional[str] = None
    second_word: Optional[str] = None
    final_result: Optional[str] = None

# functions
def input_first(state: GraphState) -> Dict[str, str]:
    print("""starting input_first function""")
    init_input = state.get("init_input", "").strip()
    if init_input != "hello":
        return {"first_word": "error"}
    return {"first_word": "hello"}
def input_second(state: GraphState) -> Dict[str, str]:
    print("""starting input_second function""")
    if state.get("first_word") == "error":
        {"second_word": "error"}
    return {"second_word": "world"}
def complete_word(state: GraphState) -> Dict[str, str]:
    print("""starting complete_word function""")
    if state.get("first_word") == "error" or state.get("second_word") == "error":
        return {"final_result": "error"}
    return {"final_result": state["first_word"] + ", " + state["second_word"] + "!"}
def error(state: GraphState) -> Dict[str, str]:
    print("""starting error function""")
    return {"final_result": "error", "first_word": "error", "second_word": "error"}

# Decision function
def continue_next(state: GraphState,) ->  Literal["to_input_second", "to_error"]:
    print(f"starting continue_next function with current state: {state}")
    if state.get("first_word") == "hello" and state.get("second_word") == None:
        print("decision to continue with to_input_second value")
        return "to_input_second"

    if (
        state.get("first_word") == "error"
        or state.get("second_word") == "error"
        or state.get("final_result") == "error"
    ):
        print("decision to continue with to_error value")
        return "to_error" 
    
# workflow is created as an instance of StateGraph, 
# which uses GraphState as its type parameter
workflow = StateGraph(GraphState)

workflow.add_node("input_first", input_first)
workflow.add_node("input_second", input_second)
workflow.add_node("complete_word", complete_word)
workflow.add_node("error", error)

workflow.set_entry_point("input_first")
workflow.add_edge("input_second", "complete_word")
workflow.add_edge("complete_word", END)
workflow.add_edge("error", END)

workflow.add_conditional_edges(
    "input_first",          # Source node
    continue_next,          # Decision function
    {                       # Mapping of decision results to next nodes
        "to_input_second": "input_second",
        "to_error": "error",
    },
)

app = workflow.compile()

result = app.invoke({"init_input": "hello"})
print("Result:")
print(result)