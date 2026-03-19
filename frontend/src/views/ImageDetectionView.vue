<script setup lang="ts">
import { computed, onUnmounted, ref } from "vue";

import { API_BASE_URL, ApiError } from "../api/client";
import { detectImage } from "../api/detect";
import ImageDetectForm from "../components/image-detection/ImageDetectForm.vue";
import ImageDetectResult from "../components/image-detection/ImageDetectResult.vue";
import PageContainer from "../components/PageContainer.vue";
import type { ImageDetectionResponse } from "../types/detect";
import { joinUrl } from "../utils";

const loading = ref(false);
const errorMessage = ref("");
const originalPreviewUrl = ref<string | null>(null);
const result = ref<ImageDetectionResponse | null>(null);

const resultImageUrl = computed(() => {
  if (!result.value?.result_image_url) {
    return null;
  }

  return joinUrl(API_BASE_URL, result.value.result_image_url);
});

function revokePreviewUrl() {
  if (originalPreviewUrl.value) {
    URL.revokeObjectURL(originalPreviewUrl.value);
    originalPreviewUrl.value = null;
  }
}

function handleFileChange(file: File | null) {
  revokePreviewUrl();
  result.value = null;
  errorMessage.value = "";

  if (file) {
    originalPreviewUrl.value = URL.createObjectURL(file);
  }
}

async function handleDetect(payload: { file: File; conf?: number; iou?: number }) {
  loading.value = true;
  errorMessage.value = "";

  try {
    result.value = await detectImage(payload.file, payload.conf, payload.iou);
  } catch (error) {
    if (error instanceof ApiError) {
      errorMessage.value = error.message;
    } else if (error instanceof Error) {
      errorMessage.value = error.message;
    } else {
      errorMessage.value = "图片检测失败，请稍后重试。";
    }
  } finally {
    loading.value = false;
  }
}

onUnmounted(() => {
  revokePreviewUrl();
});
</script>

<template>
  <PageContainer>
    <div class="page-header">
      <h1>图片检测</h1>
      <RouterLink class="back-link" to="/">返回首页</RouterLink>
    </div>

    <p class="page-description">
      当前页面用于第一次真实图片检测联调，包含图片上传、参数输入、结果图和基础结果信息展示。
    </p>

    <div class="layout">
      <ImageDetectForm :loading="loading" @file-change="handleFileChange" @submit="handleDetect" />
      <ImageDetectResult
        :error-message="errorMessage"
        :loading="loading"
        :original-preview-url="originalPreviewUrl"
        :result="result"
        :result-image-url="resultImageUrl"
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
