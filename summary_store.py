import json
import os

SUMMARY_DIR = "summaries"
os.makedirs(SUMMARY_DIR, exist_ok=True)

def save_structured_summary(user_id, patient_id, summary):
    with open(f"{SUMMARY_DIR}/{user_id}__{patient_id}.json", "w") as f:
        json.dump(summary, f, indent=2)

def load_structured_summary(user_id, patient_id):
    path = f"{SUMMARY_DIR}/{user_id}__{patient_id}.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []
