""" 
JSON Log Storage (Temporary)
Will stream to Postgres later.
"""
import json
from pathlib import Path

# Define log directory
LOG_DIR = Path("data/logs")
LOG_DIR.mkdir(exist_ok=True, parents=True)

def write_event(event, filename: str):
    path = LOG_DIR / filename
    with path.open("a") as f:
        f.write(json.dumps(event.model_dump(), default=str) + "\n")