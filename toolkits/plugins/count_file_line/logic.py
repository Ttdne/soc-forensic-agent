import os

def execute(file_path: str, buffer_size: int = 1024 * 1024, **kwargs):  # Sử dụng buffer 1MB
    try:
        # Chuẩn hóa file_path: loại bỏ ./ và / đầu
        file_path = os.path.normpath(file_path).lstrip(os.sep)

        # Đếm số dòng trong file
        if not os.path.exists(file_path):
            return {"tool": "count_file_line", "success": False, "error": "File không tồn tại"}

        line_count = 0
        with open(file_path, 'r', encoding='utf-8') as file:
            while True:
                buffer = file.read(buffer_size)
                if not buffer:
                    break
                line_count += buffer.count('\n')

        return {
            "tool": "count_file_line",
            "success": True,
            "line_count": line_count
        }
    except Exception as e:
        return {"tool": "count_file_line", "success": False, "error": str(e)}