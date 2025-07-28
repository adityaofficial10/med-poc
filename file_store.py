import os
import json
from datetime import datetime

META_DIR = "storage/metadata"
os.makedirs(META_DIR, exist_ok=True)

def store_metadata(user_id: str, filename: str, num_chunks: int, summary=""):
    meta_file = os.path.join(META_DIR, f"{user_id}.json")
    data = []

    if os.path.exists(meta_file):
        with open(meta_file, "r") as f:
            data = json.load(f)

    entry = {
        "filename": filename,
        "timestamp": datetime.now().isoformat(),
        "num_chunks": num_chunks,
        "summary": summary
    }
    data.append(entry)

    with open(meta_file, "w") as f:
        json.dump(data, f, indent=2)
