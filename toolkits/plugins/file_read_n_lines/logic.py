import os

def execute(file_path: str, num_lines: int, **kwargs):

    if num_lines > 20 :
        num_lines = 20
    try:
        # Chuẩn hóa file_path: loại bỏ ./ và / đầu
        file_path = os.path.normpath(file_path).lstrip(os.sep)

        # Đọc n dòng đầu tiên của file
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = []
            for _ in range(num_lines):
                line = file.readline()
                if not line:
                    break
                lines.append(line.rstrip('\n'))

        return {
            "tool" : "file_read_n_lines",
            "success": True,
            "lines": lines
        }
    except Exception as e:
        return { "tool" : "file_read_n_lines", "success": False, "error": str(e)}