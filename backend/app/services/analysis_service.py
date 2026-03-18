"""视频分析服务。

当前版本基于“逐帧检测结果”计算真实统计信息，严格输出 API 约定的
`class_frame_counts`、`time_intervals`、`per_second_counts` 三部分。
"""

from dataclasses import dataclass
from math import ceil

from app.schemas.video import PerSecondCount, VideoAnalysis


@dataclass
class FrameAnalysisInput:
    """单帧统计所需的最小输入结构。"""

    frame_index: int
    detected_classes: set[str]
    detection_count: int


def _format_second(second: int) -> str:
    """把秒数格式化为 `MM:SS`，用于时间区间展示。"""

    minutes, remaining_seconds = divmod(max(second, 0), 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"


def _frame_to_second(frame_index: int, fps: float) -> int:
    """把帧索引换算为所在秒数。"""

    return int(frame_index / fps)


def _build_class_frame_counts(frame_results: list[FrameAnalysisInput]) -> dict[str, int]:
    """统计每类目标出现的总帧数。"""

    class_frame_counts: dict[str, int] = {}
    for frame_result in frame_results:
        for class_name in frame_result.detected_classes:
            class_frame_counts[class_name] = class_frame_counts.get(class_name, 0) + 1
    return class_frame_counts


def _build_time_intervals(
    frame_results: list[FrameAnalysisInput],
    fps: float,
    gap_tolerance_frames: int = 1,
) -> dict[str, list[tuple[str, str]]]:
    """把逐帧类别出现记录合并为时间区间。"""

    class_frames: dict[str, list[int]] = {}
    for frame_result in frame_results:
        for class_name in frame_result.detected_classes:
            class_frames.setdefault(class_name, []).append(frame_result.frame_index)

    time_intervals: dict[str, list[tuple[str, str]]] = {}
    for class_name, frame_indexes in class_frames.items():
        if not frame_indexes:
            time_intervals[class_name] = []
            continue

        sorted_frames = sorted(frame_indexes)
        intervals: list[tuple[str, str]] = []
        start_frame = sorted_frames[0]
        previous_frame = sorted_frames[0]

        for current_frame in sorted_frames[1:]:
            if current_frame > previous_frame + gap_tolerance_frames + 1:
                start_second = _frame_to_second(start_frame, fps)
                end_second = _frame_to_second(previous_frame + 1, fps)
                intervals.append((_format_second(start_second), _format_second(end_second)))
                start_frame = current_frame
            previous_frame = current_frame

        start_second = _frame_to_second(start_frame, fps)
        end_second = _frame_to_second(previous_frame + 1, fps)
        intervals.append((_format_second(start_second), _format_second(end_second)))
        time_intervals[class_name] = intervals

    return time_intervals


def _build_per_second_counts(
    frame_results: list[FrameAnalysisInput],
    fps: float,
    frame_count: int,
) -> list[PerSecondCount]:
    """按“每秒总检测目标数”生成统计曲线。"""

    duration_seconds = ceil(frame_count / fps) if frame_count > 0 else 0
    second_totals: dict[int, int] = {second: 0 for second in range(duration_seconds)}

    for frame_result in frame_results:
        second = _frame_to_second(frame_result.frame_index, fps)
        second_totals[second] = second_totals.get(second, 0) + frame_result.detection_count

    return [
        PerSecondCount(second=second, count=second_totals.get(second, 0))
        for second in range(duration_seconds)
    ]


def build_video_analysis(
    frame_results: list[FrameAnalysisInput],
    fps: float,
    frame_count: int,
    gap_tolerance_frames: int = 1,
) -> VideoAnalysis:
    """根据真实逐帧检测结果生成视频分析数据。"""

    return VideoAnalysis(
        class_frame_counts=_build_class_frame_counts(frame_results),
        time_intervals=_build_time_intervals(
            frame_results=frame_results,
            fps=fps,
            gap_tolerance_frames=gap_tolerance_frames,
        ),
        per_second_counts=_build_per_second_counts(
            frame_results=frame_results,
            fps=fps,
            frame_count=frame_count,
        ),
    )
