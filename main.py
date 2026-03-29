import os
from dotenv import load_dotenv
load_dotenv()

import sys
import time
from langgraph.graph import StateGraph, END
from state import AgentState

# Import all agents
from agents.coordinator import coordinator_agent
from agents.extraction import extraction_agent
from agents.matching import matching_agent
from agents.compliance import compliance_agent
from agents.execution import execution_agent
from agents.health_monitor import monitor_agent
from agents.critic import critic_agent

import os
# Enable LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "VerifAI-Agent"

# --- ✋ CLARIFICATION GATE (Human-in-the-Loop) ---
def clarification_gate(state: AgentState):
    print("--- ✋ CLARIFICATION GATE: Human Review Required ---")
    
    current_logs = state.get("audit_log", [])
    errors = state.get("errors", [])
    
    log_entry = {
        "agent": "Clarification Gate",
        "event": "Escalated",
        "details": f"Paused for human review due to: {', '.join(errors) if errors else 'Low confidence'}",
        "timestamp": time.time()
    }
    
    # We return the escalated status so the monitor can report it
    return {
        "audit_log": [log_entry], 
        "status": "escalated",
        "next_step": "monitor"
    }

# ==========================================
# 1. BUILD THE DYNAMIC WORKFLOW
# ==========================================
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("coordinator", coordinator_agent)
workflow.add_node("extraction", extraction_agent)
workflow.add_node("matching", matching_agent)
workflow.add_node("critic", critic_agent)
workflow.add_node("compliance", compliance_agent)
workflow.add_node("execution", execution_agent)
workflow.add_node("clarification_gate", clarification_gate)
workflow.add_node("monitor", monitor_agent)

# --- Define Edges & Conditional Routing ---

workflow.set_entry_point("coordinator")
workflow.add_edge("coordinator", "extraction")

# Router logic: Checks if the previous agent flagged an escalation
def router(state: AgentState):
    if state.get("status") in ["escalated", "failed"]:
        return "clarification_gate"
    return state.get("next_step", "end")

workflow.add_conditional_edges("extraction", router, {
    "matching": "matching",
    "clarification_gate": "clarification_gate",
    "end": END
})

workflow.add_conditional_edges("matching", router, {
    "critic": "critic",
    "clarification_gate": "clarification_gate",
    "end": END
})

workflow.add_conditional_edges("critic", router, {
    "extraction": "extraction",
    "compliance": "compliance",
    "clarification_gate": "clarification_gate",
    "end": END
})

workflow.add_conditional_edges("compliance", router, {
    "execution": "execution",
    "clarification_gate": "clarification_gate",
    "end": END
})

workflow.add_conditional_edges("execution", router, {
    "monitor": "monitor",
    "clarification_gate": "clarification_gate",
    "end": END
})

# Both paths eventually lead to Execution/Monitor for persistence and ROI
workflow.add_edge("clarification_gate", "execution")
workflow.add_edge("monitor", END)

app = workflow.compile()

# ==========================================
# 2. UI COLORS & DEMO SCRIPT
# ==========================================
class CLR:
    HEADER, OKBLUE, OKCYAN = '\033[95m', '\033[94m', '\033[96m'
    OKGREEN, WARNING, FAIL = '\033[92m', '\033[93m', '\033[91m'
    ENDC, BOLD = '\033[0m', '\033[1m'

if __name__ == "__main__":
    print(f"{CLR.OKCYAN}{CLR.BOLD}{'='*70}\n🛡️  VERIFAI: 6-AGENT AUTONOMOUS ORCHESTRATOR\n{'='*70}{CLR.ENDC}")
    
    # Simulation: Invoice with a typo to trigger FAISS
    test_input = {
        "task_id": f"DEMO-{int(time.time())}",
        "start_time": time.time(),
        "raw_input": "Invoice from Acme Corp. Total $1250. PO Number: PO-2026-5846",
        "workflow_type": "p2p",
        "extracted_data": {},
        "audit_log": [],
        "errors": [],
        "retry_count": 0,
        "correction_flag": False,
        "status": "initiated"
    }
    
    print(f"\n{CLR.HEADER}📥 INPUT DOC:{CLR.ENDC} {test_input['raw_input']}")
    print(f"{CLR.WARNING}🔄 ORCHESTRATING AGENTS...{CLR.ENDC}\n")
    
    final_state = app.invoke(test_input)
    
    # --- Final Presentation Display ---
    print(f"\n{CLR.OKGREEN}{CLR.BOLD}{'='*70}\n🏆 CHAMPIONSHIP SUMMARY\n{'='*70}{CLR.ENDC}")
    
    status = final_state.get('status', 'unknown').upper()
    s_clr = CLR.OKGREEN if status == "COMPLETED" else CLR.WARNING if status == "ESCALATED" else CLR.FAIL
    
    print(f"STATUS: {s_clr}{status}{CLR.ENDC}")
    print(f"WORKFLOW: {final_state.get('workflow_type', 'N/A').upper()}")
    
    # 🏥 Self-Healing Proof
    if final_state.get('correction_flag'):
        print(f"{CLR.OKCYAN}✨ SELF-HEALING: Applied (Semantic FAISS Correction){CLR.ENDC}")

    # 📊 Metrics (From Agent 6)
    metrics = final_state.get('audit_log', [])[-1].get('metrics', {})
    if metrics:
        print(f"\n{CLR.BOLD}📊 PERFORMANCE METRICS:{CLR.ENDC}")
        print(f"  • Autonomy: {metrics.get('autonomy_score')}%")
        print(f"  • Savings: ${metrics.get('net_savings_usd')}")
        print(f"  • Speed: {metrics.get('processing_time_sec')}s")

    # 📑 Audit Trail
    print(f"\n{CLR.BOLD}📑 AUDIT TRAIL:{CLR.ENDC}")
    for i, entry in enumerate(final_state.get('audit_log', []), 1):
        print(f"  {i}. [{entry.get('agent')}] -> {entry.get('event')}")

    print(f"\n{CLR.OKGREEN}{CLR.BOLD}{'='*70}{CLR.ENDC}")