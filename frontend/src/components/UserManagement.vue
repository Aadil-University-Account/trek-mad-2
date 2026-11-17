<script setup>
import { ref, onMounted } from 'vue'
import api from '../api'

const users = ref([])
const search = ref('')
const message = ref('')

async function load() {
  const res = await api.get('/admin/users', { params: { q: search.value } })
  users.value = res.data
}
onMounted(load)

async function setStatus(u, changes) {
  const res = await api.put(`/admin/accounts/${u.id}/status`, changes)
  message.value = res.data.message
  load()
}
</script>

<template>
  <div>
    <input v-model="search" @input="load" class="form-control mb-3" style="max-width: 320px"
           placeholder="Search users by name, email or ID" />
    <div v-if="message" class="alert alert-success py-2">{{ message }}</div>

    <div class="card-box table-card">
      <div class="table-responsive">
        <table class="table">
          <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Joined</th><th>Status</th><th></th></tr></thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>{{ u.id }}</td>
              <td class="fw-semibold">{{ u.name }}</td>
              <td>{{ u.email }}</td>
              <td>{{ u.phone || '—' }}</td>
              <td>{{ u.created_at }}</td>
              <td>
                <span v-if="u.is_blacklisted" class="badge-soft st-Blacklisted">Blacklisted</span>
                <span v-else-if="!u.is_active" class="badge-soft st-Inactive">Inactive</span>
                <span v-else class="badge-soft st-Active">Active</span>
              </td>
              <td class="text-end text-nowrap">
                <button class="btn btn-sm btn-outline-secondary me-1"
                        @click="setStatus(u, { is_active: !u.is_active })">{{ u.is_active ? 'Deactivate' : 'Activate' }}</button>
                <button class="btn btn-sm btn-outline-danger"
                        @click="setStatus(u, { is_blacklisted: !u.is_blacklisted })">{{ u.is_blacklisted ? 'Unblacklist' : 'Blacklist' }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!users.length" class="empty">No users found.</div>
    </div>
  </div>
</template>
