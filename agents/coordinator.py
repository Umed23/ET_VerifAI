import re
import uuid
import time
from state import AgentState

def coordinator_agent(state: AgentState):
    print("--- 🤖 AGENT 1: STARTING COORDINATION & ROUTING ---")

    if not state.get("raw_input"):
        return {"error": "No input provided"}

    text = state["raw_input"].lower()

    # look for numbers that follow a currency symbol or are > 3 digits
    amounts = re.findall(r'(?:₹|\$|rs\.?|usd)\s*(\d[\d,]*)', text)
    amounts = [int(a.replace(',', '')) for a in amounts]
    max_amount = max(amounts) if amounts else 0

# Classification Logic (Expanded)
    if any(k in text for k in ["invoice", "total", "po#", "billing"]):
        w_type = "p2p"
        confidence = 0.9
    elif any(k in text for k in ["hire", "onboarding", "offer", "candidate"]):
        w_type = "onboarding"
        confidence = 0.9
    elif any(k in text for k in ["contract", "nda", "agreement", "clause"]):
        w_type = "legal"
        confidence = 0.85
    elif any(k in text for k in ["reimbursement", "travel", "receipt", "expense"]):
        w_type = "expense"
        confidence = 0.88
    else:
        w_type = "meeting"
        confidence = 0.6

    # Risk scoring (dynamic)
    risk = min(1.0, 0.3 + (max_amount / 50000))
    if any(k in text for k in ["urgent", "critical", "immediate"]):
        risk += 0.2
    risk = min(risk, 1.0)

    # Model routing
    selected_llm = "Claude-3-Opus" if risk > 0.8 else "Claude-3-Haiku"

    log_entry = {
        "agent": "Coordinator",
        "event": "Workflow Routed",
        "details": f"{w_type} | Risk: {risk:.2f} | Model: {selected_llm}",
        "timestamp": time.time()
    }

    return {
        "task_id": str(uuid.uuid4())[:8],
        "workflow_type": w_type,
        "risk_score": risk,
        "confidence": confidence,
        "selected_llm": selected_llm,
        "current_agent": "Extraction",
        "next_step": "extraction",
        "audit_log": [log_entry]
    }