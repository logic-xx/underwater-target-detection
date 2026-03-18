"""图片检测接口相关 schema。"""

from pydantic import BaseModel

from app.schemas.detection import DetectionItem


class ImageSummary(BaseModel):
    # 当前图片中总共检测到多少个目标。
    total_detections: int
    # 按类别聚合后的数量统计，例如 {"fish": 2, "starfish": 1}。
    class_counts: dict[str, int]


class ImageDetectionResponse(BaseModel):
    # 每次任务的唯一标识，用于结果文件命名和 metadata 记录。
    task_id: str
    # 用户上传时的原始文件名，便于前端展示。
    original_filename: str
    # 检测后结果图的静态访问地址。
    result_image_url: str
    # 聚合统计信息。
    summary: ImageSummary
    # 每个检测目标的详细结果列表。
    detections: list[DetectionItem]
    # 模拟处理耗时，单位秒。
    process_time: float
