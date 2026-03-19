import type {
  ImageDetectionResponse,
  VideoDetectionResponse,
} from "../types/detect";
import { request } from "./client";

function buildDetectFormData(file: File, conf?: number, iou?: number): FormData {
  const formData = new FormData();
  formData.append("file", file);

  if (typeof conf === "number") {
    formData.append("conf", String(conf));
  }

  if (typeof iou === "number") {
    formData.append("iou", String(iou));
  }

  return formData;
}

export function detectImage(file: File, conf?: number, iou?: number) {
  return request<ImageDetectionResponse>({
    url: "/api/detect/image",
    method: "post",
    data: buildDetectFormData(file, conf, iou),
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
}

export function detectVideo(file: File, conf?: number, iou?: number) {
  return request<VideoDetectionResponse>({
    url: "/api/detect/video",
    method: "post",
    data: buildDetectFormData(file, conf, iou),
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
}
