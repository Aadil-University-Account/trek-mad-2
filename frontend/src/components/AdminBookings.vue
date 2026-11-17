<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const bookings = ref([])
const search = ref('')
const status = ref('')

async function load() {
  const res = await api.get('/admin/bookings', { params: { q: search.value, status: status.value } })
  bookings.value = res.data
}
onMounted(load)
</script>

<template>
  <div>
    <div class="d-flex flex-wrap gap-2 mb-3">
      <input v-model="search" @input="load" class="form-control" style="max-width: 320px"
             placeholder="Search by user, trek or ID" />
      <select v-model="status" @change="load" class="form-select" style="max-width: 180px">
        <option value="">All statuses</option>
        <option>Booked</option><option>Cancelled</option><option>Completed</option>
      </select>
    </div>

    <div class="card-box table-card">
      <div class="table-responsive">
        <table class="table">
          <thead><tr><th>#</th><th>Trekker</th><th>Trek</th><th>Trek dates</th><th>Booked on</th><th>Booking</th><th>Payment</th></tr></thead>
          <tbody>
            <tr v-for="b in bookings" :key="b.id">
              <td>{{ b.id }}</td>
              <td><div class="fw-semibold">{{ b.user_name }}</div><div class="trek-meta">ID {{ b.user_id }}</div></td>
              <td>{{ b.trek_name }}<div class="trek-meta">{{ b.location }}</div></td>
              <td class="small">{{ b.start_date }} → {{ b.end_date }}</td>
              <td class="small">{{ b.booking_date }}</td>
              <td><span class="badge-soft" :class="'st-' + b.status">{{ b.status }}</span></td>
              <td><span class="badge-soft" :class="'st-' + b.payment_status">{{ b.payment_status }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!bookings.length" class="empty">No bookings yet.</div>
    </div>
  </div>
</template>