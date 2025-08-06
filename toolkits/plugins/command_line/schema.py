from pydantic import BaseModel, Field

class CommandLineParams(BaseModel):
    command: str = Field(..., description="Lệnh shell hoặc script cần thực thi")
    exec_dir: str = Field(..., description="Đường dẫn làm việc để thực thi lệnh (phải sử dụng đường dẫn tuyệt đối)")
    id: str = Field(..., description="ID phiên shell, dùng để phân biệt các phiên lệnh")
    state_dir: str = Field(None, description="(Optional) The base directory to save the file, defaults to a timestamped directory")
