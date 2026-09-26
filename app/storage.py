from pathlib import Path
import json

DATA_DIRECTORY = Path("data")
DATA_FILE = DATA_DIRECTORY / "issues.json"

def load_data():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            content = f.read()
            if content.strip():
                return json.loads(content)
    return []

def save_data(data):
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)