from pydantic import BaseModel, Field

class FileReadNLinesParams(BaseModel):
    file_path: str = Field(..., description="Đường dẫn tuyệt đối của file cần đọc")
    num_lines: int = Field(..., description="Số dòng cần đọc từ đầu file")