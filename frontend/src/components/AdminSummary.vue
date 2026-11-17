<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const stats = ref({ total_treks: 0, total_users: 0, total_staff: 0, total_bookings: 0 })

onMounted(async () => {
  const res = await api.get('/admin/dashboard')
  stats.value = res.data
})
</script>

<template>
  <div>
    <div class="row g-3 mb-4">
      <div class="col-6 col-lg-3">
        <div class="stat-card"><div class="label">Total treks</div><div class="value">{{ stats.total_treks }}</div></div>
      </div>
      <div class="col-6 col-lg-3">
        <div class="stat-card"><div class="label">Trekkers</div><div class="value">{{ stats.total_users }}</div></div>
      </div>
      <div class="col-6 col-lg-3">
        <div class="stat-card"><div class="label">Trek staff</div><div class="value">{{ stats.total_staff }}</div></div>
      </div>
      <div class="col-6 col-lg-3">
        <div class="stat-card"><div class="label">Bookings</div><div class="value">{{ stats.total_bookings }}</div></div>
      </div>
    </div>
  </div>
</template>