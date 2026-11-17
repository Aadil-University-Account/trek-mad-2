<script setup>
import { ref } from 'vue'
import AdminSummary from '../components/AdminSummary.vue'
import TrekManagement from '../components/TrekManagement.vue'
import StaffManagement from '../components/StaffManagement.vue'
import UserManagement from '../components/UserManagement.vue'
import AdminBookings from '../components/AdminBookings.vue'
import AdminReports from '../components/AdminReports.vue'

const tab = ref('summary')
const tabs = [
  { id: 'summary', label: 'Overview' },
  { id: 'treks', label: 'Treks' },
  { id: 'staff', label: 'Staff' },
  { id: 'users', label: 'Users' },
  { id: 'bookings', label: 'Bookings' },
  { id: 'reports', label: 'Reports' },
]
</script>

<template>
  <div class="container page">
    <h2 class="page-title">Admin Dashboard</h2>
    <p class="page-sub">Manage treks, staff, trekkers and bookings.</p>

    <div class="tabs">
      <button v-for="t in tabs" :key="t.id" class="tab-btn" :class="{ active: tab === t.id }" @click="tab = t.id">
        {{ t.label }}
      </button>
    </div>

    <AdminSummary v-if="tab === 'summary'" />
    <TrekManagement v-else-if="tab === 'treks'" />
    <StaffManagement v-else-if="tab === 'staff'" />
    <UserManagement v-else-if="tab === 'users'" />
    <AdminBookings v-else-if="tab === 'bookings'" />
    <AdminReports v-else-if="tab === 'reports'" />
  </div>
</template>