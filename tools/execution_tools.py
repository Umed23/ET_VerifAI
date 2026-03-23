import time
import random
from langchain.tools import tool

@tool
def execute_payment_api(po_number: str, amount: float, retry_count: int = 0) -> dict:
    """
    Executes a payment API transaction. 
    Simulates network failures. Success probability increases on retries.
    """
    # Success rate increases with retries to demonstrate autonomous self-healing capability
    success_rate = 0.4 if retry_count == 0 else 1.0

    print(f"   🌐 [System Output] Calling REST API `POST /api/v1/payments` (Attempt {retry_count + 1})")
    time.sleep(1) # Simulate network delay for effect

    if random.random() < success_rate:
        return {
            "success": True,
            "transaction_id": f"TXN-{random.randint(1000, 9999)}",
            "message": "Payment API executed successfully."
        }
    else:
        return {
            "success": False,
            "error": "503 Service Unavailable: Connection Refused"
        }
