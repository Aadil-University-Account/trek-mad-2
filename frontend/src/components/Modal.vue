<script setup>
defineProps({ title: String, wide: Boolean })
defineEmits(['close'])
</script>

<template>
  <div class="modal-bg" @click.self="$emit('close')">
    <div class="modal-box" :class="{ wide }">
      <div class="d-flex justify-content-between align-items-start mb-3">
        <h4 class="mb-0 fw-bold">{{ title }}</h4>
        <button class="btn-close" @click="$emit('close')"></button>
      </div>
      <slot />
    </div>
  </div>
</template>