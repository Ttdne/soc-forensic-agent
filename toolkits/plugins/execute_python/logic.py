import subprocess
import tempfile
import os
import time

def execute(code: str, timeout: int = 600, state_dir: str = None, **kwargs):
    try:
        # Tạo thư mục gốc theo timestamp nếu state_dir không được cung cấp
        if state_dir is None:
            timestamp = str(int(time.time()))
            state_dir = os.path.join("./test_environment", timestamp)
            os.makedirs(state_dir, exist_ok=True)

        # Tạo tệp tạm thời trong thư mục state_dir
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode='w', encoding='utf-8', dir=state_dir) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        result = subprocess.run(
            ["python", temp_file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=state_dir
        )

        # Xóa tệp tạm thời sau khi thực thi
        #os.remove(temp_file_path)

        return {
            "tool": "execute_python",
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }

    except subprocess.TimeoutExpired:
        return {
            "tool": "execute_python",
            "success": False,
            "error": "Execution timed out"
        }
    except Exception as e:
        return {
            "tool": "execute_python",
            "success": False,
            "error": str(e)
        }