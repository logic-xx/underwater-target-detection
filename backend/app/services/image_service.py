"""图片检测 service。

这个文件负责图片检测接口背后的完整流程：
1. 校验参数与文件类型；
2. 保存上传图片；
3. 生成 mock 检测结果；
4. 复制出一份“结果图”到输出目录；
5. 写入 metadata JSON；
6. 返回符合 API 约定的数据结构。
"""

from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings
from app.schemas.detection import DetectionItem
from app.schemas.image import ImageDetectionResponse, ImageSummary
from app.utils.file_manager import (
    build_public_url,
    copy_file,
    generate_task_id,
    save_metadata,
    save_upload_file,
)


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def _validate_threshold(value: float | None, field_name: str) -> None:
    """校验阈值参数是否在 0~1 之间。"""
    if value is not None and not 0 <= value <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be between 0 and 1",
        )


def _validate_extension(filename: str, allowed_extensions: set[str]) -> str:
    """校验文件扩展名，并返回标准化后缀。"""
    suffix = Path(filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unsupported file type",
        )
    return suffix


async def detect_image(
    upload_file: UploadFile,
    conf: float | None = None,
    iou: float | None = None,
) -> ImageDetectionResponse:
    """执行图片 mock 检测流程。"""

    settings = get_settings()
    settings.ensure_directories()

    # 先校验可选参数，避免无效值继续进入后续流程。
    _validate_threshold(conf, "conf")
    _validate_threshold(iou, "iou")

    # 如果前端没有传文件名，这里给一个兜底默认值，避免后续路径拼接出错。
    original_filename = upload_file.filename or "image.jpg"
    suffix = _validate_extension(original_filename, ALLOWED_IMAGE_EXTENSIONS)
    task_id = generate_task_id()

    # 先把用户原始上传文件保存到 uploads/images 中。
    upload_path = settings.upload_dir_path / "images" / f"{task_id}{suffix}"
    file_size = await save_upload_file(upload_file=upload_file, destination=upload_path)
    max_size_bytes = settings.max_image_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        # 文件超限时，及时删除刚保存的文件，避免无效文件堆积。
        upload_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"image exceeds {settings.max_image_size_mb}MB limit",
        )

    # 当前还是 mock 版本，没有真实绘框，所以先直接复制一份作为“结果图”。
    # 后续接入真实模型时，可以在这里替换成实际绘制后的图片。
    result_path = settings.output_dir_path / "images" / f"result_{task_id}{suffix}"
    copy_file(source=upload_path, destination=result_path)

    # 下面这组检测框是 mock 数据，但字段结构已经与真实接口保持一致。
    detections = [
        DetectionItem(class_name="fish", confidence=0.94, bbox=[96, 128, 248, 286]),
        DetectionItem(class_name="starfish", confidence=0.87, bbox=[322, 214, 412, 304]),
        DetectionItem(class_name="fish", confidence=0.91, bbox=[438, 172, 612, 338]),
    ]
    # 根据检测结果生成类别计数摘要，方便前端直接展示统计信息。
    class_counts = {"fish": 2, "starfish": 1}
    summary = ImageSummary(
        total_detections=len(detections),
        class_counts=class_counts,
    )

    # 处理耗时目前也是 mock 值，后续可替换为真实计时结果。
    process_time = 0.18
    response = ImageDetectionResponse(
        task_id=task_id,
        original_filename=original_filename,
        result_image_url=build_public_url(result_path, settings.output_dir_path, "/outputs"),
        summary=summary,
        detections=detections,
        process_time=process_time,
    )

    # 每次任务都写一份 metadata，后续前端需要历史记录或结果回查时会很有用。
    save_metadata(
        destination=settings.metadata_dir_path / f"image_{task_id}.json",
        payload={
            "task_type": "image",
            "task_id": task_id,
            "conf": conf if conf is not None else settings.default_conf,
            "iou": iou if iou is not None else settings.default_iou,
            "data": response.model_dump(mode="json"),
        },
    )
    return response
