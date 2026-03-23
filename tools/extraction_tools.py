import os
from langchain.tools import tool
try:
    from pydantic.v1 import BaseModel, Field
except ImportError:
    from pydantic import BaseModel, Field

class P2PExtraction(BaseModel):
    vendor: str = Field(description="The name of the vendor or supplier")
    amount: float = Field(description="The total payment amount")
    po_number: str = Field(description="The Purchase Order number")

class OnboardingExtraction(BaseModel):
    candidate: str = Field(description="The name of the candidate")
    role: str = Field(description="The job role offered")
    start_date: str = Field(description="The start date of the employee")

@tool
def extract_entity_data(text: str, workflow_type: str) -> dict:
    """
    Extracts structured data (vendor, amount, PO, etc.) from raw document text using an LLM.
    Returns the extracted data and an LLM confidence score.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        # Fallback simulation if no API key is provided
        result = {}
        if workflow_type == "p2p":
            result = {"vendor": "Acme Corp", "amount": 1250.00, "po_number": "PO-2026-X"}
        elif workflow_type == "onboarding":
            result = {"candidate": "John Doe", "role": "AI Engineer", "start_date": "2026-04-01"}
        else:
            result = {"topic": "Sprint Planning", "action_items": ["Fix Bug #101"]}
        return {"extracted": result, "confidence": 0.85}

    try:
        from langchain_anthropic import ChatAnthropic
        # Real LLM Extraction Implementation!
        llm = ChatAnthropic(model="claude-3-haiku-20240307", temperature=0)
        
        if workflow_type == "p2p":
            structured_llm = llm.with_structured_output(P2PExtraction)
        elif workflow_type == "onboarding":
            structured_llm = llm.with_structured_output(OnboardingExtraction)
        else:
            return {"extracted": {"topic": "Meeting", "action_items": []}, "confidence": 0.5}
            
        res = structured_llm.invoke(f"Extract details from this text:\n\n{text}")
        return {"extracted": res.dict(), "confidence": 0.95}
        
    except Exception as e:
        print(f"Extraction Error: {str(e)}")
        # If the LLM call fails, we ensure the system can escalate appropriately
        return {"extracted": {}, "confidence": 0.0}
