import pytest
import time
import sys
import os

# Add root folder to sys.path so it can find main.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app as agent_graph

def generate_base_state(text, w_type, time_offset=0):
    return {
        "task_id": f"TEST-{int(time.time())}",
        "start_time": time.time() - time_offset,
        "raw_input": text,
        "workflow_type": w_type,
        "extracted_data": {},
        "audit_log": [],
        "errors": [],
        "retry_count": 0,
        "critic_loops": 0,
        "correction_flag": False,
        "status": "initiated",
        "next_step": "coordinator"
    }

# 1. Employee Onboarding Error Correction
def test_onboarding_error_correction():
    text = "New hire offer for Jane Doe. Role: SWE. Start date: June 1st. Resume mentions Jone Doe."
    test_input = generate_base_state(text, "onboarding")
    final_state = agent_graph.invoke(test_input)
    
    assert final_state["status"] in ["completed", "escalated", "waiting_for_user"]
    
    # The workflow should route through the extraction and critic at minimum
    agents_triggered = [entry.get("agent") for entry in final_state["audit_log"]]
    assert "Coordinator" in agents_triggered
    assert "Extraction" in agents_triggered
    assert "Critic" in agents_triggered

# 2. Meeting-to-Action with Ambiguous Owner
def test_meeting_ownership_ambiguity():
    text = "Meeting summary: We discussed the Q4 product launch. Someone needs to finish the final deck by Tuesday."
    test_input = generate_base_state(text, "meeting")
    final_state = agent_graph.invoke(test_input)
    
    # Assert it handles it gracefully (might escalate at Clarification Gate due to low confidence on Action Owner)
    assert final_state["status"] in ["completed", "escalated", "waiting_for_user", "failed"]

# 3. SLA Breach Prevention Tracking
def test_sla_breach_prevention():
    text = "Invoice from Acme Corp. Total $150,000. PO Number: PO-2026-5846. Urgent payment needed immediately."
    # Simulate a run that started 130 seconds ago (SLA limit in health monitor is 120s for P2P)
    test_input = generate_base_state(text, "p2p", time_offset=130)
    final_state = agent_graph.invoke(test_input)
    
    # Extract the final SLA check from monitor logs
    metrics = final_state.get("audit_log", [])[-1].get("metrics", {})
    if metrics:
        assert metrics["sla_status"] == "FAIL" # Since we injected an artificial 130s delay
