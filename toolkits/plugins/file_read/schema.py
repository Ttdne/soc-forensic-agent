from pydantic import BaseModel, Field

class FileReadParams(BaseModel):
    file_path: str = Field(..., description="Đường dẫn tuyệt đối của file cần đọc")
    start_line: int = Field(0, description="(Tùy chọn) Dòng bắt đầu đọc, bắt đầu từ 0")
    end_line: int = Field(None, description="(Tùy chọn) Dòng kết thúc đọc (không bao gồm)")
    sudo: bool = Field(False, description="(Tùy chọn) Sử dụng quyền sudo")
