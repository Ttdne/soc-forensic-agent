from pydantic import BaseModel, Field

class CountFileLineParams(BaseModel):
    file_path: str = Field(..., description="Đường dẫn tuyệt đối của file cần đếm số dòng")