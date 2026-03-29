import time
import logging
from state import AgentState
from tools.extraction_tools import extract_entity_data

logger = logging.getLogger(__name__)

def extraction_agent(state: AgentState):
    """
    Agent 2: Entity Extraction & Validation Gate
    Maintains full state history and prepares data for Matching.
    """
    # 1. Pull Context from Shared State
    w_type = state.get("workflow_type", "meeting")
    text = state.get("raw_input", "")
    model = state.get("selected_llm", "gemini-2.0-pro")

    print(f"--- 🔍 AGENT 2: EXTRACTING {w_type.upper()} DATA USING {model} ---")

    # 2. Define Business Rules for Validation
    validation_map = {
        "p2p": ["vendor", "amount", "po_number"],
        "onboarding": ["candidate", "role", "start_date"],
        "legal": ["contract_type", "expiry_date"],
        "meeting": ["summary", "action_items"]
    }
    required_fields = validation_map.get(w_type, [])

    # 3. Execute AI Extraction
    try:
        tool_result = extract_entity_data.invoke({
            "text": text,
            "workflow_type": w_type,
            "model": model
        })

        extracted = tool_result.get("extracted", {})
        confidence = tool_result.get("confidence", 0.0)

    except Exception as e:
        logger.error(f"Extraction Agent Failed: {str(e)}")
        
        error_log = {
            "agent": "Extraction",
            "event": "Critical Error",
            "details": f"LLM Call Failed: {str(e)}",
            "timestamp": time.time()
        }

        # IMPORTANT: Append to previous logs, don't replace them
        # IMPORTANT: Append to previous errors but ONLY return new audit_log entry
        return {
            "status": "failed",
            "next_step": "end",
            "current_agent": "Extraction",
            "retry_count": state.get("retry_count", 0) + 1,
            "errors": state.get("errors", []) + [str(e)],
            "audit_log": [error_log]
        }

    # 4. Data Quality Gate (Missing Fields or Low Confidence)
    missing = [f for f in required_fields if f not in extracted or not extracted[f] or extracted[f] in ["UNKNOWN", "FAILURE", "ERROR"]]

    if confidence < 0.6 or missing:
        log_entry = {
            "agent": "Extraction",
            "event": "Data Quality Alert",
            "details": f"Missing: {missing} | Conf: {confidence*100:.1f}%",
            "timestamp": time.time()
        }

        return {
            "extracted_data": extracted,
            "confidence_score": confidence,
            "status": "escalated",
            "next_step": "clarification_gate",
            "current_agent": "Extraction",
            "audit_log": [log_entry]
        }

    # 5. Success Path (Maintain Audit Integrity)
    logger.info(f"Successfully parsed {w_type} document.")

    log_entry = {
        "agent": "Extraction",
        "event": "Structure Generated",
        "details": f"Parsed {len(extracted)} fields | Conf: {confidence*100:.1f}%",
        "timestamp": time.time()
    }

    return {
        "extracted_data": extracted,
        "confidence_score": confidence,
        "status": "processing",
        "current_agent": "Extraction",
        "next_step": "matching",
        "audit_log": [log_entry]
    }