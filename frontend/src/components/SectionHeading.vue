<template>
  <div class="section-heading">
    <h2 class="gradient-text">{{ title }}</h2>
    <p v-if="subtitle">{{ subtitle }}</p>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  subtitle: { type: String, default: '' }
})
</script>
