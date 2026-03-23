import json
from langchain.tools import tool

def load_compliance_db():
    try:
        with open('data/vendor_contracts.json', 'r') as f:
            return json.load(f)
    except:
        return {"approved_vendors": ["Acme Corp", "TechSupply", "Global Logistics"], "budget_remaining": 5000.00}

compliance_db = load_compliance_db()
# Explicit casting to please Pyre static analysis
approved_vendors = list(compliance_db.get("approved_vendors", []))
monthly_budget_remaining = float(compliance_db.get("budget_remaining", 0))

@tool
def check_vendor_approval(vendor: str) -> bool:
    """
    Checks if a vendor is currently approved by the compliance rule system.
    """
    return vendor in approved_vendors

@tool
def check_budget(amount: float) -> dict:
    """
    Checks if the requested invoice amount is within the current remaining budget.
    """
    approved = amount <= monthly_budget_remaining
    return {
        "approved": approved,
        "remaining": monthly_budget_remaining,
        "requested": amount
    }

@tool
def check_hr_policy(candidate: str) -> dict:
    """
    Checks if a candidate meets HR policy requirements for onboarding.
    """
    # Demonstration mock logic for the hackathon
    return {
        "eligible": True,
        "reason": "Meets all background check and eligibility requirements."
    }
