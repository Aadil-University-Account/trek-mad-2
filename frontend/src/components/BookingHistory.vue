<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { errorMessage } from '../api'

const bookings = ref([])
const filter = ref('')
const message = ref('')
const error = ref('')

const shown = computed(() => bookings.value.filter((b) => !filter.value || b.status === filter.value))

async function load() {
  const res = await api.get('/my-bookings')
  bookings.value = res.data
}
onMounted(load)

function canCancel(b) {
  return b.status === 'Booked' && !['Ongoing', 'Completed'].includes(b.trek_status)
}

// ---- export booking history as CSV (runs as a Celery job)
const exporting = ref(false)
const exportFile = ref('')

async function startExport() {
  message.value = ''
  error.value = ''
  exportFile.value = ''
  exporting.value = true
  try {
    const res = await api.post('/export')
    waitForExport(res.data.task_id)
  } catch (err) {
    exporting.value = false
    error.value = errorMessage(err)
  }
}

// ask the server every 2 seconds if the job is finished
function waitForExport(taskId) {
  const timer = setInterval(async () => {
    const res = await api.get('/export/status/' + taskId)
    if (res.data.state === 'PENDING') return
    clearInterval(timer)
    exporting.value = false
    if (res.data.state === 'SUCCESS') {
      exportFile.value = res.data.filename
      alert('Your CSV export is ready! Click "Download CSV".')
    } else {
      error.value = 'Export failed. Is the Celery worker running?'
    }
  }, 2000)
}

async function downloadExport() {
  const res = await api.get('/export/download/' + exportFile.value, { responseType: 'blob' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(res.data)
  link.download = exportFile.value
  link.click()
}

async function cancel(b) {
  if (!confirm(`Cancel booking for ${b.trek_name}?`)) return
  message.value = ''
  error.value = ''
  try {
    const res = await api.put(`/bookings/${b.id}/cancel`)
    message.value = res.data.message
    load()
  } catch (err) {
    error.value = errorMessage(err)
  }
}
</script>

<template>
  <div>
    <div class="d-flex flex-wrap gap-2 justify-content-between mb-3">
      <select v-model="filter" class="form-select" style="max-width: 200px">
        <option value="">All bookings</option>
        <option>Booked</option><option>Completed</option><option>Cancelled</option>
      </select>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-primary" @click="startExport" :disabled="exporting">
          {{ exporting ? 'Preparing CSV...' : 'Export history (CSV)' }}
        </button>
        <button v-if="exportFile" class="btn btn-primary" @click="downloadExport">Download CSV</button>
      </div>
    </div>

    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

    <div class="card-box table-card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr><th>Trek</th><th>Dates</th><th>Booked on</th><th>Trek status</th><th>Booking</th><th>Payment</th><th></th></tr>
          </thead>
          <tbody>
            <tr v-for="b in shown" :key="b.id">
              <td><div class="fw-semibold">{{ b.trek_name }}</div><div class="trek-meta">{{ b.location }}</div></td>
              <td class="small">{{ b.start_date }} → {{ b.end_date }}</td>
              <td class="small">{{ b.booking_date }}</td>
              <td><span class="badge-soft" :class="'st-' + b.trek_status">{{ b.trek_status }}</span></td>
              <td><span class="badge-soft" :class="'st-' + b.status">{{ b.status }}</span></td>
              <td><span class="badge-soft" :class="'st-' + b.payment_status">{{ b.payment_status }}</span></td>
              <td class="text-end text-nowrap">
                <button v-if="canCancel(b)" class="btn btn-sm btn-outline-danger" @click="cancel(b)">Cancel</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!shown.length" class="empty">No bookings to show. Book your first trek!</div>
    </div>
  </div>
</template>