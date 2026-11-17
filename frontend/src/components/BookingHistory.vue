<script setup>
import { ref } from 'vue'

const bookings = ref([
  { id: 1, trek: 'Himalayan Escape', date: '2026-11-28', status: 'Confirmed' },
  { id: 2, trek: 'Lakeside Trail', date: '2026-12-12', status: 'Pending' },
])
</script>

<template>
  <div class="card-box">
    <h5 class="mb-3">My bookings</h5>
    <div v-if="bookings.length" class="list-group list-group-flush">
      <div v-for="booking in bookings" :key="booking.id" class="list-group-item d-flex justify-content-between align-items-center px-0">
        <div>
          <div class="fw-semibold">{{ booking.trek }}</div>
          <small class="text-muted">{{ booking.date }}</small>
        </div>
        <span class="badge-soft">{{ booking.status }}</span>
      </div>
    </div>
    <div v-else class="text-muted">No bookings yet.</div>
  </div>
</template>
