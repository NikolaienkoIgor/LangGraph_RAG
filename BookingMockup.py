from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from typing import Dict, TypedDict, Optional, Literal
import re
import streamlit as st

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
    decision = st.session_state.get('accountant_decision', None)
    return {"stateAccountantDecision": decision}

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

# Modify the Streamlit interface section
if 'page' not in st.session_state:
    st.session_state.page = 'user_input'
    st.session_state.workflow_result = None
    st.session_state.accountant_decision = None

if st.session_state.page == 'user_input':
    name_input = st.text_input("Please enter your name:", "")
    amount_input = st.text_input("Please enter the amount in $:", "")

    user_input = amount_input + str(" $") if amount_input else ""

    if st.button("Enter"):
        if amount_input:
            result = app.invoke({"stateCustomerInput": user_input})
            st.session_state.workflow_result = result
            st.session_state.page = 'accountant_review'
            st.rerun()

elif st.session_state.page == 'accountant_review':
    st.write("Review Booking Request")
    st.write("Amount:", st.session_state.workflow_result.get("stateExtractAmount"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Confirm"):
            st.session_state.accountant_decision = "booking_approved"
            st.session_state.workflow_result = app.invoke(st.session_state.workflow_result)
            st.session_state.page = 'final_status'
            st.rerun()
            
    with col2:
        if st.button("Reject"):
            st.session_state.accountant_decision = "booking_rejected"
            st.session_state.workflow_result = app.invoke(st.session_state.workflow_result)
            st.session_state.page = 'final_status'
            st.rerun()

elif st.session_state.page == 'final_status':
    amount = st.session_state.workflow_result.get("stateExtractAmount")
    
    if st.session_state.accountant_decision == "booking_approved":
        st.success(f"Amount ${amount} has been successfully booked!")
    else:
        st.error(f"Amount ${amount} has been rejected.")
    
    # Add both print and streamlit display of the result
    print("Final Graph Execution Result:", st.session_state.workflow_result)
    st.write("Graph Execution Result:", st.session_state.workflow_result)
    
    if st.button("Start New Booking"):
        st.session_state.page = 'user_input'
        st.session_state.workflow_result = None
        st.session_state.accountant_decision = None
        st.rerun()