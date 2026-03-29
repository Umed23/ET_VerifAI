import time
from state import AgentState
from tools.compliance_tools import check_vendor_approval, check_budget, check_hr_policy

def compliance_agent(state: AgentState):
    print(f"--- ⚖️ AGENT 4: STARTING {state['workflow_type'].upper()} AUDIT ---")
    
    w_type = state.get("workflow_type")
    extracted = state.get("extracted_data", {})
    current_logs = state.get("audit_log", [])
    violations = []

    try:
        # -------------------------
        # P2P (Finance)
        # -------------------------
        if w_type == "p2p":
            vendor = extracted.get("vendor", "")
            amount = extracted.get("amount", 0)
            
            if vendor:
                is_approved = check_vendor_approval.invoke({"vendor": vendor})
                if not is_approved:
                    violations.append(f"Unapproved Vendor: {vendor}")
                    
            if amount > 0:
                budget_info = check_budget.invoke({"amount": amount})
                if not budget_info.get("approved", False):
                    violations.append("Insufficient Budget limit")

        # -------------------------
        # ONBOARDING (HR)
        # -------------------------
        elif w_type == "onboarding":
            candidate = extracted.get("candidate_name")
            
            if candidate:
                policy_check = check_hr_policy.invoke({"candidate": candidate})
                if not policy_check.get("eligible"):
                    violations.append(f"HR Policy Violation: {policy_check.get('reason')}")

        # -------------------------
        # DEFAULT (Skip)
        # -------------------------
        else:
            log_entry = {
                "agent": "Compliance",
                "event": "Skipped",
                "details": f"No rules for {w_type}",
                "timestamp": time.time()
            }
            return {
                "status": "processing",
                "current_agent": "Compliance",
                "next_step": "execution",
                "audit_log": [log_entry]
            }

    except Exception as e:
        return {
            "status": "failed",
            "current_agent": "Compliance",
            "next_step": "end",
            "errors": state.get("errors", []) + [str(e)],
            "audit_log": current_logs
        }

    # -------------------------
    # RISK CHECK (Upgrade)
    # -------------------------
    if state.get("risk_score", 0) > 0.8:
        violations.append("High Risk Transaction")

    # -------------------------
    # DECISION
    # -------------------------
    if not violations:
        log_entry = {
            "agent": "Compliance",
            "event": "Audit Passed",
            "details": f"All {w_type} constraints verified successfully.",
            "timestamp": time.time()
        }
        return {
            "status": "processing",
            "current_agent": "Compliance",
            "next_step": "execution",
            "audit_log": [log_entry]
        }

    log_entry = {
        "agent": "Compliance",
        "event": "Audit Failed",
        "details": f"Violations: {', '.join(violations)}",
        "timestamp": time.time()
    }

    return {
        "status": "escalated",
        "current_agent": "Compliance",
        "next_step": "clarification_gate",
        "errors": state.get("errors", []) + violations,
        "audit_log": [log_entry]
    }