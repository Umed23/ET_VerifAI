import json
import faiss
import numpy as np
import os
from langchain.tools import tool
from sentence_transformers import SentenceTransformer

# 1. Load the Model Once
model = SentenceTransformer('all-MiniLM-L6-v2')

# 2. Universal Resource Loader
# This stores the indices for DIFFERENT departments (P2P, HR, etc.)
RESOURCES = {}

def initialize_resources():
    """Load all registries into memory on startup"""
    configs = {
        "p2p": {"file": "data/po_registry.json", "key": "po_number"},
        "onboarding": {"file": "data/employee_db.json", "key": "full_name"}
    }
    
    for w_type, cfg in configs.items():
        try:
            if os.path.exists(cfg["file"]):
                with open(cfg["file"], 'r') as f:
                    data = json.load(f)
                
                # Extract the "Truth" values (Names or POs)
                valid_values = [item[cfg["key"]] for item in data]
                
                # Create FAISS Index
                embeddings = model.encode(valid_values).astype('float32')
                idx = faiss.IndexFlatL2(embeddings.shape[1])
                idx.add(embeddings)
                
                # Store in our universal resource map
                RESOURCES[w_type] = {"index": idx, "values": valid_values}
                print(f"✅ Loaded {w_type} registry: {len(valid_values)} records.")
        except Exception as e:
            print(f"⚠️ Warning: Failed to load {w_type} registry: {e}")

# Run initialization
initialize_resources()

@tool
def universal_fuzzy_search(query: str, workflow_type: str) -> dict:
    """
    Universal Self-Healing Tool:
    Searches the correct Vector DB (FAISS) based on the workflow type.
    Heals typos in PO numbers, Employee names, or Contract IDs.
    """
    # 1. Check if we have a registry for this workflow
    res = RESOURCES.get(workflow_type)
    
    if not res or not query:
        # If no registry exists (like for a 'meeting'), return original text
        return {"match": query, "confidence": 1.0, "exact": True}

    valid_list = res["values"]
    index = res["index"]

    # 2. Check for Exact Match First (Efficiency)
    if query in valid_list:
        return {"match": query, "confidence": 1.0, "exact": True}

    # 3. Vector Semantic Search (The "Healing" Part)
    query_embedding = model.encode([query]).astype('float32')
    D, I = index.search(query_embedding, 1)

    best_match = valid_list[I[0][0]]
    distance = float(D[0][0])

    # Convert L2 distance to 0-1 Confidence score
    # (Using your scaled mapping)
    confidence = max(0.0, 1.0 - (distance / 1.5)) 

    return {
        "match": best_match,
        "confidence": confidence,
        "exact": False,
        "workflow": workflow_type
    }