<script setup>
import { ref, onMounted } from 'vue'
import api, { errorMessage } from '../api'
import Modal from './Modal.vue'

const reports = ref([])
const message = ref('')
const error = ref('')
const openReport = ref('')
const reportHtml = ref('')

async function load() {
  const res = await api.get('/admin/reports')
  reports.value = res.data
}
onMounted(load)

async function runJob(url) {
  message.value = ''
  error.value = ''
  try {
    const res = await api.post(url)
    message.value = res.data.message
    setTimeout(load, 3000)
  } catch (err) {
    error.value = errorMessage(err)
  }
}

async function view(file) {
  const res = await api.get('/admin/reports/' + file, { responseType: 'text' })
  reportHtml.value = res.data
  openReport.value = file
}
</script>

<template>
  <div>
    <div class="card-box mb-3">
      <h5 class="fw-bold">Scheduled jobs</h5>
      <p class="text-muted small mb-3">
        The monthly report is generated automatically on the 1st of every month (8:00 AM) and the daily
        reminders go out every day at 9:00 AM. You can also run them now for a demo.
      </p>
      <div class="d-flex flex-wrap gap-2">
        <button class="btn btn-primary" @click="runJob('/admin/report')">Generate monthly report now</button>
        <button class="btn btn-outline-primary" @click="runJob('/admin/reminders')">Send trek reminders now</button>
      </div>
    </div>

    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

    <div class="card-box table-card">
      <div class="table-responsive">
        <table class="table">
          <thead><tr><th>Generated monthly reports</th><th></th></tr></thead>
          <tbody>
            <tr v-for="r in reports" :key="r">
              <td>{{ r }}</td>
              <td class="text-end"><button class="btn btn-sm btn-outline-primary" @click="view(r)">View</button></td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!reports.length" class="empty">No reports yet.</div>
    </div>

    <Modal v-if="openReport" :title="openReport" wide @close="openReport = ''">
      <iframe :srcdoc="reportHtml" style="width: 100%; height: 480px; border: 0"></iframe>
    </Modal>
  </div>
</template>