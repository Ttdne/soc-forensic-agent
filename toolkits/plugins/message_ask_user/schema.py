from pydantic import BaseModel, Field
from typing import Optional, Union, List

class MessageAskUserParams(BaseModel):
    text: str = Field(..., description="Question text to present to user")
    attachments: Optional[Union[str, List[str]]] = Field(None, description="(Optional) List of question-related files or reference materials")
    suggest_user_takeover: Optional[str] = Field("none", description="(Optional) Suggested operation for user takeover", enum=["none", "browser"])
