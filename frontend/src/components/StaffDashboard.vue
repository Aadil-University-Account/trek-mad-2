<script setup>
import { ref, computed, onMounted } from 'vue'
import api, { errorMessage } from '../api'
import Modal from './Modal.vue'

const treks = ref([])
const message = ref('')
const error = ref('')
const slotInputs = ref({}) // trek id -> number typed in the box

const participantTrek = ref(null)
const participants = ref([])

const totalRegistered = computed(() => treks.value.reduce((sum, t) => sum + t.registered_count, 0))
const openCount = computed(() => treks.value.filter((t) => t.status === 'Open').length)

async function load() {
  const res = await api.get('/staff/treks')
  treks.value = res.data
  res.data.forEach((t) => (slotInputs.value[t.id] = t.available_slots))
}
onMounted(load)

async function run(promise) {
  message.value = ''
  error.value = ''
  try {
    const res = await promise
    message.value = res.data.message
    await load()
  } catch (err) {
    error.value = errorMessage(err)
  }
}

const saveSlots = (t) => run(api.put(`/staff/treks/${t.id}/slots`, { available_slots: slotInputs.value[t.id] }))
const setStatus = (t, status) => run(api.put(`/staff/treks/${t.id}/status`, { status }))

async function showParticipants(t) {
  participantTrek.value = t
  const res = await api.get(`/staff/treks/${t.id}/participants`)
  participants.value = res.data
}

async function removeParticipant(p) {
  if (!confirm(`Remove ${p.name} from this trek?`)) return
  await run(api.put(`/staff/bookings/${p.booking_id}/cancel`))
  showParticipants(participantTrek.value)
}
</script>

<template>
  <div>
    <div class="row g-3 mb-4">
      <div class="col-4"><div class="stat-card"><div class="label">Assigned treks</div><div class="value">{{ treks.length }}</div></div></div>
      <div class="col-4"><div class="stat-card"><div class="label">Registered</div><div class="value">{{ totalRegistered }}</div></div></div>
      <div class="col-4"><div class="stat-card"><div class="label">Open now</div><div class="value">{{ openCount }}</div></div></div>
    </div>

    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

    <div v-if="!treks.length" class="card-box empty">No treks are assigned to you yet.</div>

    <div class="row g-3">
      <div v-for="t in treks" :key="t.id" class="col-md-6 col-xl-4">
        <div class="trek-card">
          <div class="trek-banner" :class="t.difficulty">
            <span class="badge-soft" :class="'st-' + t.status">{{ t.status }}</span>
          </div>
          <div class="trek-body">
            <h5>{{ t.trek_name }}</h5>
            <div class="trek-meta mb-2">{{ t.location }} · {{ t.start_date }} → {{ t.end_date }}</div>
            <div class="d-flex justify-content-between small mb-3">
              <span><b>{{ t.registered_count }}</b> registered</span>
              <span><b>{{ t.available_slots }}</b> / {{ t.total_slots }} slots left</span>
            </div>

            <div class="input-group input-group-sm mb-3">
              <span class="input-group-text">Available slots</span>
              <input v-model="slotInputs[t.id]" type="number" min="0" class="form-control"
                     :disabled="t.status === 'Completed' || t.status === 'Ongoing'" />
              <button class="btn btn-outline-primary" @click="saveSlots(t)"
                      :disabled="t.status === 'Completed' || t.status === 'Ongoing'">Update</button>
            </div>

            <div class="mt-auto d-flex flex-wrap gap-2">
              <button class="btn btn-sm btn-outline-secondary" @click="showParticipants(t)">Participants</button>
              <button v-if="t.status === 'Approved' || t.status === 'Closed'" class="btn btn-sm btn-success" @click="setStatus(t, 'Open')">Open booking</button>
              <button v-if="t.status === 'Approved' || t.status === 'Open'" class="btn btn-sm btn-outline-danger" @click="setStatus(t, 'Closed')">Close booking</button>
              <button v-if="t.status === 'Open' || t.status === 'Closed'" class="btn btn-sm btn-primary" @click="setStatus(t, 'Ongoing')">Start trek</button>
              <button v-if="t.status === 'Ongoing'" class="btn btn-sm btn-dark" @click="setStatus(t, 'Completed')">Mark completed</button>
            </div>
            <div v-if="t.status === 'Pending'" class="small text-muted mt-2">Waiting for admin approval.</div>
          </div>
        </div>
      </div>
    </div>

    <Modal v-if="participantTrek" :title="'Participants - ' + participantTrek.trek_name" wide @close="participantTrek = null">
      <div class="table-responsive">
        <table class="table">
          <thead><tr><th>Name</th><th>Contact</th><th>Booked on</th><th>Status</th><th>Payment</th><th></th></tr></thead>
          <tbody>
            <tr v-for="p in participants" :key="p.booking_id">
              <td class="fw-semibold">{{ p.name }}</td>
              <td class="small">{{ p.email }}<br />{{ p.phone }}</td>
              <td class="small">{{ p.booking_date }}</td>
              <td><span class="badge-soft" :class="'st-' + p.status">{{ p.status }}</span></td>
              <td><span class="badge-soft" :class="'st-' + p.payment_status">{{ p.payment_status }}</span></td>
              <td>
                <button v-if="p.status === 'Booked' && participantTrek.status !== 'Ongoing'" class="btn btn-sm btn-outline-danger"
                        @click="removeParticipant(p)">Remove</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!participants.length" class="empty">Nobody has registered yet.</div>
    </Modal>
  </div>
</template>