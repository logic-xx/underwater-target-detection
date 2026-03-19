<script setup lang="ts">
import { computed } from "vue";

import type { VideoDetectionResponse } from "../../types/detect";
import VideoClassFrameChart from "./VideoClassFrameChart.vue";
import VideoPerSecondChart from "./VideoPerSecondChart.vue";

const props = defineProps<{
  result: VideoDetectionResponse | null;
  resultVideoUrl: string | null;
  loading?: boolean;
  errorMessage?: string;
}>();

const videoInfoCards = computed(() => {
  if (!props.result) {
    return [];
  }

  const { video_info: videoInfo, process_time: processTime } = props.result;
  return [
    { label: "帧率", value: `${videoInfo.fps} fps` },
    { label: "总帧数", value: `${videoInfo.frame_count}` },
    { label: "视频时长", value: `${videoInfo.duration} 秒` },
    { label: "分辨率", value: `${videoInfo.width} x ${videoInfo.height}` },
    { label: "处理耗时", value: `${processTime} 秒` },
  ];
});

const classFrameCountEntries = computed(() => {
  if (!props.result) {
    return [];
  }

  return Object.entries(props.result.analysis.class_frame_counts).sort((a, b) => b[1] - a[1]);
});

const timeIntervalEntries = computed(() => {
  if (!props.result) {
    return [];
  }

  return Object.entries(props.result.analysis.time_intervals).map(([className, intervals]) => ({
    className,
    intervals: intervals.map((interval) => {
      const durationSeconds = calculateDurationSeconds(interval[0], interval[1]);
      return {
        start: interval[0],
        end: interval[1],
        durationSeconds,
        durationText: formatDuration(durationSeconds),
        isShort: durationSeconds <= 1,
      };
    }),
  }));
});

function parseTimeLabel(value: string): number {
  const [minutes, seconds] = value.split(":").map((item) => Number(item));
  return minutes * 60 + seconds;
}

function calculateDurationSeconds(start: string, end: string): number {
  return Math.max(parseTimeLabel(end) - parseTimeLabel(start), 0);
}

function formatDuration(durationSeconds: number): string {
  if (durationSeconds <= 1) {
    return "极短区间";
  }

  return `持续 ${durationSeconds} 秒`;
}
</script>

<template>
  <section class="result-layout">
    <div class="panel panel-video">
      <h2>检测结果视频</h2>
      <div class="video-box">
        <video v-if="resultVideoUrl" :src="resultVideoUrl" controls />
        <p v-else-if="loading" class="empty-text">正在等待检测结果视频...</p>
        <p v-else class="empty-text">检测完成后将在这里展示结果视频。</p>
      </div>
    </div>

    <div class="panel panel-full">
      <div class="section-header">
        <div>
          <h2>检测总览</h2>
          <p class="section-description">以分析系统的方式展示视频概况、类别分布、时间区间和逐秒变化。</p>
        </div>
      </div>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

      <div v-if="result" class="result-content">
        <div class="summary-bar">
          <div class="summary-item">
            <span class="summary-label">任务 ID</span>
            <strong class="summary-value">{{ result.task_id }}</strong>
          </div>
        </div>

        <div class="result-section">
          <div class="section-header">
            <div>
              <h3>视频信息</h3>
              <p class="section-description">用卡片形式展示关键基础指标，便于快速阅读。</p>
            </div>
          </div>
          <div class="info-card-grid">
            <div
              v-for="item in videoInfoCards"
              :key="item.label"
              class="info-card"
            >
              <span class="info-card-label">{{ item.label }}</span>
              <strong class="info-card-value">{{ item.value }}</strong>
            </div>
          </div>
        </div>

        <div class="analysis-grid">
          <div class="result-section chart-panel">
            <div class="section-header">
              <div>
                <h3>类别出现帧数</h3>
                <p class="section-description">
                  使用横向柱状图更适合横向比较不同类别出现帧数，比饼图更利于分析差异。
                </p>
              </div>
            </div>
            <VideoClassFrameChart
              v-if="classFrameCountEntries.length > 0"
              :items="classFrameCountEntries"
            />
            <p v-else class="empty-text">当前没有类别帧数统计结果。</p>
          </div>

          <div class="result-section chart-panel">
            <div class="section-header">
              <div>
                <h3>逐秒数量变化</h3>
                <p class="section-description">使用折线图查看每秒总检测目标数的变化趋势。</p>
              </div>
            </div>
            <VideoPerSecondChart
              v-if="result.analysis.per_second_counts.length > 0"
              :items="result.analysis.per_second_counts"
            />
            <p v-else class="empty-text">当前没有逐秒统计结果。</p>
          </div>
        </div>

        <div class="result-section">
          <div class="section-header">
            <div>
              <h3>时间区间分析</h3>
              <p class="section-description">
                按类别分组展示时间区间，对很短的小区间做单独强调，避免纯文本堆叠。
              </p>
            </div>
          </div>
          <div v-if="timeIntervalEntries.length > 0" class="interval-group-list">
            <div
              v-for="group in timeIntervalEntries"
              :key="group.className"
              class="interval-group"
            >
              <div class="interval-group-header">
                <div class="interval-group-title">{{ group.className }}</div>
                <span class="interval-group-count">{{ group.intervals.length }} 个区间</span>
              </div>
              <div v-if="group.intervals.length > 0" class="interval-list">
                <div
                  v-for="(interval, index) in group.intervals"
                  :key="`${group.className}-${index}`"
                  class="interval-row"
                  :class="{ 'interval-row-short': interval.isShort }"
                >
                  <div class="interval-main">
                    <span class="interval-index">区间 {{ index + 1 }}</span>
                    <span class="interval-value">{{ interval.start }} - {{ interval.end }}</span>
                  </div>
                  <span class="interval-duration" :class="{ 'interval-duration-short': interval.isShort }">
                    {{ interval.durationText }}
                  </span>
                </div>
              </div>
              <p v-else class="empty-text">当前无时间区间。</p>
            </div>
          </div>
          <p v-else class="empty-text">当前没有时间区间统计结果。</p>
        </div>
      </div>

      <p v-else-if="!loading" class="empty-text">尚未发起视频检测。</p>
    </div>
  </section>
</template>

<style scoped>
.result-layout {
  display: grid;
  gap: 20px;
}

.panel {
  position: relative;
  overflow: hidden;
  padding: 20px;
  border-radius: var(--panel-radius);
  border: 1px solid var(--panel-border);
  background:
    radial-gradient(circle at top left, rgba(34, 211, 238, 0.1), transparent 24%),
    var(--panel-bg);
  box-shadow: var(--shadow-soft), var(--glow-soft);
  backdrop-filter: blur(20px);
  color: var(--text-primary);
}

.panel-video {
  padding: 24px;
}

.panel-full {
  display: grid;
  gap: 16px;
}

.panel h2,
.panel h3 {
  color: var(--text-primary);
}

.video-box {
  min-height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 14px;
  border: 1px solid var(--panel-border);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.03);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.02);
}

.video-box video {
  width: 100%;
  max-width: 100%;
  display: block;
  border-radius: 18px;
  box-shadow:
    0 12px 28px rgba(15, 23, 42, 0.28),
    0 0 24px rgba(34, 211, 238, 0.06);
}

.result-content {
  display: grid;
  gap: 24px;
}

.result-section {
  padding: 18px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid rgba(34, 211, 238, 0.12);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
}

.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.chart-panel {
  min-height: 420px;
}

.section-header {
  margin-bottom: 12px;
}

.section-header h2,
.section-header h3 {
  margin: 0;
}

.section-description {
  margin: 6px 0 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.5;
}

.summary-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.summary-item {
  width: 100%;
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--panel-border);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
}

.summary-label {
  display: block;
  margin-bottom: 6px;
  color: var(--text-secondary);
  font-size: 13px;
}

.summary-value {
  display: block;
  color: var(--text-primary);
  word-break: break-all;
}

.info-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
}

.info-card {
  padding: 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--panel-border);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
}

.info-card-label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-size: 13px;
}

.info-card-value {
  display: block;
  color: var(--text-primary);
  font-size: 18px;
  line-height: 1.4;
}

.interval-group-list {
  display: grid;
  gap: 14px;
}

.interval-group {
  padding: 14px 16px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--panel-border);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.02);
}

.interval-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.interval-group-title {
  font-weight: 700;
  color: var(--text-primary);
}

.interval-group-count {
  padding: 4px 10px;
  border-radius: 999px;
  color: var(--accent);
  background: rgba(34, 211, 238, 0.12);
  font-size: 12px;
  box-shadow: 0 0 16px rgba(34, 211, 238, 0.08);
}

.interval-list {
  display: grid;
  gap: 8px;
}

.interval-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(56, 189, 248, 0.08);
}

.interval-row-short {
  border-color: rgba(34, 211, 238, 0.34);
  background: rgba(34, 211, 238, 0.08);
  box-shadow: 0 0 24px rgba(34, 211, 238, 0.08);
}

.interval-main {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.interval-index {
  color: var(--text-secondary);
  font-size: 13px;
}

.interval-value {
  color: var(--text-primary);
  font-weight: 600;
}

.interval-duration {
  padding: 5px 10px;
  border-radius: 999px;
  color: #d9f8ff;
  background: rgba(56, 189, 248, 0.1);
  font-size: 12px;
}

.interval-duration-short {
  color: var(--accent);
  background: rgba(34, 211, 238, 0.14);
}

.empty-text {
  margin: 0;
  color: var(--text-secondary);
}

.error-message {
  margin: 0 0 16px;
  color: #fca5a5;
}

@media (max-width: 768px) {
  .analysis-grid {
    grid-template-columns: 1fr;
  }

  .interval-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
