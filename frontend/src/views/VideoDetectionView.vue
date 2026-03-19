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
const selectedFileName = ref("");
const result = ref<VideoDetectionResponse | null>(null);

const resultVideoUrl = computed(() => {
  if (!result.value?.result_video_url) {
    return null;
  }

  return joinUrl(API_BASE_URL, result.value.result_video_url);
});

function handleFileChange(file: File | null) {
  selectedFileName.value = file?.name ?? "";
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
    <div class="page-header">
      <h1>视频检测</h1>
      <RouterLink class="back-link" to="/">返回首页</RouterLink>
    </div>

    <p class="page-description">
      当前页面用于第一次真实视频检测联调，包含视频上传、参数输入、结果视频播放和基础统计信息展示。
    </p>

    <div class="layout">
      <VideoDetectForm :loading="loading" @file-change="handleFileChange" @submit="handleDetect" />
      <VideoDetectResult
        :error-message="errorMessage"
        :loading="loading"
        :result="result"
        :result-video-url="resultVideoUrl"
        :selected-file-name="selectedFileName"
      />
    </div>
  </PageContainer>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.back-link {
  color: #2563eb;
}

.page-description {
  margin: 12px 0 24px;
}

.layout {
  display: grid;
  gap: 20px;
}
</style>
