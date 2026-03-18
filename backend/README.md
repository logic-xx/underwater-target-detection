# Backend

## 技术栈
- FastAPI
- PyTorch
- OpenCV

## 说明
后端负责：
- 模型加载
- 图片检测
- 视频检测
- 统计分析
- 文件保存
- 结果返回

当前仓库已提供一个可直接运行的 MVP 初版后端骨架：
- `GET /health`
- `POST /api/detect/image`
- `POST /api/detect/video`
- `/outputs/*` 静态结果访问

本轮接口均为 mock，不会真实加载 `.pt` 模型。

## 运行步骤
1. 创建 Python 3.10 环境
2. 在项目根目录复制环境变量模板：`copy .env.example .env`
3. 进入 `backend` 目录并安装依赖：`pip install -r requirements.txt`
4. 启动 FastAPI 服务：`uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload`

启动后可访问：
- 健康检查：`http://127.0.0.1:8000/health`
- Swagger：`http://127.0.0.1:8000/docs`
- 输出文件：`http://127.0.0.1:8000/outputs/...`

## 配置项
配置文件位于项目根目录 `.env`，当前后端使用以下字段：
- `BACKEND_HOST`
- `BACKEND_PORT`
- `MODEL_PATH`
- `UPLOAD_DIR`
- `OUTPUT_DIR`
- `METADATA_DIR`
- `DEFAULT_CONF`
- `DEFAULT_IOU`
- `MAX_IMAGE_SIZE_MB`
- `MAX_VIDEO_SIZE_MB`

目录会在应用启动时自动创建。

## PyTorch 安装说明
当前 mock 版本可先不安装 PyTorch；接入真实模型时，再根据本机 CUDA 环境单独安装。

例如（CUDA 11.8）：
```bash
conda install pytorch=2.2.2 torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
```

## 推荐目录结构
    backend/app/
    ├── main.py
    ├── api/
    ├── services/
    ├── models/
    ├── utils/
    ├── schemas/
    └── core/
