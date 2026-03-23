import faiss
import json
import numpy as np
import os
from sentence_transformers import SentenceTransformer

# Load a lightweight, fast embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

def build_vector_db(json_file, text_field, index_path, records_path):
    """
    Turns a JSON database into a searchable FAISS Vector Index.
    """
    if not os.path.exists(json_file):
        print(f"❌ Error: {json_file} not found.")
        return

    with open(json_file, 'r') as f:
        data = json.load(f)

    # Extract the strings we want to 'Heal' (e.g., PO Numbers or Names)
    records = [item[text_field] for item in data]

    # 1. Convert strings to Vectors (Embeddings)
    embeddings = model.encode(records)
    embeddings = np.array(embeddings).astype("float32")

    # 2. Create and Train the FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # 3. Save to disk so we don't have to rebuild every time
    faiss.write_index(index, index_path)
    with open(records_path, "w") as f:
        json.dump(records, f)

    print(f"✅ Vector DB built: {len(records)} records indexed at {index_path}")

def load_vector_db(index_path, records_path):
    """
    Loads the pre-built index into memory.
    """
    index = faiss.read_index(index_path)
    with open(records_path, "r") as f:
        records = json.load(f)
    return index, records

def search_vector(index, records, query, top_k=1):
    """
    The 'Healing' Logic: Finds the closest match to a messy input string.
    """
    query_vec = model.encode([query])
    query_vec = np.array(query_vec).astype("float32")

    # Search the index for the nearest neighbor
    distances, indices = index.search(query_vec, top_k)

    best_match = records[indices[0][0]]
    # Convert L2 distance to a 0-1 similarity score
    # Lower distance = Higher confidence
    confidence = 1 / (1 + distances[0][0])

    return {
        "match": best_match,
        "confidence": confidence,
        "exact": query.strip().lower() == best_match.strip().lower()
    }