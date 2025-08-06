from pydantic import BaseModel, Field
from typing import Dict

class DocxFillParams(BaseModel):
    text_content: object = Field(..., description="Json chứa các placeholder và giá trị tương ứng để điền vào tài liệu. VD: \"text_content\" : {\"text_placeholder_1\":\"text_value\" }")
    image_content: object = Field(..., description="Json chứa các placeholder và đường dẫn hình ảnh tương ứng để điền vào tài liệu. : {\"image_placeholder_1\":\".\\test\\image_path_1 \" }")
    file_path: str = Field(..., description="Đường dẫn tuyệt đối của file DOCX cần điền nội dung")
    output_file_path: str = Field(..., description="Đường dẫn tuyệt đối để lưu tài liệu sau khi điền")
