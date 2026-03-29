import time
import json
import os
from state import AgentState
from tools.notification_tools import send_workflow_notification

def execution_agent(state: AgentState):
    """
    Agent 5: Final Execution & Delivery
    Handles DB updates and user notifications.
    """
    w_type = state.get("workflow_type", "meeting")
    status = state.get("status", "processing")
    extracted = state.get("extracted_data", {})
    current_logs = state.get("audit_log", [])
    errors = state.get("errors", [])

    user_email = extracted.get("email", "default@email.com")

    print(f"--- 🚀 AGENT 5: EXECUTING FINAL ACTIONS FOR {w_type.upper()} ---")

    # -------------------------------
    # SUCCESS PATH
    # -------------------------------
    if status == "processing":
        db_path = f"data/{w_type}_final_records.json"

        # 1. Database Update
        try:
            records = []
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    records = json.load(f)

            records.append({**extracted, "processed_at": time.time()})

            with open(db_path, 'w') as f:
                json.dump(records, f, indent=4)

        except Exception as e:
            errors.append(f"DB Error: {str(e)}")

        # 2. Send Email
        try:
            email_msg = f"""
Hello,

Your {w_type.upper()} request has been successfully processed.

Details:
{json.dumps(extracted, indent=2)}

Status: ACTIVE

Thank you for using VerifAI.
"""
            send_workflow_notification.invoke({
                "recipient_email": user_email,
                "subject": f"✅ VerifAI: {w_type.upper()} Processed",
                "message": email_msg
            })

        except Exception as e:
            errors.append(f"Email Error: {str(e)}")

        log_entry = {
            "agent": "Execution",
            "event": "Completed",
            "details": f"Processed and notified {user_email}",
            "timestamp": time.time()
        }

        final_status = "completed"

    # -------------------------------
    # FAILURE / ESCALATION
    # -------------------------------
    else:
        # Save to DB even in failure path so it shows up in "everything"
        db_path = f"data/{w_type}_final_records.json"
        try:
            records = []
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    records = json.load(f)
            
            # Label as 'incomplete' or 'escalated' in the DB
            records.append({**extracted, "processed_at": time.time(), "system_status": "ESCALATED"})
            with open(db_path, 'w') as f:
                json.dump(records, f, indent=4)
        except Exception as e:
            errors.append(f"DB Draft Save Error: {str(e)}")

        if not errors:
            errors = ["Missing or invalid data"]

        try:
            error_msg = f"""
Hello,

We could not process your {w_type.upper()} request.

Issues:
{chr(10).join(['* ' + e for e in errors])}

Please correct and re-upload.

Ref: VerifAI-{int(time.time())}
"""
            send_workflow_notification.invoke({
                "recipient_email": user_email,
                "subject": "⚠️ Action Required",
                "message": error_msg
            })

        except Exception as e:
            errors.append(f"Email Error: {str(e)}")

        log_entry = {
            "agent": "Execution",
            "event": "User Notified",
            "details": f"Sent correction email to {user_email}",
            "timestamp": time.time()
        }

        final_status = "waiting_for_user"

    # -------------------------------
    # FINAL RETURN
    # -------------------------------
    return {
        "status": final_status,
        "current_agent": "Execution",
        "next_step": "monitor",
        "errors": errors,
        "audit_log": [log_entry]
    }