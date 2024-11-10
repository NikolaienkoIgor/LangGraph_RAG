from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from typing import Dict, TypedDict, Optional, Literal
import re

load_dotenv()

# GraphState inherits from TypedDict
class GraphState(TypedDict):
    stateCustomerInput: Optional[str] = None
    stateExtractAmount: Optional[str] = None
    stateAccountantDecision: Optional[str] = None

# functions
def extractAmountFunc(state: GraphState) -> Dict[str, str]:
    print("""starting extractAmountFunc function""")
    extractAmount = state.get("stateCustomerInput", "").strip()
    extractAmount = int(re.search(r'\d+', extractAmount).group())
    return {"stateExtractAmount": extractAmount}

def accountantDecisionFunc(state: GraphState) -> Dict[str, str]:
    print("""starting accountantDecisionFunc function""")
    amount = state.get("stateExtractAmount")
    
    # Validate amount is an integer and greater than 0
    if isinstance(amount, int) and amount > 1:
        return {"stateAccountantDecision": "booking_approved"}
    else:
        return {"stateAccountantDecision": "booking_rejected"}

def continue_next(state: GraphState,) ->  Literal["to_input_second"]:
    print(f"starting continue_next function with current state: {state}")
    if state.get("stateAccountantDecision") == None:
        print("decision to continue with 2_node_accountantDecision")
        return "TO_2_node_accountantDecision"

workflow = StateGraph(GraphState)
workflow.add_node("1_node_extractAmount", extractAmountFunc)
workflow.add_node("2_node_accountantDecision", accountantDecisionFunc)

workflow.set_entry_point("1_node_extractAmount")
workflow.add_edge("2_node_accountantDecision", END)

workflow.add_conditional_edges(
    "1_node_extractAmount", 
    continue_next, 
    {"TO_2_node_accountantDecision": "2_node_accountantDecision"}
)

app = workflow.compile()

user_input = input("Please enter the amount: ") + str(" $")
result = app.invoke({"stateCustomerInput": user_input})
print("Result:" + str(result))