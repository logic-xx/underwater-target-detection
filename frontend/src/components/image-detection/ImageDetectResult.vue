<script setup lang="ts">
import type { ImageDetectionResponse } from "../../types/detect";

defineProps<{
  originalPreviewUrl: string | null;
  result: ImageDetectionResponse | null;
  resultImageUrl: string | null;
  loading?: boolean;
  errorMessage?: string;
}>();
</script>

<template>
  <section class="result-layout">
    <div class="panel">
      <h2>上传前原图</h2>
      <div class="preview-box">
        <img v-if="originalPreviewUrl" :src="originalPreviewUrl" alt="原图预览" />
        <p v-else>请选择一张图片后预览。</p>
      </div>
    </div>

    <div class="panel">
      <h2>检测结果图</h2>
      <div class="preview-box">
        <img v-if="resultImageUrl" :src="resultImageUrl" alt="检测结果图" />
        <p v-else-if="loading">正在等待检测结果...</p>
        <p v-else>检测完成后将在这里展示结果图。</p>
      </div>
    </div>

    <div class="panel panel-full">
      <h2>检测结果信息</h2>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      <div v-if="result" class="result-content">
        <p><strong>任务 ID：</strong>{{ result.task_id }}</p>
        <p><strong>原始文件名：</strong>{{ result.original_filename }}</p>
        <p><strong>总检测数量：</strong>{{ result.summary.total_detections }}</p>
        <p><strong>处理耗时：</strong>{{ result.process_time }} 秒</p>

        <div class="result-section">
          <h3>类别统计</h3>
          <ul v-if="Object.keys(result.summary.class_counts).length > 0">
            <li
              v-for="(count, className) in result.summary.class_counts"
              :key="className"
            >
              {{ className }}：{{ count }}
            </li>
          </ul>
          <p v-else>当前未检测到目标类别。</p>
        </div>

        <div class="result-section">
          <h3>检测明细</h3>
          <ul v-if="result.detections.length > 0">
            <li v-for="(item, index) in result.detections" :key="`${item.class_name}-${index}`">
              {{ index + 1 }}. {{ item.class_name }} | 置信度 {{ item.confidence }} | bbox:
              [{{ item.bbox.join(", ") }}]
            </li>
          </ul>
          <p v-else>当前未检测到目标。</p>
        </div>
      </div>

      <p v-else-if="!loading">尚未发起图片检测。</p>
    </div>
  </section>
</template>

<style scoped>
.result-layout {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.panel {
  padding: 16px;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  background: #ffffff;
}

.panel-full {
  grid-column: 1 / -1;
}

.preview-box {
  min-height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  border: 1px dashed #cbd5e1;
  border-radius: 6px;
  background: #f8fafc;
}

.preview-box img {
  max-width: 100%;
  max-height: 360px;
  display: block;
}

.result-content p {
  margin: 8px 0;
}

.result-section {
  margin-top: 16px;
}

.result-section ul {
  margin: 8px 0 0;
  padding-left: 20px;
}

.error-message {
  color: #dc2626;
}

@media (max-width: 768px) {
  .result-layout {
    grid-template-columns: 1fr;
  }
}
</style>
