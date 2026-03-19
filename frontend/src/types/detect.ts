export interface DetectionItem {
  class_name: string;
  confidence: number;
  bbox: number[];
}

export interface ImageDetectionResponse {
  task_id: string;
  original_filename: string;
  result_image_url: string;
  summary: {
    total_detections: number;
    class_counts: Record<string, number>;
  };
  detections: DetectionItem[];
  process_time: number;
}

export interface VideoDetectionResponse {
  task_id: string;
  result_video_url: string;
  video_info: {
    fps: number;
    frame_count: number;
    duration: number;
    width: number;
    height: number;
  };
  analysis: {
    class_frame_counts: Record<string, number>;
    time_intervals: Record<string, [string, string][]>;
    per_second_counts: Array<{
      second: number;
      count: number;
    }>;
  };
  process_time: number;
}
