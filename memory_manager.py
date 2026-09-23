import os
import json
import datetime

LOGS_DIR = "logs"

class MemoryManager:
    def __init__(self):
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = os.path.join(LOGS_DIR, f"session_{timestamp}.json")
        self.history = []

    def log_interaction(self, role: str, content: str):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "role": role,
            "content": content
        }
        self.history.append(entry)
        
        with open(self.session_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=4, ensure_ascii=False)

memory_manager = MemoryManager()
