<template>
  <label :class="labelClasses" :for="for">
    <slot />
  </label>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  for: {
    type: String,
    default: ''
  }
})

const labelClasses = computed(() => {
  return 'text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70'
})
</script> 