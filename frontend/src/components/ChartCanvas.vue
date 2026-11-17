<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

// type: 'bar' | 'line' | 'doughnut'
const props = defineProps({ type: String, labels: Array, values: Array, label: String })

const canvas = ref(null)
let chart = null
const colors = ['#0f766e', '#14b8a6', '#f59e0b', '#6366f1', '#ef4444', '#94a3b8']

function draw() {
  if (chart) chart.destroy()
  const round = props.type === 'doughnut'
  chart = new Chart(canvas.value, {
    type: props.type,
    data: {
      labels: props.labels,
      datasets: [
        {
          label: props.label,
          data: props.values,
          backgroundColor: round ? colors : props.type === 'line' ? 'rgba(15,118,110,.15)' : '#0f766e',
          borderColor: '#0f766e',
          borderRadius: 6,
          fill: props.type === 'line',
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: round } },
      scales: round ? {} : { y: { beginAtZero: true, ticks: { precision: 0 } } },
    },
  })
}

onMounted(draw)
watch(() => [props.labels, props.values], draw)
onBeforeUnmount(() => chart && chart.destroy())
</script>

<template>
  <div style="height: 260px"><canvas ref="canvas"></canvas></div>
</template>