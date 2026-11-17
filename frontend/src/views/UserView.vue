<script setup>
import { auth } from '../auth'
</script>

<template>
  <div class="container page">
    <h2 class="page-title">User Dashboard</h2>
    <div class="card-box">Welcome, {{ auth.name }}! (Features are added in the next milestones.)</div>
  </div>
</template>