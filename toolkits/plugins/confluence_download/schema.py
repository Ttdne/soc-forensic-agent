from pydantic import BaseModel, Field, HttpUrl

class ConfluenceDownloadParams(BaseModel):
    url: HttpUrl = Field(..., description="The URL of the file to download")
    file_path: str = Field(..., description="The relative file path where the downloaded file should be saved")
    state_dir: str = Field(None, description="(Optional) The base directory to save the file, defaults to a timestamped directory")