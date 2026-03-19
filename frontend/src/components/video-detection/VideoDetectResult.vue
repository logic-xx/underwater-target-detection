<script setup lang="ts">
import type { VideoDetectionResponse } from "../../types/detect";

defineProps<{
  selectedFileName: string;
  result: VideoDetectionResponse | null;
  resultVideoUrl: string | null;
  loading?: boolean;
  errorMessage?: string;
}>();
</script>

<template>
  <section class="result-layout">
    <div class="panel">
      <h2>已选择视频</h2>
      <p v-if="selectedFileName">{{ selectedFileName }}</p>
      <p v-else>请选择一个视频文件后再开始检测。</p>
    </div>

    <div class="panel">
      <h2>检测结果视频</h2>
      <div class="video-box">
        <video v-if="resultVideoUrl" :src="resultVideoUrl" controls />
        <p v-else-if="loading">正在等待检测结果视频...</p>
        <p v-else>检测完成后将在这里展示结果视频。</p>
      </div>
    </div>

    <div class="panel panel-full">
      <h2>检测结果信息</h2>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <div v-if="result" class="result-content">
        <p><strong>任务 ID：</strong>{{ result.task_id }}</p>
        <p><strong>处理耗时：</strong>{{ result.process_time }} 秒</p>

        <div class="result-section">
          <h3>视频信息</h3>
          <ul>
            <li>fps：{{ result.video_info.fps }}</li>
            <li>frame_count：{{ result.video_info.frame_count }}</li>
            <li>duration：{{ result.video_info.duration }}</li>
            <li>width：{{ result.video_info.width }}</li>
            <li>height：{{ result.video_info.height }}</li>
          </ul>
        </div>

        <div class="result-section">
          <h3>class_frame_counts</h3>
          <ul v-if="Object.keys(result.analysis.class_frame_counts).length > 0">
            <li
              v-for="(count, className) in result.analysis.class_frame_counts"
              :key="className"
            >
              {{ className }}：{{ count }}
            </li>
          </ul>
          <p v-else>当前没有类别帧数统计结果。</p>
        </div>

        <div class="result-section">
          <h3>time_intervals</h3>
          <ul v-if="Object.keys(result.analysis.time_intervals).length > 0">
            <li
              v-for="(intervals, className) in result.analysis.time_intervals"
              :key="className"
            >
              {{ className }}：
              <span v-if="intervals.length > 0">
                <span
                  v-for="(interval, index) in intervals"
                  :key="`${className}-${index}`"
                  class="interval-item"
                >
                  [{{ interval[0] }} - {{ interval[1] }}]
                </span>
              </span>
              <span v-else>无区间</span>
            </li>
          </ul>
          <p v-else>当前没有时间区间统计结果。</p>
        </div>

        <div class="result-section">
          <h3>per_second_counts</h3>
          <ul v-if="result.analysis.per_second_counts.length > 0">
            <li
              v-for="item in result.analysis.per_second_counts"
              :key="item.second"
            >
              second={{ item.second }}, count={{ item.count }}
            </li>
          </ul>
          <p v-else>当前没有逐秒统计结果。</p>
        </div>
      </div>

      <p v-else-if="!loading">尚未发起视频检测。</p>
    </div>
  </section>
</template>

<style scoped>
.result-layout {
  display: grid;
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

.video-box {
  min-height: 260px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
  border: 1px dashed #cbd5e1;
  border-radius: 6px;
  background: #f8fafc;
}

.video-box video {
  width: 100%;
  max-width: 100%;
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

.interval-item {
  margin-right: 8px;
}

.error-message {
  color: #dc2626;
}
</style>
