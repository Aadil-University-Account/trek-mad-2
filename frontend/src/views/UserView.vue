<script setup>
import { ref } from 'vue'
import UserDashboard from '../components/UserDashboard.vue'
import BookingHistory from '../components/BookingHistory.vue'
import UserProfile from '../components/UserProfile.vue'

const tab = ref('explore')
</script>

<template>
  <div class="container page">
    <h2 class="page-title">Find your next trek</h2>
    <p class="page-sub">Browse open treks and book your slot.</p>

    <div class="tabs">
      <button class="tab-btn" :class="{ active: tab === 'explore' }" @click="tab = 'explore'">Explore treks</button>
      <button class="tab-btn" :class="{ active: tab === 'bookings' }" @click="tab = 'bookings'">My bookings</button>
      <button class="tab-btn" :class="{ active: tab === 'profile' }" @click="tab = 'profile'">Profile</button>
    </div>

    <UserDashboard v-if="tab === 'explore'" />
    <BookingHistory v-else-if="tab === 'bookings'" />
    <UserProfile v-else-if="tab === 'profile'" />
  </div>
</template>