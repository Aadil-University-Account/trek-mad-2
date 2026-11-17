<script setup>
import { ref, onMounted } from 'vue'
import api, { errorMessage } from '../api'
import Modal from './Modal.vue'

const staff = ref([])
const search = ref('')
const message = ref('')
const error = ref('')
const showForm = ref(false)
const editingId = ref(null)
const form = ref({})

async function load() {
  const res = await api.get('/admin/staff', { params: { q: search.value } })
  staff.value = res.data
}
onMounted(load)

function openCreate() {
  editingId.value = null
  form.value = { name: '', email: '', phone: '', password: '', experience_years: 0, specialization: '' }
  error.value = ''
  showForm.value = true
}

function openEdit(s) {
  editingId.value = s.id
  form.value = { ...s, password: '' }
  error.value = ''
  showForm.value = true
}

async function save() {
  error.value = ''
  try {
    const res = editingId.value
      ? await api.put('/admin/staff/' + editingId.value, form.value)
      : await api.post('/admin/staff', form.value)
    message.value = res.data.message
    showForm.value = false
    load()
  } catch (err) {
    error.value = errorMessage(err)
  }
}

async function setStatus(s, changes) {
  const res = await api.put(`/admin/accounts/${s.user_id}/status`, changes)
  message.value = res.data.message
  load()
}
</script>

<template>
  <div>
    <div class="d-flex flex-wrap gap-2 justify-content-between mb-3">
      <input v-model="search" @input="load" class="form-control" style="max-width: 320px"
             placeholder="Search staff by name, email or ID" />
      <button class="btn btn-primary" @click="openCreate">+ Add staff</button>
    </div>

    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>

    <div class="card-box table-card">
      <div class="table-responsive">
        <table class="table">
          <thead><tr><th>ID</th><th>Name</th><th>Contact</th><th>Experience</th><th>Assigned treks</th><th>Status</th><th></th></tr></thead>
          <tbody>
            <tr v-for="s in staff" :key="s.id">
              <td>{{ s.id }}</td>
              <td><div class="fw-semibold">{{ s.name }}</div><div class="trek-meta">{{ s.specialization || 'General' }}</div></td>
              <td class="small">{{ s.email }}<br />{{ s.phone }}</td>
              <td>{{ s.experience_years }} yrs</td>
              <td class="small">{{ s.assigned_treks.join(', ') || '—' }}</td>
              <td>
                <span v-if="s.is_blacklisted" class="badge-soft st-Blacklisted">Blacklisted</span>
                <span v-else class="badge-soft" :class="'st-' + s.status">{{ s.status }}</span>
              </td>
              <td class="text-end text-nowrap">
                <button class="btn btn-sm btn-outline-primary me-1" @click="openEdit(s)">Edit</button>
                <button class="btn btn-sm btn-outline-secondary me-1"
                        @click="setStatus(s, { is_active: !s.is_active })">{{ s.is_active ? 'Deactivate' : 'Activate' }}</button>
                <button class="btn btn-sm btn-outline-danger"
                        @click="setStatus(s, { is_blacklisted: !s.is_blacklisted })">{{ s.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!staff.length" class="empty">No staff found.</div>
    </div>

    <Modal v-if="showForm" :title="editingId ? 'Edit staff' : 'Add trek staff'" @close="showForm = false">
      <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
      <form @submit.prevent="save">
        <div class="row g-3">
          <div class="col-12"><label class="form-label">Name</label>
            <input v-model="form.name" class="form-control" required /></div>
          <div class="col-12"><label class="form-label">Email (login id)</label>
            <input v-model="form.email" type="email" class="form-control" required :disabled="!!editingId" /></div>
          <div class="col-md-6"><label class="form-label">Phone</label>
            <input v-model="form.phone" class="form-control" pattern="[0-9]{10}" title="10 digits" /></div>
          <div class="col-md-6"><label class="form-label">Experience (years)</label>
            <input v-model="form.experience_years" type="number" min="0" class="form-control" /></div>
          <div class="col-12"><label class="form-label">Specialization</label>
            <input v-model="form.specialization" class="form-control" placeholder="e.g. Himalayan treks" /></div>
          <div class="col-12"><label class="form-label">{{ editingId ? 'New password (optional)' : 'Password' }}</label>
            <input v-model="form.password" type="password" minlength="6" class="form-control" :required="!editingId" /></div>
        </div>
        <button class="btn btn-primary w-100 mt-4">{{ editingId ? 'Save changes' : 'Create staff' }}</button>
      </form>
    </Modal>
  </div>
</template>