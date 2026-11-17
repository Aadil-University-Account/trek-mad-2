<script setup>
import { ref } from 'vue'

const treks = ref([
  { id: 1, name: 'Himalayan Escape', location: 'Manali', difficulty: 'Moderate', price: '₹4,500' },
  { id: 2, name: 'Lakeside Trail', location: 'Nainital', difficulty: 'Easy', price: '₹3,200' },
  { id: 3, name: 'Snowline Adventure', location: 'Gulmarg', difficulty: 'Hard', price: '₹6,800' },
])
</script>

<template>
  <div class="row g-3">
    <div v-for="trek in treks" :key="trek.id" class="col-md-6 col-xl-4">
      <div class="trek-card">
        <div class="trek-banner" :class="trek.difficulty.toLowerCase()">
          <span class="badge-soft">{{ trek.difficulty }}</span>
        </div>
        <div class="trek-body">
          <h5>{{ trek.name }}</h5>
          <div class="trek-meta mb-2">{{ trek.location }}</div>
          <div class="d-flex justify-content-between align-items-center">
            <span class="fw-semibold">{{ trek.price }}</span>
            <button class="btn btn-sm btn-primary">Book now</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
