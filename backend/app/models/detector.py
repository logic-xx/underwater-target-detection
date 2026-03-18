"""YOLOv8 检测器封装。

这个模块只负责与 `ultralytics.YOLO` 打交道：
1. 按配置加载本地权重；
2. 执行图片检测；
3. 把 YOLO 原始结果解析成项目自己的标准结构；
4. 返回带检测框和标签的可视化结果图。

这样 service 层不需要知道 ultralytics 的内部对象结构，后续替换模型实现时，
只需要优先改这里。
"""

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from ultralytics import YOLO
from ultralytics.engine.results import Results

from app.core.config import get_settings


@dataclass
class ParsedDetection:
    """项目内部统一的单个检测结果结构。"""

    class_name: str
    confidence: float
    bbox: list[int]


@dataclass
class ImageDetectionOutput:
    """图片检测后的标准输出。"""

    detections: list[ParsedDetection]
    plotted_image: object


class YOLODetector:
    """基于 ultralytics YOLO 的目标检测器。"""

    def __init__(self, model_path: Path) -> None:
        if not model_path.exists():
            raise FileNotFoundError(f"model file not found: {model_path}")

        self.model_path = model_path
        self.model = YOLO(str(model_path))

    def detect_image(self, image_path: Path, conf: float, iou: float) -> ImageDetectionOutput:
        """执行图片检测并返回解析后的结果。"""

        results = self.model.predict(
            source=str(image_path),
            conf=conf,
            iou=iou,
            verbose=False,
            save=False,
        )
        result = results[0] if results else None
        if result is None:
            return ImageDetectionOutput(detections=[], plotted_image=None)

        return ImageDetectionOutput(
            detections=self._parse_result(result),
            plotted_image=result.plot(),
        )

    def _parse_result(self, result: Results) -> list[ParsedDetection]:
        """把 YOLO 原始结果解析成 API 需要的检测列表。"""

        boxes = result.boxes
        if boxes is None:
            return []

        names = result.names or self.model.names or {}
        detections: list[ParsedDetection] = []
        for box in boxes:
            cls_id = int(box.cls.item())
            class_name = str(names.get(cls_id, cls_id))
            confidence = round(float(box.conf.item()), 4)
            bbox = [int(round(value)) for value in box.xyxy[0].tolist()]
            detections.append(
                ParsedDetection(
                    class_name=class_name,
                    confidence=confidence,
                    bbox=bbox,
                )
            )
        return detections


@lru_cache
def get_detector() -> YOLODetector:
    """返回全局复用的检测器实例，避免每次请求重复加载权重。"""

    settings = get_settings()
    return YOLODetector(model_path=settings.model_path_abs)
