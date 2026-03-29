import time
from state import AgentState
from tools.verification_tools import universal_fuzzy_search

def matching_agent(state: AgentState):
    w_type = state.get("workflow_type", "meeting")
    extracted = state.get("extracted_data", {})
    current_logs = state.get("audit_log", [])
    
    print(f"--- 🤖 AGENT 3: STARTING UNIVERSAL MATCHING ({w_type.upper()}) ---")

    # 1. DYNAMIC TARGET SELECTION
    # If P2P -> we heal the PO. If Onboarding -> we heal the Name.
    if w_type == "p2p":
        target_field = "po_number"
    elif w_type == "onboarding":
        target_field = "candidate"
    else:
        # For meetings or general tasks, no healing registry exists
        return {
            "status": "processing",
            "current_agent": "Matching",
            "next_step": "critic",
            "audit_log": [{"agent": "Matching", "event": "Skipped", "details": f"No matching registry for {w_type}."}]
        }

    query_value = extracted.get(target_field, "")

    # 2. SKIP IF DATA IS MISSING
    if not query_value:
        return {
            "status": "processing",
            "current_agent": "Matching",
            "next_step": "critic",
            "audit_log": [{"agent": "Matching", "event": "Skipped", "details": f"Target field '{target_field}' empty."}]
        }

    # 3. CALL UNIVERSAL FAISS TOOL
    try:
        result = universal_fuzzy_search.invoke({
            "query": query_value,
            "workflow_type": w_type
        })
    except Exception as e:
        return {
            "status": "failed",
            "next_step": "end",
            "errors": state.get("errors", []) + [str(e)],
            "audit_log": []
        }

    best_match = result.get("match")
    confidence = result.get("confidence", 0.0)
    matched_value = result.get("match", query_value)

    # 4. SELF-HEALING DECISION LOGIC
    if result.get("exact"):
        event = "Exact Match Verified"
        new_data = extracted
        correction = False
    elif confidence > 0.85:
        event = "Self-Correction Applied (FAISS)"
        new_data = extracted.copy()
        new_data[target_field] = matched_value # THE HEAL happens here
        correction = True
    else:
        # Escalation path for low confidence
        return {
            "status": "escalated",
            "current_agent": "Matching",
            "next_step": "clarification_gate",
            "audit_log": [{
                "agent": "Matching",
                "event": "Match Failed",
                "details": f"Low confidence for {query_value} ({confidence*100:.1f}%)",
                "timestamp": time.time()
            }]
        }

    # 5. LOG SUCCESS
    log_entry = {
        "agent": "Matching",
        "event": event,
        "details": f"{query_value} ➔ {matched_value} ({confidence*100:.2f}%)",
        "timestamp": time.time()
    }

    return {
        "extracted_data": new_data,
        "correction_flag": state.get("correction_flag", False) or correction,
        "status": "processing",
        "current_agent": "Matching",
        "next_step": "critic",
        "audit_log": [log_entry]
    }