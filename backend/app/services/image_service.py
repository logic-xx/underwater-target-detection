"""图片检测 service。

这个文件负责图片检测接口背后的完整流程：
1. 校验参数与文件类型；
2. 保存上传图片；
3. 调用 detector 执行真实 YOLOv8 推理；
4. 保存带检测框的结果图到输出目录；
5. 写入 metadata JSON；
6. 返回符合 API 约定的数据结构。
"""

from collections import Counter
from pathlib import Path
from time import perf_counter

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings
from app.models.detector import get_detector
from app.schemas.detection import DetectionItem
from app.schemas.image import ImageDetectionResponse, ImageSummary
from app.utils.file_manager import (
    build_public_url,
    copy_file,
    generate_task_id,
    save_image_array,
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
    """执行图片真实检测流程。"""

    settings = get_settings()
    settings.ensure_directories()

    # 先校验可选参数，避免无效值继续进入后续流程。
    _validate_threshold(conf, "conf")
    _validate_threshold(iou, "iou")
    resolved_conf = conf if conf is not None else settings.default_conf
    resolved_iou = iou if iou is not None else settings.default_iou

    # 如果前端没有传文件名，这里给一个兜底默认值，避免后续路径拼接出错。
    original_filename = upload_file.filename or "image.jpg"
    suffix = _validate_extension(original_filename, ALLOWED_IMAGE_EXTENSIONS)
    task_id = generate_task_id()

    # 先把用户原始上传文件保存到 uploads/images 中。
    upload_path = settings.upload_dir_abs / "images" / f"{task_id}{suffix}"
    file_size = await save_upload_file(upload_file=upload_file, destination=upload_path)
    max_size_bytes = settings.max_image_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        # 文件超限时，及时删除刚保存的文件，避免无效文件堆积。
        upload_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"image exceeds {settings.max_image_size_mb}MB limit",
        )

    detector = get_detector()
    start_time = perf_counter()
    detection_output = detector.detect_image(
        image_path=upload_path,
        conf=resolved_conf,
        iou=resolved_iou,
    )
    process_time = round(perf_counter() - start_time, 4)

    # 真实推理后，把带检测框和类别标签的图像保存到 outputs/images 中。
    result_path = settings.output_dir_abs / "images" / f"result_{task_id}{suffix}"
    if detection_output.plotted_image is not None:
        save_image_array(image=detection_output.plotted_image, destination=result_path)
    else:
        # 极端情况下如果模型未返回结果图，则保底保存原图，保证结果地址仍可访问。
        copy_file(source=upload_path, destination=result_path)

    detections = [
        DetectionItem(
            class_name=item.class_name,
            confidence=item.confidence,
            bbox=item.bbox,
        )
        for item in detection_output.detections
    ]
    # 根据真实检测结果统计类别数量；若未检测到目标则返回空字典。
    class_counts = dict(Counter(item.class_name for item in detections))
    summary = ImageSummary(
        total_detections=len(detections),
        class_counts=class_counts,
    )

    response = ImageDetectionResponse(
        task_id=task_id,
        original_filename=original_filename,
        result_image_url=build_public_url(result_path, settings.output_dir_abs, "/outputs"),
        summary=summary,
        detections=detections,
        process_time=process_time,
    )

    # 每次任务都写一份 metadata，后续前端需要历史记录或结果回查时会很有用。
    save_metadata(
        destination=settings.metadata_dir_abs / f"image_{task_id}.json",
        payload={
            "task_type": "image",
            "task_id": task_id,
            "original_filename": original_filename,
            "model_path": settings.model_path,
            "conf": resolved_conf,
            "iou": resolved_iou,
            "data": response.model_dump(mode="json"),
        },
    )
    return response
