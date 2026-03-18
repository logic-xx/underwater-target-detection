# 水下目标检测网页系统

## 项目简介
本项目是一个面向网页端的水下目标检测系统，支持图片检测、视频检测以及检测结果的统计分析与可视化展示。

当前模型已训练完成，使用本地 PyTorch `.pt` 权重文件进行推理。

---

## 当前功能规划

### 图片检测
- 上传图片
- 目标检测
- 返回带检测框结果图
- 显示类别、数量、置信度
- 下载检测结果

### 视频检测
- 上传视频
- 逐帧检测
- 生成带检测框视频
- 下载检测后视频

### 视频分析
- 每类目标出现的总帧数
- 按时间轴显示目标出现区间
- 每秒目标数量变化曲线

---

## 技术栈

### 后端
- Python 3.10
- FastAPI
- PyTorch
- OpenCV

### 前端
- Vue 3
- Element Plus
- ECharts

### 存储
- 文件系统
- JSON 元数据
- 后续可扩展 SQLite

---

## 推荐项目结构

```text
underwater-target-detection/
├── AGENTS.md
├── README.md
├── PROJECT_PLAN.md
├── ARCHITECTURE.md
├── API_SPEC.md
├── TASKS.md
├── .env.example
├── .gitignore
├── backend/
├── frontend/
├── weights/
├── uploads/
├── outputs/
├── metadata/
└── docs/
```

---

## 开发目标
第一阶段目标是实现最小可用系统（MVP）：

1. 图片检测完整流程
2. 视频检测完整流程
3. 三项基础视频统计分析
4. 前端展示与结果下载

---

## 环境要求

### 后端
- Python 3.10
- 建议使用 Conda 虚拟环境

### 前端
- Node.js 18+

### 模型
- 本地 `.pt` 权重文件
- 放入 `weights/` 目录

---

## 配置说明
复制环境模板文件：

```bash
cp .env.example .env
```

根据实际情况修改配置项，例如：
- 模型路径
- 上传目录
- 输出目录
- 默认阈值

---

## 启动方式（初版）

### 后端
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端
```bash
cd frontend
npm install
npm run dev
```

---

## 当前开发建议
建议先完成：

1. 后端图片检测接口
2. 后端视频检测接口
3. 视频统计分析服务
4. 前端图片检测页
5. 前端视频检测页

---

## 后续扩展方向
- 历史记录查询
- SQLite 持久化
- 自动生成检测报告
- 云端部署
- 目标跟踪分析
