"""单个检测框结果的结构定义。"""

from pydantic import BaseModel, Field


class DetectionItem(BaseModel):
    # 检测出的类别名称，例如 fish / starfish / jellyfish。
    class_name: str
    # 模型对该目标的置信度，范围通常为 0~1。
    confidence: float
    # 边界框坐标，格式为 [x1, y1, x2, y2]。
    bbox: list[int] = Field(min_length=4, max_length=4)
