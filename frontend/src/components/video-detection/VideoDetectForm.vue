<script setup lang="ts">
import { computed, reactive } from "vue";

const props = defineProps<{
  loading?: boolean;
}>();

const emit = defineEmits<{
  fileChange: [File | null];
  submit: [{ file: File; conf?: number; iou?: number }];
}>();

const formState = reactive({
  file: null as File | null,
  conf: "0.5",
  iou: "0.5",
});

const canSubmit = computed(() => !props.loading && formState.file !== null);

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement;
  formState.file = target.files?.[0] ?? null;
  emit("fileChange", formState.file);
}

function parseOptionalNumber(value: string): number | undefined {
  if (value.trim() === "") {
    return undefined;
  }

  const parsedValue = Number(value);
  return Number.isNaN(parsedValue) ? undefined : parsedValue;
}

function handleSubmit() {
  if (!formState.file) {
    return;
  }

  emit("submit", {
    file: formState.file,
    conf: parseOptionalNumber(formState.conf),
    iou: parseOptionalNumber(formState.iou),
  });
}
</script>

<template>
  <section class="panel">
    <h2>检测参数</h2>

    <div class="field-group">
      <label class="field-label" for="video-file">上传视频</label>
      <input
        id="video-file"
        accept="video/*"
        type="file"
        @change="handleFileChange"
      />
    </div>

    <div class="field-group">
      <label class="field-label" for="video-conf">conf</label>
      <input id="video-conf" v-model="formState.conf" step="0.01" type="number" />
    </div>

    <div class="field-group">
      <label class="field-label" for="video-iou">iou</label>
      <input id="video-iou" v-model="formState.iou" step="0.01" type="number" />
    </div>

    <button :disabled="!canSubmit" type="button" @click="handleSubmit">
      {{ loading ? "处理中..." : "开始视频检测" }}
    </button>
  </section>
</template>

<style scoped>
.panel {
  padding: 16px;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  background: #ffffff;
}

.field-group {
  margin-bottom: 16px;
}

.field-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
}

input[type="file"],
input[type="number"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
}

button {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  background: #2563eb;
  color: #ffffff;
  cursor: pointer;
}

button:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}
</style>
