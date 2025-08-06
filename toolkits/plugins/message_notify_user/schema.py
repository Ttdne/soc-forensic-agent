from pydantic import BaseModel, Field
from typing import Optional, Union, List

class MessageNotifyUserParams(BaseModel):
    text: str = Field(..., description="Message text to display to user")
    attachments: Optional[Union[str, List[str]]] = Field(None, description="(Optional) List of attachments to show to user, can be file paths or URLs")
