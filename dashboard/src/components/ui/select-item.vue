<template>
  <div
    :class="itemClasses"
    @click="$emit('click', value)"
  >
    <slot />
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: {
    type: [String, Number],
    required: true
  },
  selected: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])

const itemClasses = computed(() => {
  const baseClasses = 'relative flex w-full cursor-default select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none'
  const stateClasses = props.selected 
    ? 'bg-accent text-accent-foreground' 
    : 'hover:bg-accent hover:text-accent-foreground'
  
  return `${baseClasses} ${stateClasses}`
})
</script> 