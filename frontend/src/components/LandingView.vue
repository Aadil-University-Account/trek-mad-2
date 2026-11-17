<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'
import ChartCanvas from '../components/ChartCanvas.vue'

const stats = ref(null)

onMounted(async () => {
  try {
    stats.value = (await api.get('/public/stats')).data
  } catch (e) {
    /* backend not running - page still works */
  }
})
</script>

<template>
  <div class="container page">
    <section class="hero">
      <span class="badge-soft">Trekking Management</span>
      <h1>Plan, book and manage treks in one place.</h1>
      <p class="lead text-muted">
        TrekMate connects trek organizers, staff and trekkers. Browse open treks, book your slot
        and track your trekking history.
      </p>
      <div class="d-flex gap-2 flex-wrap">
        <router-link to="/register" class="btn btn-primary btn-lg">Get started</router-link>
        <router-link to="/login" class="btn btn-outline-primary btn-lg">Login</router-link>
      </div>
    </section>

    <section v-if="stats" class="mt-5">
      <h5 class="fw-bold mb-3">TrekMate in numbers</h5>
      <div class="row g-3 mb-3">
        <div class="col-6 col-md-3"><div class="stat-card"><div class="label">Treks</div><div class="value">{{ stats.total_treks }}</div></div></div>
        <div class="col-6 col-md-3"><div class="stat-card"><div class="label">Open for booking</div><div class="value">{{ stats.open_treks }}</div></div></div>
        <div class="col-6 col-md-3"><div class="stat-card"><div class="label">Completed</div><div class="value">{{ stats.completed_treks }}</div></div></div>
        <div class="col-6 col-md-3"><div class="stat-card"><div class="label">Trekkers</div><div class="value">{{ stats.trekkers }}</div></div></div>
      </div>
      <div v-if="stats.popular.length" class="card-box">
        <h6 class="fw-bold">Popular treks</h6>
        <ChartCanvas type="bar" label="Bookings" :labels="stats.popular.map((p) => p.name)" :values="stats.popular.map((p) => p.count)" />
      </div>
    </section>

    <section class="row g-3 mt-4">
      <div class="col-md-4"><div class="card-box h-100"><h6 class="fw-bold">1. Register</h6><p class="text-muted mb-0">Create a free trekker account in a few seconds.</p></div></div>
      <div class="col-md-4"><div class="card-box h-100"><h6 class="fw-bold">2. Pick a trek</h6><p class="text-muted mb-0">Filter by difficulty, location and duration.</p></div></div>
      <div class="col-md-4"><div class="card-box h-100"><h6 class="fw-bold">3. Book &amp; go</h6><p class="text-muted mb-0">Book a slot, get reminders and track your history.</p></div></div>
    </section>
  </div>
</template>