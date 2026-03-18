# API_SPEC.md

## 一、接口设计原则
- RESTful 风格
- 返回结构统一
- 路径清晰
- 错误信息明确

---

## 二、统一响应格式

### 成功响应
```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

### 失败响应
```json
{
  "code": 1,
  "message": "error message",
  "data": null
}
```

---

## 三、图片检测接口

### POST /api/detect/image

#### 功能
上传图片并执行目标检测。

#### 请求参数
- `file`：图片文件
- `conf`：float，可选，置信度阈值
- `iou`：float，可选，IoU 阈值

#### 返回示例
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "xxx",
    "original_filename": "test.jpg",
    "result_image_url": "/outputs/image_xxx.jpg",
    "summary": {
      "total_detections": 5,
      "class_counts": {
        "fish": 3,
        "starfish": 2
      }
    },
    "detections": [
      {
        "class_name": "fish",
        "confidence": 0.93,
        "bbox": [100, 120, 180, 220]
      }
    ],
    "process_time": 0.42
  }
}
```

---

## 四、视频检测接口

### POST /api/detect/video

#### 功能
上传视频并执行逐帧检测，输出带框视频及统计结果。

#### 请求参数
- `file`：视频文件
- `conf`：float，可选
- `iou`：float，可选

#### 返回示例
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "task_id": "xxx",
    "result_video_url": "/outputs/video_xxx.mp4",
    "video_info": {
      "fps": 25,
      "frame_count": 1000,
      "duration": 40.0,
      "width": 1280,
      "height": 720
    },
    "analysis": {
      "class_frame_counts": {
        "fish": 420,
        "starfish": 80
      },
      "time_intervals": {
        "fish": [
          ["00:03", "00:18"],
          ["00:25", "00:40"]
        ],
        "jellyfish": [
          ["00:12", "00:15"]
        ]
      },
      "per_second_counts": [
        {"second": 0, "count": 2},
        {"second": 1, "count": 4},
        {"second": 2, "count": 1}
      ]
    },
    "process_time": 18.6
  }
}
```

---

## 五、结果文件接口（可选）

### GET /api/results/{task_id}
获取某次检测的详情。

### GET /api/results/list
获取历史任务列表。

---

## 六、静态文件访问
需要支持：
- 输出图片访问
- 输出视频访问
- JSON 元数据访问（按需）
