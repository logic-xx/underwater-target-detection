<script setup lang="ts">
import PageContainer from "../components/PageContainer.vue";
</script>

<template>
  <PageContainer>
    <h1>水下目标检测系统</h1>
    <p>这是当前前端联调阶段的基础首页，可从这里进入图片检测或视频检测页面。</p>

    <nav class="nav-links">
      <RouterLink class="nav-link" to="/image">进入图片检测</RouterLink>
      <RouterLink class="nav-link" to="/video">进入视频检测</RouterLink>
    </nav>

    <section class="home-panel">
      <h2>当前可用入口</h2>
      <p>图片检测页将优先用于第一次真实接口联调。</p>
      <p>视频检测页本阶段仍保留为基础占位页面。</p>
    </section>
  </PageContainer>
</template>

<style scoped>
.nav-links {
  display: flex;
  gap: 12px;
  margin: 24px 0;
}

.nav-link {
  display: inline-block;
  padding: 10px 16px;
  border: 1px solid #2563eb;
  border-radius: 6px;
  color: #2563eb;
}

.home-panel {
  padding: 16px;
  border: 1px solid #d0d7de;
  border-radius: 8px;
  background: #ffffff;
}
</style>
