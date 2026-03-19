<script setup lang="ts">
import { computed, ref } from "vue";

import { API_BASE_URL, ApiError } from "../api/client";
import { detectVideo } from "../api/detect";
import PageContainer from "../components/PageContainer.vue";
import VideoDetectForm from "../components/video-detection/VideoDetectForm.vue";
import VideoDetectResult from "../components/video-detection/VideoDetectResult.vue";
import type { VideoDetectionResponse } from "../types/detect";
import { joinUrl } from "../utils";

const loading = ref(false);
const errorMessage = ref("");
const result = ref<VideoDetectionResponse | null>(null);

const resultVideoUrl = computed(() => {
  if (!result.value?.result_video_url) {
    return null;
  }

  return joinUrl(API_BASE_URL, result.value.result_video_url);
});

function handleFileChange(file: File | null) {
  result.value = null;
  errorMessage.value = "";
}

async function handleDetect(payload: { file: File; conf?: number; iou?: number }) {
  loading.value = true;
  errorMessage.value = "";

  try {
    result.value = await detectVideo(payload.file, payload.conf, payload.iou);
  } catch (error) {
    if (error instanceof ApiError) {
      errorMessage.value = error.message;
    } else if (error instanceof Error) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = "视频检测失败，请稍后重试。";
    }
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <PageContainer>
    <section class="hero">
      <div class="hero-content">
        <p class="hero-eyebrow">Underwater Target Detection</p>
        <h1>视频检测与分析</h1>
        <p class="page-description">
          面向演示与分析展示的视频检测页，聚焦结果播放、核心指标读取、类别比较、时间区间理解与逐秒趋势观察。
        </p>
      </div>
      <RouterLink class="back-link" to="/">返回首页</RouterLink>
    </section>

    <div class="layout">
      <VideoDetectForm :loading="loading" @file-change="handleFileChange" @submit="handleDetect" />
      <VideoDetectResult
        :error-message="errorMessage"
        :loading="loading"
        :result="result"
        :result-video-url="resultVideoUrl"
      />
    </div>
  </PageContainer>
</template>

<style scoped>
.hero {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 28px 32px;
  margin-bottom: 24px;
  border-radius: var(--panel-radius);
  background:
    radial-gradient(circle at left top, rgba(34, 211, 238, 0.08), transparent 26%),
    rgba(10, 18, 32, 0.42);
  border: 1px solid var(--panel-border);
  box-shadow: var(--glow-soft);
  backdrop-filter: blur(18px);
}

.hero-content {
  max-width: 720px;
}

.hero-eyebrow {
  margin: 0 0 10px;
  color: var(--accent);
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-size: 12px;
}

.hero h1 {
  margin: 0;
  color: var(--text-primary);
  font-size: 44px;
  line-height: 1.1;
  text-shadow: 0 0 18px rgba(34, 211, 238, 0.08);
}

.back-link {
  align-self: flex-start;
  padding: 10px 16px;
  border-radius: 999px;
  color: var(--text-primary);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--panel-border);
}

.page-description {
  margin: 14px 0 0;
  color: var(--text-secondary);
  font-size: 16px;
}

.layout {
  display: grid;
  gap: 20px;
}

@media (max-width: 768px) {
  .hero {
    flex-direction: column;
    padding: 24px;
    border-radius: 28px;
  }

  .hero h1 {
    font-size: 34px;
  }

  .back-link {
    align-self: flex-start;
  }
}
</style>
