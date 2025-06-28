from pydantic import BaseModel


class UploadResponse(BaseModel):
    id: int
    file_name: str


class ValidationRequest(BaseModel):
    file_id: int


class ValidationResponse(BaseModel):
    file_id: int
    is_valid: bool
    message: str


class ProcessRequest(BaseModel):
    file_id: int


class ProcessResponse(BaseModel):
    receipt_id: int
    message: str
