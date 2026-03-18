"""统一响应 schema。

项目文档已经明确要求所有接口都返回固定结构：
- 成功：code=0, message=success, data=...
- 失败：code=1, message=..., data=null

这里把这套结构抽成通用模型，避免每个接口重复定义。
"""

from typing import Generic, TypeVar

from pydantic import BaseModel


DataT = TypeVar("DataT")


class SuccessResponse(BaseModel, Generic[DataT]):
    """成功响应模型。

    通过泛型 `DataT`，不同接口可以在 `data` 中放入不同业务结构，
    但外层返回壳保持一致。
    """
    code: int = 0
    message: str = "success"
    data: DataT | None = None


class ErrorResponse(BaseModel):
    """失败响应模型。"""
    code: int = 1
    message: str
    data: None = None


def error_response(message: str) -> ErrorResponse:
    """快速创建错误响应对象，方便异常处理器统一复用。"""
    return ErrorResponse(message=message)
