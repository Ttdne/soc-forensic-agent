import os
import time

def execute(file_path: str, start_line: int = 0, state_dir: str = None, end_line: int = None, sudo: bool = False, **kwargs):
    # Tạo thư mục gốc theo timestamp
    if state_dir is None:
        timestamp = str(int(time.time()))
        state_dir = os.path.join("./test_environment", timestamp)
        os.makedirs(state_dir, exist_ok=True)

    # Chuẩn hóa file_path: loại bỏ ./ và / đầu, dùng path tuyệt đối
    if not file_path.startswith(state_dir):
        file_path = os.path.normpath(file_path).lstrip(os.sep)
        full_file_path = os.path.join(state_dir, file_path)
    else:
        full_file_path = file_path

    # Kiểm tra sự tồn tại của file
    if not os.path.exists(full_file_path):
        return {
            "tool": "file_read",
            "success": False,
            "error": f"{full_file_path} không tồn tại"}

    try:
        # Kiểm tra kích thước file
        file_size = os.path.getsize(full_file_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            return {
                "tool": "file_read",
                "success": False,
                "error": "File quá lớn. Hãy đổi tool khác để chỉ đọc một số dòng đầu tiên."
            }

        # Đọc nội dung file
        with open(full_file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            selected_lines = lines[start_line:end_line]
            return {
                "tool": "file_read",
                "success": True,
                "content": selected_lines
            }
    except Exception as e:
        return {"tool": "file_read", "success": False, "error": str(e)}