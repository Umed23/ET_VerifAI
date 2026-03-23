from utils.vector_store import build_vector_db
import os

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

def run_setup():
    print("--- 🛠️ BUILDING VERIFAI KNOWLEDGE BASE ---")
    
    # 1. Build PO Registry Index
    build_vector_db(
        json_file="data/po_registry.json",
        text_field="po_number",
        index_path="data/po_index.faiss",
        records_path="data/po_records.json"
    )

    # 2. Build Employee Registry Index (The Universal Part!)
    build_vector_db(
        json_file="data/employee_db.json",
        text_field="full_name",
        index_path="data/emp_index.faiss",
        records_path="data/emp_records.json"
    )

if __name__ == "__main__":
    run_setup()