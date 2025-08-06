import os
import random
from tqdm import tqdm

def execute(file_path: str, num_lines: int, **kwargs):
    if num_lines > 20:
        num_lines = 20

    try:
        # Chuẩn hóa file_path: loại bỏ ./ và / đầu
        file_path = os.path.normpath(file_path).lstrip(os.sep)

        # Đọc toàn bộ file và lưu trữ các dòng
        with open(file_path, 'r', encoding='utf-8') as file:
            all_lines = file.readlines()

        # Lấy n//3 dòng ngẫu nhiên
        random_lines = random.sample(all_lines, num_lines // 2)

        # Lấy n//3 dòng dài nhất
        longest_lines = sorted(all_lines, key=len, reverse=True)[:num_lines // 4]

        # Lấy n//3 dòng ngắn nhất
        shortest_lines = sorted(all_lines, key=len)[:num_lines // 4]

        result_lines = random_lines + longest_lines + shortest_lines

        result_lines = random_lines + longest_lines

        return {
            "tool": "file_get_sample_lines",
            "success": True,
            "lines": result_lines
        }
    except Exception as e:
        return {"tool": "file_get_sample_lines", "success": False, "error": str(e)}