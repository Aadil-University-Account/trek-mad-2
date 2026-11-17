<script setup>
import { useRouter } from 'vue-router'
import { auth, logout } from '../auth'

const router = useRouter()

function doLogout() {
  logout()
  router.push('/login')
}
</script>

<template>
  <nav class="topbar">
    <div class="container d-flex align-items-center justify-content-between">
      <router-link to="/" class="brand">
        <span class="brand-icon">&#9650;</span> TrekMate
      </router-link>

      <div class="d-flex align-items-center gap-2">
        <template v-if="auth.token">
          <span class="d-none d-sm-inline text-muted small me-2">
            {{ auth.name }} <span class="role-pill">{{ auth.role }}</span>
          </span>
          <button class="btn btn-sm btn-outline-secondary" @click="doLogout">Logout</button>
        </template>
        <template v-else>
          <router-link to="/login" class="btn btn-sm btn-outline-primary">Login</router-link>
          <router-link to="/register" class="btn btn-sm btn-primary">Sign up</router-link>
        </template>
      </div>
    </div>
  </nav>
</template>