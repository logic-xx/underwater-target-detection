"""视频检测 service。

这里负责视频接口背后的完整流程：
1. 校验参数与文件类型；
2. 保存上传视频；
3. 读取真实视频信息；
4. 逐帧调用 YOLOv8 做推理并绘框；
5. 写出检测结果视频；
6. 基于逐帧结果计算真实统计信息；
7. 写入 metadata JSON；
8. 返回统一响应数据。
"""

import subprocess
from time import perf_counter
from pathlib import Path

import cv2
from imageio_ffmpeg import get_ffmpeg_exe
from fastapi import HTTPException, UploadFile, status

from app.core.config import get_settings
from app.models.detector import get_detector
from app.schemas.video import VideoDetectionResponse, VideoInfo
from app.services.analysis_service import FrameAnalysisInput, build_video_analysis
from app.utils.file_manager import (
    build_public_url,
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


def _create_video_writer(video_path: Path, fps: float, width: int, height: int) -> cv2.VideoWriter:
    """创建中间结果视频写入器，并在失败时明确报错。"""

    video_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(video_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        writer.release()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to initialize video writer",
        )
    return writer


def _transcode_to_browser_mp4(source_path: Path, destination_path: Path) -> None:
    """把 OpenCV 生成的中间视频转成浏览器兼容性更好的 H.264 MP4。"""

    ffmpeg_executable = get_ffmpeg_exe()
    command = [
        ffmpeg_executable,
        "-y",
        "-i",
        str(source_path),
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(destination_path),
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0 or not destination_path.exists() or destination_path.stat().st_size == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="failed to transcode browser-compatible mp4",
        )


async def detect_video(
    upload_file: UploadFile,
    conf: float | None = None,
    iou: float | None = None,
) -> VideoDetectionResponse:
    """执行视频真实检测流程。"""

    settings = get_settings()
    settings.ensure_directories()

    # 先校验阈值参数。
    _validate_threshold(conf, "conf")
    _validate_threshold(iou, "iou")
    resolved_conf = conf if conf is not None else settings.default_conf
    resolved_iou = iou if iou is not None else settings.default_iou

    original_filename = upload_file.filename or "video.mp4"
    _validate_extension(original_filename, ALLOWED_VIDEO_EXTENSIONS)
    task_id = generate_task_id()

    # 保存原始上传视频。
    upload_path = settings.upload_dir_abs / "videos" / f"{task_id}{Path(original_filename).suffix.lower()}"
    file_size = await save_upload_file(upload_file=upload_file, destination=upload_path)
    max_size_bytes = settings.max_video_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        # 超限则删除刚保存的文件，避免占用磁盘。
        upload_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"video exceeds {settings.max_video_size_mb}MB limit",
        )

    detector = get_detector()
    intermediate_result_path = settings.output_dir_abs / "videos" / f"result_{task_id}_raw.mp4"
    result_path = settings.output_dir_abs / "videos" / f"result_{task_id}.mp4"
    capture: cv2.VideoCapture | None = None
    writer: cv2.VideoWriter | None = None
    frame_results: list[FrameAnalysisInput] = []
    processed_frame_count = 0
    should_cleanup_result = False
    start_time = perf_counter()

    try:
        capture = cv2.VideoCapture(str(upload_path))
        if not capture.isOpened():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="failed to open video file",
            )

        raw_fps = float(capture.get(cv2.CAP_PROP_FPS))
        fps = raw_fps if raw_fps > 0 else 1.0
        width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        declared_frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

        if width <= 0 or height <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="failed to read video dimensions",
            )

        writer = _create_video_writer(
            video_path=intermediate_result_path,
            fps=fps,
            width=width,
            height=height,
        )

        frame_index = 0
        while True:
            success, frame = capture.read()
            if not success:
                break

            detection_output = detector.detect_frame(
                frame=frame,
                conf=resolved_conf,
                iou=resolved_iou,
            )
            plotted_frame = detection_output.plotted_image if detection_output.plotted_image is not None else frame
            writer.write(plotted_frame)
            frame_results.append(
                FrameAnalysisInput(
                    frame_index=frame_index,
                    detected_classes={item.class_name for item in detection_output.detections},
                    detection_count=len(detection_output.detections),
                )
            )
            frame_index += 1

        processed_frame_count = frame_index
        frame_count = declared_frame_count if declared_frame_count > 0 else processed_frame_count
        if processed_frame_count == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="video contains no readable frames",
            )
        process_time = round(perf_counter() - start_time, 4)
    except Exception:
        should_cleanup_result = True
        raise
    finally:
        if capture is not None:
            capture.release()
        if writer is not None:
            writer.release()
        if should_cleanup_result:
            intermediate_result_path.unlink(missing_ok=True)
            result_path.unlink(missing_ok=True)

    try:
        _transcode_to_browser_mp4(
            source_path=intermediate_result_path,
            destination_path=result_path,
        )
    except Exception:
        intermediate_result_path.unlink(missing_ok=True)
        result_path.unlink(missing_ok=True)
        raise
    finally:
        intermediate_result_path.unlink(missing_ok=True)

    duration = round(processed_frame_count / fps, 4) if processed_frame_count > 0 else 0.0
    video_info = VideoInfo(
        fps=int(round(fps)),
        frame_count=processed_frame_count if processed_frame_count > 0 else frame_count,
        duration=duration,
        width=width,
        height=height,
    )
    analysis = build_video_analysis(
        frame_results=frame_results,
        fps=fps,
        frame_count=video_info.frame_count,
    )

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
            "model_path": settings.model_path,
            "conf": resolved_conf,
            "iou": resolved_iou,
            "data": response.model_dump(mode="json"),
        },
    )
    return response
