<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { errorMessage } from '../api'

const router = useRouter()
const form = ref({ name: '', email: '', phone: '', password: '' })
const error = ref('')
const loading = ref(false)

async function register() {
  error.value = ''
  loading.value = true
  try {
    await api.post('/register', form.value)
    alert('Registered successfully! Please login.')
    router.push('/login')
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-card card-box">
    <h3 class="mb-1">Join TrekMate</h3>
    <p class="text-muted mb-4">Register as a trekker and book your first trek.</p>

    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

    <form @submit.prevent="register">
      <div class="mb-3">
        <label class="form-label">Full name</label>
        <input v-model="form.name" class="form-control" required minlength="2" />
      </div>
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model="form.email" type="email" class="form-control" required />
      </div>
      <div class="mb-3">
        <label class="form-label">Phone (10 digits)</label>
        <input v-model="form.phone" class="form-control" pattern="[0-9]{10}" title="Enter 10 digits" />
      </div>
      <div class="mb-4">
        <label class="form-label">Password (min 6 characters)</label>
        <input v-model="form.password" type="password" class="form-control" required minlength="6" />
      </div>
      <button class="btn btn-primary w-100" :disabled="loading">
        {{ loading ? 'Please wait...' : 'Register' }}
      </button>
    </form>

    <p class="text-center mt-3 mb-0 small">
      Already have an account? <router-link to="/login">Login</router-link>
    </p>
  </div>
</template>