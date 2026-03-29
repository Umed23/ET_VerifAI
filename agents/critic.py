import time
from state import AgentState

def critic_agent(state: AgentState):
    """
    Agent 7: Critic & Supervisor
    Cross-examines the output of Extraction and Matching before Compliance.
    Provides hierarchical reflexion loops.
    """
    print(f"--- 🧐 AGENT 7: CRITIC/SUPERVISOR REVIEW ({state.get('workflow_type', 'UNKNOWN').upper()}) ---")
    
    current_logs = state.get("audit_log", [])
    extracted = state.get("extracted_data", {})
    confidence = state.get("confidence_score", 0.0)
    w_type = state.get("workflow_type", "unknown")
    loops = state.get("critic_loops", 0)
    
    # 1. Anti-Infinite Loop Protection
    max_loops = 2
    if loops >= max_loops:
        log_entry = {
            "agent": "Critic",
            "event": "Loop Limit Reached",
            "details": f"Forcing workflow forward after {max_loops} critique loops.",
            "timestamp": time.time()
        }
        return {
            "status": "processing",
            "next_step": "compliance", 
            "current_agent": "Critic",
            "audit_log": [log_entry]
        }
        
    # 2. Evaluation Logic
    missing_fields = []
    if w_type == "p2p" and not extracted.get("po_number"):
        missing_fields.append("po_number")
    elif w_type == "onboarding" and not extracted.get("candidate_name"):
        missing_fields.append("candidate_name")
        
    # Example heuristic: if data is missing or confidence is mediocre, push back to extraction
    passed = len(missing_fields) == 0 and confidence > 0.65
    
    if passed:
        log_entry = {
            "agent": "Critic",
            "event": "Review Passed",
            "details": f"Data Integrity Verified. Confidence: {confidence*100:.1f}%",
            "timestamp": time.time()
        }
        return {
            "status": "processing",
            "next_step": "compliance", 
            "current_agent": "Critic",
            "audit_log": [log_entry]
        }
    else:
        feedback = f"Critic found missing critical fields: {missing_fields}. Refine extraction logic."
        log_entry = {
            "agent": "Critic",
            "event": "Review Failed",
            "details": f"Routing back to Extraction. Feedback: {feedback}",
            "timestamp": time.time()
        }
        return {
            "status": "processing",
            "next_step": "extraction", 
            "current_agent": "Critic",
            "critic_loops": loops + 1,
            "critic_feedback": feedback,
            "audit_log": [log_entry]
        }
