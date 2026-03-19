<script setup lang="ts">
import { computed, reactive, ref } from "vue";

const props = defineProps<{
  loading?: boolean;
}>();

const emit = defineEmits<{
  fileChange: [File | null];
  submit: [{ file: File; conf?: number; iou?: number }];
}>();

const formState = reactive({
  file: null as File | null,
  conf: 0.5,
  iou: 0.5,
});

const fileInputRef = ref<HTMLInputElement | null>(null);
const canSubmit = computed(() => !props.loading && formState.file !== null);
const selectedFileMeta = computed(() => {
  if (!formState.file) {
    return null;
  }

  const fileSizeMb = (formState.file.size / 1024 / 1024).toFixed(2);
  return `${formState.file.name} · ${fileSizeMb} MB`;
});

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  formState.file = target.files?.[0] ?? null;
  emit("fileChange", formState.file);
}

function triggerFilePicker() {
  fileInputRef.value?.click();
}

function handleSubmit() {
  if (!formState.file) {
    return;
  }

  emit("submit", {
    file: formState.file,
    conf: formState.conf,
    iou: formState.iou,
  });
}
</script>

<template>
  <section class="upload-panel">
    <div class="panel-header">
      <div>
        <p class="eyebrow">Video Analysis Console</p>
        <h2>上传与参数设置</h2>
        <p class="panel-description">
          上传待检测视频，使用滑块快速调整阈值，然后开始生成可播放结果与分析数据。
        </p>
      </div>
    </div>

    <button class="upload-card" type="button" @click="triggerFilePicker">
      <span class="upload-icon">+</span>
      <span class="upload-title">选择待检测视频</span>
      <span class="upload-subtitle">
        {{ selectedFileMeta || "支持常见视频格式，点击后从本地选择文件" }}
      </span>
      <span class="upload-hint">
        {{ selectedFileMeta ? "重新选择文件" : "点击上传" }}
      </span>
    </button>

    <div class="field-group field-group-hidden">
      <input
        ref="fileInputRef"
        id="video-file"
        accept="video/*"
        type="file"
        @change="handleFileChange"
      />
    </div>

    <div class="slider-card">
      <div class="slider-header">
        <label class="field-label" for="video-conf">置信度阈值 conf</label>
        <strong class="slider-value">{{ formState.conf.toFixed(2) }}</strong>
      </div>
      <el-slider
        id="video-conf"
        v-model="formState.conf"
        :max="1"
        :min="0"
        :step="0.01"
      />
    </div>

    <div class="slider-card">
      <div class="slider-header">
        <label class="field-label" for="video-iou">IoU 阈值</label>
        <strong class="slider-value">{{ formState.iou.toFixed(2) }}</strong>
      </div>
      <el-slider
        id="video-iou"
        v-model="formState.iou"
        :max="1"
        :min="0"
        :step="0.01"
      />
    </div>

    <div class="action-row">
      <el-button
        :disabled="!canSubmit"
        :loading="loading"
        class="detect-button"
        size="large"
        type="primary"
        @click="handleSubmit"
      >
        {{ loading ? "正在生成检测结果..." : "开始视频检测" }}
      </el-button>
    </div>
  </section>
</template>

<style scoped>
.upload-panel {
  position: relative;
  overflow: hidden;
  padding: 28px;
  border-radius: var(--panel-radius);
  background:
    radial-gradient(circle at top left, rgba(34, 211, 238, 0.14), transparent 28%),
    var(--panel-bg-strong);
  border: 1px solid var(--panel-border);
  box-shadow: var(--shadow-soft), var(--glow-soft);
  backdrop-filter: blur(18px);
  color: var(--text-primary);
}

.panel-header {
  margin-bottom: 20px;
}

.field-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-primary);
}

.eyebrow {
  margin: 0 0 8px;
  color: var(--accent);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  font-size: 12px;
}

.panel-header h2 {
  margin: 0;
  font-size: 32px;
  line-height: 1.2;
}

.panel-description {
  margin: 12px 0 0;
  max-width: 520px;
  color: var(--text-secondary);
}

.upload-card {
  width: 100%;
  display: grid;
  gap: 8px;
  padding: 24px;
  border: 1px dashed rgba(34, 211, 238, 0.48);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.04);
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.03),
    0 0 0 rgba(34, 211, 238, 0);
  color: inherit;
  text-align: left;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease;
}

.upload-card:hover {
  transform: translateY(-2px);
  border-color: rgba(34, 211, 238, 0.9);
  background: rgba(255, 255, 255, 0.07);
  box-shadow:
    0 0 0 1px rgba(34, 211, 238, 0.16),
    0 0 34px rgba(34, 211, 238, 0.14);
}

.upload-icon {
  width: 44px;
  height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(34, 211, 238, 0.22), rgba(56, 189, 248, 0.16));
  color: var(--accent);
  font-size: 28px;
  line-height: 1;
  box-shadow: 0 0 22px rgba(34, 211, 238, 0.12);
}

.upload-title {
  font-size: 18px;
  font-weight: 700;
}

.upload-subtitle {
  color: var(--text-secondary);
  word-break: break-all;
}

.upload-hint {
  color: var(--accent);
  font-size: 13px;
}

.field-group-hidden {
  display: none;
}

.slider-card {
  margin-top: 18px;
  padding: 18px 18px 8px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.045);
  border: 1px solid var(--panel-border);
  backdrop-filter: blur(10px);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
}

.slider-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.slider-value {
  color: var(--accent);
  font-size: 18px;
}

:deep(.el-slider__runway) {
  background-color: rgba(147, 183, 200, 0.14);
}

:deep(.el-slider__bar) {
  background: linear-gradient(90deg, var(--accent), var(--accent-strong));
  box-shadow: 0 0 14px rgba(34, 211, 238, 0.22);
}

:deep(.el-slider__button) {
  border: 2px solid #dff8ff;
  background: var(--accent);
  box-shadow: 0 0 16px rgba(34, 211, 238, 0.28);
}

.action-row {
  margin-top: 22px;
}

.detect-button {
  min-width: 220px;
  height: 48px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(90deg, var(--accent), var(--accent-strong));
  box-shadow:
    0 16px 34px rgba(34, 211, 238, 0.16),
    0 0 26px rgba(34, 211, 238, 0.12);
}

:deep(.detect-button:hover) {
  background: linear-gradient(90deg, #45e6ff, #55c9ff);
}

:deep(.detect-button.is-disabled) {
  background: rgba(148, 163, 184, 0.4);
  box-shadow: none;
}

@media (max-width: 768px) {
  .upload-panel {
    padding: 22px;
    border-radius: 24px;
  }

  .panel-header h2 {
    font-size: 28px;
  }

  .action-row :deep(.detect-button) {
    width: 100%;
  }
}
</style>
