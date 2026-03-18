"""检测相关接口。

路由层只做两件事：
1. 声明 HTTP 接口需要接收哪些参数；
2. 调用 service 并把结果包装成统一响应结构。

文件保存、mock 结果生成、metadata 写入等逻辑都放在 service 层。
"""

from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

from app.schemas.common import SuccessResponse
from app.schemas.image import ImageDetectionResponse
from app.schemas.video import VideoDetectionResponse
from app.services.image_service import detect_image
from app.services.video_service import detect_video


router = APIRouter(prefix="/api/detect", tags=["detect"])


@router.post("/image", response_model=SuccessResponse[ImageDetectionResponse])
async def detect_image_endpoint(
    file: Annotated[UploadFile, File(...)],
    conf: Annotated[float | None, Form()] = None,
    iou: Annotated[float | None, Form()] = None,
) -> SuccessResponse[ImageDetectionResponse]:
    # `UploadFile` 适合处理 multipart/form-data 上传文件；
    # `conf` 和 `iou` 作为可选表单字段一并传入。
    result = await detect_image(upload_file=file, conf=conf, iou=iou)
    # 所有成功响应都统一包装为 code=0, message=success, data=...
    return SuccessResponse(data=result)


@router.post("/video", response_model=SuccessResponse[VideoDetectionResponse])
async def detect_video_endpoint(
    file: Annotated[UploadFile, File(...)],
    conf: Annotated[float | None, Form()] = None,
    iou: Annotated[float | None, Form()] = None,
) -> SuccessResponse[VideoDetectionResponse]:
    result = await detect_video(upload_file=file, conf=conf, iou=iou)
    return SuccessResponse(data=result)
