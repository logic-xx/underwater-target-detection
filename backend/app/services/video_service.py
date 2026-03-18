"""视频检测 service。

与图片 service 类似，这里负责视频接口背后的完整流程：
1. 校验参数与文件类型；
2. 保存上传视频；
3. 生成 mock 视频基础信息；
4. 生成 mock 视频分析结果；
5. 复制出一份“结果视频”到输出目录；
6. 写入 metadata JSON；
7. 返回统一响应数据。
"""

from pathlib import Path

from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings
from app.schemas.video import VideoDetectionResponse, VideoInfo
from app.services.analysis_service import generate_mock_video_analysis
from app.utils.file_manager import (
    build_public_url,
    copy_file,
    generate_task_id,
    save_metadata,
    save_upload_file,
)


ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}


def _validate_threshold(value: float | None, field_name: str) -> None:
    """校验阈值参数是否在 0~1 之间。"""
    if value is not None and not 0 <= value <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field_name} must be between 0 and 1",
        )


def _validate_extension(filename: str, allowed_extensions: set[str]) -> str:
    """校验视频扩展名，并返回标准化后缀。"""
    suffix = Path(filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unsupported file type",
        )
    return suffix


async def detect_video(
    upload_file: UploadFile,
    conf: float | None = None,
    iou: float | None = None,
) -> VideoDetectionResponse:
    """执行视频 mock 检测流程。"""

    settings = get_settings()
    settings.ensure_directories()

    # 先校验阈值参数。
    _validate_threshold(conf, "conf")
    _validate_threshold(iou, "iou")

    original_filename = upload_file.filename or "video.mp4"
    suffix = _validate_extension(original_filename, ALLOWED_VIDEO_EXTENSIONS)
    task_id = generate_task_id()

    # 保存原始上传视频。
    upload_path = settings.upload_dir_abs / "videos" / f"{task_id}{suffix}"
    file_size = await save_upload_file(upload_file=upload_file, destination=upload_path)
    max_size_bytes = settings.max_video_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        # 超限则删除刚保存的文件，避免占用磁盘。
        upload_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"video exceeds {settings.max_video_size_mb}MB limit",
        )

    # 当前 mock 版本没有真实逐帧处理，所以直接复制一份作为结果视频。
    result_path = settings.output_dir_abs / "videos" / f"result_{task_id}{suffix}"
    copy_file(source=upload_path, destination=result_path)

    # 视频基础信息先写成固定 mock 值，后续可改为通过 OpenCV 读取真实信息。
    video_info = VideoInfo(
        fps=25,
        frame_count=900,
        duration=36.0,
        width=1280,
        height=720,
    )
    # 分析结果从专门的 analysis_service 生成，避免统计逻辑堆在这里。
    analysis = generate_mock_video_analysis(
        fps=video_info.fps,
        duration_seconds=int(video_info.duration),
    )
    process_time = 3.6

    response = VideoDetectionResponse(
        task_id=task_id,
        result_video_url=build_public_url(result_path, settings.output_dir_abs, "/outputs"),
        video_info=video_info,
        analysis=analysis,
        process_time=process_time,
    )

    # 写 metadata，便于之后做历史任务、结果回查或调试。
    save_metadata(
        destination=settings.metadata_dir_abs / f"video_{task_id}.json",
        payload={
            "task_type": "video",
            "task_id": task_id,
            "original_filename": original_filename,
            "conf": conf if conf is not None else settings.default_conf,
            "iou": iou if iou is not None else settings.default_iou,
            "data": response.model_dump(mode="json"),
        },
    )
    return response
