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

## 运行步骤
1. 创建 Python 3.10 环境
2. 根据本机 CUDA 环境单独安装 PyTorch
3. 安装 `requirements.txt`
4. 配置 `.env`
5. 启动 FastAPI 服务

## PyTorch 安装说明
请根据本机 CUDA 环境单独安装 PyTorch。

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
