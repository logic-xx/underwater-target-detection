"""视频检测接口相关 schema。"""

from pydantic import BaseModel


class VideoInfo(BaseModel):
    # 视频每秒帧数。
    fps: int
    # 总帧数。
    frame_count: int
    # 总时长，单位秒。
    duration: float
    # 视频宽度。
    width: int
    # 视频高度。
    height: int


class PerSecondCount(BaseModel):
    # 第几秒，从 0 开始计。
    second: int
    # 这一秒内目标数量统计值。
    count: int


class VideoAnalysis(BaseModel):
    # 每类目标出现的总帧数。
    class_frame_counts: dict[str, int]
    # 每类目标在时间轴上的出现区间。
    time_intervals: dict[str, list[tuple[str, str]]]
    # 每秒目标数量变化曲线数据。
    per_second_counts: list[PerSecondCount]


class VideoDetectionResponse(BaseModel):
    # 每次视频任务的唯一标识。
    task_id: str
    # 检测后结果视频的静态访问地址。
    result_video_url: str
    # 视频基础信息。
    video_info: VideoInfo
    # 视频统计分析结果。
    analysis: VideoAnalysis
    # 模拟处理耗时，单位秒。
    process_time: float
