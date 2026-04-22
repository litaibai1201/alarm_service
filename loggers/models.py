from typing import Any, Dict, Optional
from pydantic import BaseModel, Extra

# ALLOWED_FIELDS = {
#     "service": {"name", "environment"},
#     "client_ip",
#     "trace": {"id"},
#     "transaction": {"id"},
#     "req": {"method", "path", "headers", "body"},
#     "resp": {"status_code", "body", "event_duration"},
#     "db": {"statement", "status", "duration"},
#     "custom": "*",
#     "error": {"message", "stack_trace"},
# }


class ServiceModel(BaseModel):
    name: str
    environment: str

    class Config: extra = Extra.forbid


class TraceModel(BaseModel):
    id: str

    class Config: extra = Extra.forbid


class TransactionModel(BaseModel):
    id: str

    class Config: extra = Extra.forbid


class HTTPRequestModel(BaseModel):
    method: str
    path: str
    headers: Dict[str, Any]
    body: Any

    class Config: extra = Extra.forbid


class HTTPResponseModel(BaseModel):
    status_code: int
    body: Any
    event_duration: float

    class Config: extra = Extra.forbid


class DBModel(BaseModel):
    statement: str
    status: str
    duration: float

    class Config: extra = Extra.forbid


class ErrorModel(BaseModel):
    message: str
    stack_trace: str

    class Config: extra = Extra.forbid


# 主日志模型
class LogModel(BaseModel):
    event: Optional[str] = None
    service: Optional[ServiceModel] = None
    client_ip: Optional[str] = None
    trace: Optional[TraceModel] = None
    transaction: Optional[TransactionModel] = None
    req: Optional[HTTPRequestModel] = None
    resp: Optional[HTTPResponseModel] = None
    db: Optional[DBModel] = None
    custom: Optional[Dict[str, Any]] = None  # custom.*
    error: Optional[ErrorModel] = None

    class Config: extra = Extra.forbid
