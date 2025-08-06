<template>
  <div class="relative">
    <button
      type="button"
      :class="triggerClasses"
      @click="isOpen = !isOpen"
      @blur="handleBlur"
    >
      <span v-if="modelValue" class="block truncate">{{ getSelectedLabel() }}</span>
      <span v-else class="block truncate text-muted-foreground">{{ placeholder }}</span>
      <svg class="ml-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
    
    <div v-if="isOpen" class="absolute z-50 mt-1 w-full rounded-md border bg-popover text-popover-foreground shadow-md">
      <div class="max-h-60 overflow-auto">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Select an option'
  }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)

const triggerClasses = computed(() => {
  return 'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50'
})

const getSelectedLabel = () => {
  // This would need to be implemented based on the options
  return props.modelValue
}

const handleBlur = () => {
  setTimeout(() => {
    isOpen.value = false
  }, 150)
}
</script> 