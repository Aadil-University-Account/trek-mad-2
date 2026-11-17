<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import ChartCanvas from './ChartCanvas.vue'

const stats = ref({ total_treks: 0, total_users: 0, total_staff: 0, total_bookings: 0 })
const charts = ref(null)

onMounted(async () => {
  stats.value = (await api.get('/admin/dashboard')).data
  charts.value = (await api.get('/admin/stats')).data
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

    <div v-if="charts" class="row g-3">
      <div class="col-lg-6">
        <div class="card-box">
          <h6 class="fw-bold">Most popular treks</h6>
          <ChartCanvas v-if="charts.popular.length" type="bar" label="Bookings"
                       :labels="charts.popular.map((p) => p.name)" :values="charts.popular.map((p) => p.count)" />
          <div v-else class="empty">No bookings yet.</div>
        </div>
      </div>
      <div class="col-lg-6">
        <div class="card-box">
          <h6 class="fw-bold">Booking trend (last 6 months)</h6>
          <ChartCanvas type="line" label="Bookings"
                       :labels="charts.monthly.map((m) => m.month)" :values="charts.monthly.map((m) => m.count)" />
        </div>
      </div>
      <div class="col-lg-6">
        <div class="card-box">
          <h6 class="fw-bold">Booking status</h6>
          <ChartCanvas type="doughnut" label="Bookings"
                       :labels="Object.keys(charts.booking_status)" :values="Object.values(charts.booking_status)" />
        </div>
      </div>
      <div class="col-lg-6">
        <div class="card-box">
          <h6 class="fw-bold">Treks by status</h6>
          <ChartCanvas type="bar" label="Treks"
                       :labels="Object.keys(charts.trek_status)" :values="Object.values(charts.trek_status)" />
        </div>
      </div>
    </div>
  </div>
</template>