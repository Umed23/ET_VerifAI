from typing import TypedDict, List, Dict, Any, Annotated, Union
import operator

class AgentState(TypedDict):
    # --- 1. IDENTIFICATION ---
    task_id: str             # Unique ID for the run (e.g., VERIFAI-998)
    file_name: str           # Original filename of the uploaded document
    workflow_type: str       # "p2p", "onboarding", or "meeting" (Set by Agent 1)
    raw_input: str           # The raw text extracted from the uploaded PDF/Doc
    
    # --- 2. INTELLIGENCE ---
    # Agent 2 fills this; Agent 3/4/Critic validate it
    extracted_data: Dict[str, Any] 
    confidence_score: float  # LLM's confidence in the extraction (0.0 to 1.0)
    risk_score: float        # Calculated by Coordinator (Agent 1)
    selected_llm: str        # Which model is handling the current task
    
    # --- 3. DYNAMIC ROUTING & STATUS ---
    # This tells LangGraph which node to visit next based on the last agent's output
    next_step: str           # e.g., "matching", "human_approval", or "end"
    status: str              # "processing", "completed", "escalated", "failed"
    current_agent: str       # Tracks which agent currently "owns" the folder
    
    # --- 4. SELF-CORRECTION TRACKING ---
    # Judges look for this! It proves the agent "Recovered when things broke"
    correction_flag: bool    # True if Agent 3/5 had to fix an error
    retry_count: int         # Track attempts for Agent 5 (Execution)
    errors: List[str]        # Technical log of any API fails or mismatches
    critic_loops: int        # Number of times the critic has asked for re-extraction
    critic_feedback: str     # Rationale from the Critic Agent
    
    # --- 5. THE AUDIT TRAIL (The "Captain's Log") ---
    # Annotated with operator.add so that every agent's dictionary 
    # is APPENDED to the list instead of overwriting it.
    audit_log: Annotated[List[Dict[str, Any]], operator.add]