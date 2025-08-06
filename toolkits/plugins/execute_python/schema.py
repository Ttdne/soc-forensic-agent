from pydantic import BaseModel, Field, validator

class ExecutePythonParams(BaseModel):
    code: str = Field(..., description="Đoạn mã Python cần thực thi")
    timeout: int = Field(600, description="(Tùy chọn) Thời gian chờ tối đa cho việc thực thi mã, tính bằng giây.")

    @validator('timeout')
    def check_min_timeout(cls, value):
        if value < 600:
            raise ValueError("Thời gian chờ tối thiểu là 600 giây.")
        return value