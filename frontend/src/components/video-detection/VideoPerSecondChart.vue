<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as echarts from "echarts";

const props = defineProps<{
  items: Array<{
    second: number;
    count: number;
  }>;
}>();

const chartRef = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;
let resizeObserver: ResizeObserver | null = null;

const seconds = computed(() => props.items.map((item) => `${item.second}s`));
const counts = computed(() => props.items.map((item) => item.count));

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
      left: 36,
      right: 24,
      top: 24,
      bottom: 36,
      containLabel: true,
    },
    tooltip: {
      trigger: "axis",
    },
    xAxis: {
      type: "category",
      data: seconds.value,
      boundaryGap: false,
      axisLabel: {
        color: "#8fb6c9",
      },
      axisLine: {
        lineStyle: {
          color: "rgba(56, 189, 248, 0.2)",
        },
      },
    },
    yAxis: {
      type: "value",
      minInterval: 1,
      axisLabel: {
        color: "#8fb6c9",
      },
      splitLine: {
        lineStyle: {
          color: "rgba(56, 189, 248, 0.12)",
        },
      },
    },
    series: [
      {
        type: "line",
        smooth: true,
        data: counts.value,
        symbol: "circle",
        symbolSize: 8,
        lineStyle: {
          width: 3,
          color: "#22d3ee",
          shadowBlur: 16,
          shadowColor: "rgba(34, 211, 238, 0.22)",
        },
        itemStyle: {
          color: "#38bdf8",
          borderColor: "#ecfeff",
          borderWidth: 2,
          shadowBlur: 12,
          shadowColor: "rgba(34, 211, 238, 0.2)",
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: "rgba(34, 211, 238, 0.24)" },
            { offset: 1, color: "rgba(34, 211, 238, 0.02)" },
          ]),
        },
      },
    ],
  });
}

watch(
  () => props.items,
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
