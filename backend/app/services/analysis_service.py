"""视频分析 mock 逻辑。

当前版本还没有真实逐帧检测结果，因此这里通过“预设目标出现时间表”来生成
贴近业务的 mock 数据。这样前端在早期就能联调图表和统计展示逻辑。
"""

from app.schemas.video import PerSecondCount, VideoAnalysis


def _format_second(second: int) -> str:
    """把秒数格式化为 `MM:SS`，用于时间区间展示。"""
    minutes, remaining_seconds = divmod(second, 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"


def generate_mock_video_analysis(fps: int, duration_seconds: int) -> VideoAnalysis:
    """生成视频分析 mock 数据。

    参数说明：
    - `fps`：视频帧率，用于把“出现秒数”换算成“出现总帧数”；
    - `duration_seconds`：总时长，用于生成完整的每秒统计曲线。

    返回结果包含三部分，严格对应文档要求：
    - `class_frame_counts`
    - `time_intervals`
    - `per_second_counts`
    """

    # 这里把每个类别“在哪些秒出现”预先写出来，后续所有 mock 统计都从它推导。
    class_schedule: dict[str, list[int]] = {
        "fish": list(range(2, 12)) + list(range(18, 30)),
        "starfish": list(range(8, 15)),
        "jellyfish": list(range(20, 25)),
    }

    # 根据“出现的秒数 * fps”得到“出现总帧数”。
    # 这与 `ANALYSIS_RULES.md` 中“某类在某帧出现至少一次则该帧计 1”的定义一致。
    class_frame_counts = {
        class_name: len(seconds) * fps for class_name, seconds in class_schedule.items()
    }

    # 把连续的秒段合并成时间区间，供前端直接展示。
    # 例如 [2,3,4,5,8,9] 会合并成 [("00:02","00:06"), ("00:08","00:10")]。
    time_intervals: dict[str, list[tuple[str, str]]] = {}
    for class_name, seconds in class_schedule.items():
        intervals: list[tuple[str, str]] = []
        start = seconds[0]
        previous = seconds[0]
        for second in seconds[1:]:
            if second != previous + 1:
                intervals.append((_format_second(start), _format_second(previous + 1)))
                start = second
            previous = second
        intervals.append((_format_second(start), _format_second(previous + 1)))
        time_intervals[class_name] = intervals

    # 生成每秒目标数量曲线。
    # 当前第一版按总数统计，不区分类别拆分。
    per_second_counts: list[PerSecondCount] = []
    for second in range(duration_seconds):
        count = 0
        if second in class_schedule["fish"]:
            # 让鱼类数量做轻微波动，模拟更接近真实视频中的变化。
            count += 2 if second % 2 == 0 else 3
        if second in class_schedule["starfish"]:
            count += 1
        if second in class_schedule["jellyfish"]:
            count += 2 if second % 2 == 0 else 1
        per_second_counts.append(PerSecondCount(second=second, count=count))

    return VideoAnalysis(
        class_frame_counts=class_frame_counts,
        time_intervals=time_intervals,
        per_second_counts=per_second_counts,
    )
