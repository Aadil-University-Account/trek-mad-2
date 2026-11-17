<script setup>
import { ref, onMounted } from 'vue'
import api, { errorMessage } from '../api'
import { auth } from '../auth'

const form = ref({ name: '', email: '', phone: '', password: '' })
const message = ref('')
const error = ref('')

onMounted(async () => {
  const res = await api.get('/profile')
  form.value = { ...res.data, password: '' }
})

async function save() {
  message.value = ''
  error.value = ''
  try {
    const res = await api.put('/profile', form.value)
    message.value = res.data.message
    auth.name = res.data.name
    localStorage.setItem('name', res.data.name)
    form.value.password = ''
  } catch (err) {
    error.value = errorMessage(err)
  }
}
</script>

<template>
  <div class="card-box" style="max-width: 520px">
    <h5 class="fw-bold mb-3">My profile</h5>
    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>
    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
    <form @submit.prevent="save">
      <div class="mb-3"><label class="form-label">Name</label>
        <input v-model="form.name" class="form-control" required /></div>
      <div class="mb-3"><label class="form-label">Email</label>
        <input v-model="form.email" class="form-control" disabled /></div>
      <div class="mb-3"><label class="form-label">Phone (10 digits)</label>
        <input v-model="form.phone" class="form-control" pattern="[0-9]{10}" title="10 digits" /></div>
      <div class="mb-4"><label class="form-label">New password (leave empty to keep)</label>
        <input v-model="form.password" type="password" minlength="6" class="form-control" /></div>
      <button class="btn btn-primary">Save profile</button>
    </form>
  </div>
</template>