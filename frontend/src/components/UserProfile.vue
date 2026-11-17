<script setup>
import { auth } from '../auth'
</script>

<template>
  <div class="card-box">
    <h5 class="mb-3">Profile</h5>
    <div class="row g-3">
      <div class="col-md-6">
        <label class="form-label text-muted">Name</label>
        <div class="fw-semibold">{{ auth.name || 'Trekker' }}</div>
      </div>
      <div class="col-md-6">
        <label class="form-label text-muted">Role</label>
        <div class="fw-semibold text-capitalize">{{ auth.role || 'user' }}</div>
      </div>
    </div>
  </div>
</template>
