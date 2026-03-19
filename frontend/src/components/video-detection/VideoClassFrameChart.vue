<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as echarts from "echarts";

const props = defineProps<{
  items: Array<[string, number]>;
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;
let resizeObserver: ResizeObserver | null = null;

const sortedItems = computed(() => [...props.items].sort((a, b) => b[1] - a[1]));

function renderChart() {
  if (!chartRef.value) {
    return;
  }

  if (!chart) {
    chart = echarts.init(chartRef.value);
  }

  chart.setOption({
    backgroundColor: "transparent",
    grid: {
      left: 100,
      right: 24,
      top: 20,
      bottom: 20,
      containLabel: true,
    },
    tooltip: {
      trigger: "axis",
      axisPointer: {
        type: "shadow",
      },
    },
    xAxis: {
      type: "value",
      axisLabel: {
        color: "#8fb6c9",
      },
      splitLine: {
        lineStyle: {
          color: "rgba(56, 189, 248, 0.12)",
        },
      },
    },
    yAxis: {
      type: "category",
      data: sortedItems.value.map(([className]) => className),
      axisTick: {
        show: false,
      },
      axisLine: {
        show: false,
      },
      axisLabel: {
        color: "#d9f3ff",
      },
    },
    series: [
      {
        type: "bar",
        data: sortedItems.value.map(([, count]) => count),
        barWidth: 16,
        showBackground: true,
        backgroundStyle: {
          color: "rgba(255, 255, 255, 0.05)",
          borderRadius: 999,
        },
        itemStyle: {
          borderRadius: 999,
          color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
            { offset: 0, color: "#38bdf8" },
            { offset: 1, color: "#22d3ee" },
          ]),
          shadowBlur: 24,
          shadowColor: "rgba(34, 211, 238, 0.26)",
        },
        label: {
          show: true,
          position: "right",
          color: "#ecfeff",
          formatter: "{c} 帧",
        },
      },
    ],
  });
}

watch(
  sortedItems,
  async () => {
    await nextTick();
    renderChart();
  },
  { deep: true }
);

onMounted(async () => {
  await nextTick();
  renderChart();

  if (chartRef.value) {
    resizeObserver = new ResizeObserver(() => {
      chart?.resize();
    });
    resizeObserver.observe(chartRef.value);
  }
});

onBeforeUnmount(() => {
  resizeObserver?.disconnect();
  chart?.dispose();
  chart = null;
});
</script>

<template>
  <div ref="chartRef" class="chart-container"></div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 320px;
}
</style>
