import time
from state import AgentState

def monitor_agent(state: AgentState):
    print("--- 📉 AGENT 6: FINAL HEALTH & SLA AUDIT ---")
    
    current_logs = state.get("audit_log", [])
    corrections = state.get("correction_flag", False)
    status = state.get("status", "unknown")
    w_type = state.get("workflow_type", "general")
    errors = state.get("errors", [])

    # -------------------------
    # 1. AUTONOMY SCORE (Numeric for Graphing)
    # -------------------------
    if status == "completed":
        # 100 if perfect, 90 if it required FAISS self-healing
        autonomy_score = 90 if corrections else 100
    elif status in ["escalated", "waiting_for_user"]:
        autonomy_score = 50
    elif status == "failed":
        autonomy_score = 0
    else:
        autonomy_score = 10  # Unknown/Partial state

    # -------------------------
    # 2. SLA TRACKING (Robust Logic)
    # -------------------------
    start_time = state.get("start_time")
    # If start_time is missing, we default to 0 to avoid false "Fast" results
    processing_time_sec = time.time() - start_time if start_time else 0
    
    sla_limit = 120 if w_type in ["p2p", "onboarding"] else 60
    # Must be > 0 to be a valid measurement
    sla_compliant = 0 < processing_time_sec < sla_limit

    # -------------------------
    # 3. ROI CALCULATION
    # -------------------------
    manual_cost = 25.00
    ai_cost = 0.15 
    savings = manual_cost - ai_cost if status == "completed" else 0.00

    # -------------------------
    # 4. FINAL LOG ENTRY (Clean Data)
    # -------------------------
    log_entry = {
        "agent": "Health Monitor",
        "event": "System Performance Audit",
        "metrics": {
            "workflow": w_type,
            "autonomy_score": autonomy_score, # Pure Number
            "sla_status": "PASS" if sla_compliant else "FAIL",
            "processing_time_sec": round(processing_time_sec, 2),
            "net_savings_usd": round(savings, 2),
            "self_healed_flag": corrections,
            "error_count": len(errors)
        },
        "timestamp": time.time()
    }

    # -------------------------
    # 5. CONSOLE REPORT (Clean Formatting)
    # -------------------------
    print(
        f"📊 REPORT: {w_type.upper()} | "
        f"Autonomy: {autonomy_score}% | "
        f"Saved: ${round(savings, 2)} | "
        f"Time: {round(processing_time_sec, 2)}s"
    )

    # -------------------------
    # 6. FINAL STATE RETURN
    # -------------------------
    return {
        "status": status,
        "current_agent": "Monitor",
        "next_step": "end",
        "audit_log": current_logs + [log_entry]
    }