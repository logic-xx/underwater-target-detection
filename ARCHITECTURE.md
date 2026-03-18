# ARCHITECTURE.md

## 一、总体架构
本项目采用轻量前后端分离架构：

- 前端负责：页面展示、文件上传、图表展示、结果下载
- 后端负责：模型加载、推理、视频处理、统计分析、结果返回

---

## 二、前端架构

### 技术栈
- Vue 3
- Element Plus
- ECharts
- Axios
- Vue Router

### 建议目录
    frontend/src/
    ├── api/
    ├── assets/
    ├── components/
    ├── router/
    ├── views/
    ├── utils/
    └── App.vue

### 前端页面建议
- 首页
- 图片检测页
- 视频检测页

### 前端组件建议
- 上传组件
- 图片结果展示组件
- 视频播放组件
- 类别统计组件
- 时间区间展示组件
- 曲线图组件

---

## 三、后端架构

### 技术栈
- FastAPI
- PyTorch
- OpenCV

### 建议目录
    backend/app/
    ├── main.py
    ├── api/
    ├── services/
    ├── models/
    ├── utils/
    ├── schemas/
    └── core/

### 职责说明
- `main.py`：应用入口
- `api/`：接口路由
- `services/`：业务逻辑
- `models/`：模型加载与推理封装
- `utils/`：绘框、视频读写、路径处理等工具函数
- `schemas/`：请求响应结构
- `core/`：配置项与基础设置

---

## 四、文件存储设计
- `weights/`：模型权重文件
- `uploads/`：上传的原始文件
- `outputs/`：带检测框的图片与视频
- `metadata/`：检测任务元信息和统计结果 JSON

---

## 五、数据流

### 图片检测流程
用户上传图片  
-> 后端保存文件  
-> 模型推理  
-> 绘制检测框  
-> 保存结果图  
-> 返回结果路径和统计信息

### 视频检测流程
用户上传视频  
-> 后端保存文件  
-> 逐帧推理  
-> 生成带框视频  
-> 统计分析  
-> 保存结果视频和 JSON  
-> 返回结果路径和统计数据
