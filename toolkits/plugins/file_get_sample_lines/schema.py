from pydantic import BaseModel, Field

class FileGetSampleNLinesParams(BaseModel):
    file_path: str = Field(..., description="Đường dẫn tuyệt đối của file cần đọc")
    num_lines: int = Field(..., description="Số mẫu cần lấy")