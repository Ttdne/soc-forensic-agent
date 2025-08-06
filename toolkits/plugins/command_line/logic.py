import subprocess
import os
import time
def execute(command: str, exec_dir: str, id: str, state_dir: str):
    # Tạo thư mục gốc theo timestamp nếu state_dir không được cung cấp
    if state_dir is None:
        timestamp = str(int(time.time()))
        state_dir = os.path.join("./test_environment", timestamp)
        os.makedirs(state_dir, exist_ok=True)
    if not os.path.exists(exec_dir):
        return {"success": False, "error": "Thư mục không tồn tại"}
    
    try:
        result = subprocess.run(command, shell=True, cwd=exec_dir, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
