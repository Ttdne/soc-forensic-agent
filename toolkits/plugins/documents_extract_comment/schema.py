from pydantic import BaseModel, Field

class DocumentsExtractCommentParams(BaseModel):
    file_path: str = Field(..., description="Đường dẫn tuyệt đối của file Word cần trích xuất comment")