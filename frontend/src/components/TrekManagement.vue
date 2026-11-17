<script setup>
import { ref, onMounted } from 'vue'
import api, { errorMessage } from '../api'
import Modal from './Modal.vue'

const treks = ref([])
const staff = ref([])
const search = ref('')
const message = ref('')
const error = ref('')

const showForm = ref(false)
const editingId = ref(null)
const emptyForm = {
  trek_name: '', location: '', difficulty: 'Easy', duration_days: 3, total_slots: 10,
  price: 0, start_date: '', description: '', assigned_staff_id: '',
}
const form = ref({ ...emptyForm })

const assignTrek = ref(null)
const assignStaffId = ref('')

async function load() {
  const res = await api.get('/admin/treks', { params: { q: search.value } })
  treks.value = res.data
}

onMounted(async () => {
  load()
  const res = await api.get('/admin/staff')
  staff.value = res.data.filter((s) => s.is_active && !s.is_blacklisted)
})

function openCreate() {
  editingId.value = null
  form.value = { ...emptyForm }
  error.value = ''
  showForm.value = true
}

function openEdit(t) {
  editingId.value = t.id
  form.value = { ...t }
  error.value = ''
  showForm.value = true
}

async function save() {
  error.value = ''
  try {
    const res = editingId.value
      ? await api.put('/admin/treks/' + editingId.value, form.value)
      : await api.post('/admin/treks', form.value)
    message.value = res.data.message
    showForm.value = false
    load()
  } catch (err) {
    error.value = errorMessage(err)
  }
}

async function action(promise) {
  message.value = ''
  error.value = ''
  try {
    const res = await promise
    message.value = res.data.message
    load()
  } catch (err) {
    error.value = errorMessage(err)
  }
}

const approve = (t) => action(api.post(`/admin/treks/${t.id}/approve`))

function remove(t) {
  if (confirm(`Remove trek "${t.trek_name}"?`)) action(api.delete('/admin/treks/' + t.id))
}

function openAssign(t) {
  assignTrek.value = t
  assignStaffId.value = t.assigned_staff_id || ''
}

async function assign() {
  await action(api.post(`/admin/treks/${assignTrek.value.id}/assign`, { staff_id: assignStaffId.value }))
  assignTrek.value = null
}
</script>

<template>
  <div>
    <div class="d-flex flex-wrap gap-2 justify-content-between mb-3">
      <input v-model="search" @input="load" class="form-control" style="max-width: 320px"
             placeholder="Search by trek name, location or ID" />
      <button class="btn btn-primary" @click="openCreate">+ New trek</button>
    </div>

    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
    <div v-if="error && !showForm" class="alert alert-danger py-2">{{ error }}</div>

    <div class="card-box table-card">
      <div class="table-responsive">
        <table class="table">
          <thead>
            <tr><th>ID</th><th>Trek</th><th>Difficulty</th><th>Dates</th><th>Slots</th><th>Staff</th><th>Status</th><th></th></tr>
          </thead>
          <tbody>
            <tr v-for="t in treks" :key="t.id">
              <td>{{ t.id }}</td>
              <td><div class="fw-semibold">{{ t.trek_name }}</div><div class="trek-meta">{{ t.location }}</div></td>
              <td><span class="badge-soft" :class="'d-' + t.difficulty">{{ t.difficulty }}</span></td>
              <td class="small">{{ t.start_date }}<br />{{ t.duration_days }} day(s)</td>
              <td>{{ t.available_slots }} / {{ t.total_slots }}</td>
              <td>{{ t.staff_name || '—' }}</td>
              <td><span class="badge-soft" :class="'st-' + t.status">{{ t.status }}</span></td>
              <td class="text-end text-nowrap">
                <button v-if="t.status === 'Pending'" class="btn btn-sm btn-success me-1" @click="approve(t)">Approve</button>
                <button class="btn btn-sm btn-outline-secondary me-1" @click="openAssign(t)">Assign</button>
                <button class="btn btn-sm btn-outline-primary me-1" @click="openEdit(t)">Edit</button>
                <button class="btn btn-sm btn-outline-danger" @click="remove(t)">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!treks.length" class="empty">No treks found.</div>
    </div>

    <!-- create / edit -->
    <Modal v-if="showForm" :title="editingId ? 'Edit trek' : 'New trek'" @close="showForm = false">
      <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
      <form @submit.prevent="save">
        <div class="row g-3">
          <div class="col-md-6"><label class="form-label">Trek name</label>
            <input v-model="form.trek_name" class="form-control" required /></div>
          <div class="col-md-6"><label class="form-label">Location</label>
            <input v-model="form.location" class="form-control" required /></div>
          <div class="col-md-4"><label class="form-label">Difficulty</label>
            <select v-model="form.difficulty" class="form-select">
              <option>Easy</option><option>Moderate</option><option>Hard</option>
            </select></div>
          <div class="col-md-4"><label class="form-label">Duration (days)</label>
            <input v-model="form.duration_days" type="number" min="1" class="form-control" required /></div>
          <div class="col-md-4"><label class="form-label">Total slots</label>
            <input v-model="form.total_slots" type="number" min="1" class="form-control" required /></div>
          <div class="col-md-6"><label class="form-label">Start date</label>
            <input v-model="form.start_date" type="date" class="form-control" required /></div>
          <div class="col-md-6"><label class="form-label">Price (₹)</label>
            <input v-model="form.price" type="number" min="0" class="form-control" required /></div>
          <div v-if="!editingId" class="col-12"><label class="form-label">Assign staff (optional)</label>
            <select v-model="form.assigned_staff_id" class="form-select">
              <option value="">-- none --</option>
              <option v-for="s in staff" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select></div>
          <div class="col-12"><label class="form-label">Description</label>
            <textarea v-model="form.description" class="form-control" rows="2" maxlength="500"></textarea></div>
        </div>
        <button class="btn btn-primary w-100 mt-4">{{ editingId ? 'Save changes' : 'Create trek' }}</button>
      </form>
    </Modal>

    <!-- assign staff -->
    <Modal v-if="assignTrek" title="Assign staff" @close="assignTrek = null">
      <p class="text-muted">Trek: <b>{{ assignTrek.trek_name }}</b></p>
      <select v-model="assignStaffId" class="form-select mb-3">
        <option value="" disabled>Select staff</option>
        <option v-for="s in staff" :key="s.id" :value="s.id">{{ s.name }} ({{ s.specialization || 'General' }})</option>
      </select>
      <button class="btn btn-primary w-100" :disabled="!assignStaffId" @click="assign">Assign</button>
    </Modal>
  </div>
</template>