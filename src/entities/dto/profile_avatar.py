from pydantic import BaseModel, Field


class AvatarUploadRequest(BaseModel):
    file_name: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(min_length=1, max_length=100)
    file_size: int = Field(gt=0, le=2 * 1024 * 1024)


class AvatarUploadResponse(BaseModel):
    object_path: str
    upload_url: str
    upload_token: str


class CompleteAvatarUploadRequest(BaseModel):
    object_path: str = Field(min_length=1, max_length=512)


class AvatarResponse(BaseModel):
    avatar_url: str
