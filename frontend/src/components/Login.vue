<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api, { errorMessage } from '../api'
import { saveLogin } from '../auth'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function login() {
  error.value = ''
  loading.value = true
  try {
    const res = await api.post('/login', { email: email.value, password: password.value })
    saveLogin(res.data)
    router.push('/' + res.data.role) // role based dashboard
  } catch (err) {
    error.value = errorMessage(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-card card-box">
    <h3 class="mb-1">Welcome back</h3>
    <p class="text-muted mb-4">Login to continue your adventure.</p>

    <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

    <form @submit.prevent="login">
      <div class="mb-3">
        <label class="form-label">Email</label>
        <input v-model="email" type="email" class="form-control" placeholder="you@example.com" required />
      </div>
      <div class="mb-4">
        <label class="form-label">Password</label>
        <input v-model="password" type="password" class="form-control" placeholder="Password" required />
      </div>
      <button class="btn btn-primary w-100" :disabled="loading">
        {{ loading ? 'Logging in...' : 'Login' }}
      </button>
    </form>

    <p class="text-center mt-3 mb-0 small">
      New trekker? <router-link to="/register">Create an account</router-link>
    </p>
  </div>
</template>