<script setup>
const reportRows = [
  { label: 'Bookings this month', value: '328' },
  { label: 'Average occupancy', value: '74%' },
  { label: 'Cancelled trips', value: '12' },
  { label: 'Top destination', value: 'Manali' },
]
</script>

<template>
  <div class="row g-3">
    <div v-for="row in reportRows" :key="row.label" class="col-md-6 col-xl-3">
      <div class="stat-card">
        <div class="label">{{ row.label }}</div>
        <div class="value">{{ row.value }}</div>
      </div>
    </div>
  </div>
</template>
