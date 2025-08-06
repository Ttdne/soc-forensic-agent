import os
import time
import json

def execute(state_dir: str = None, **kwargs):
    # Create directory based on timestamp if not provided
    if state_dir is None:
        timestamp = str(int(time.time()))
        state_dir = os.path.join("./test_environment", timestamp)
    
    if not os.path.exists(state_dir):
        os.makedirs(state_dir, exist_ok=True)
    
    # Log the idle state transition
    idle_log_path = os.path.join(state_dir, "idle_log.txt")
    with open(idle_log_path, "a") as log_file:
        log_file.write(f"Entered idle state at: {time.ctime()}\n")
    
    # Create a status file
    status = {
        "status": "idle",
        "timestamp": time.time(),
        "message": "All tasks completed, agent is now in idle state."
    }
    
    status_path = os.path.join(state_dir, "idle_status.json")
    with open(status_path, "w") as status_file:
        json.dump(status, status_file, indent=2)
    
    return {
        "success": True,
        "status": "idle",
        "timestamp": time.time(),
        "message": "All tasks completed, agent is now in idle state.",
        "status_file": status_path
    }
