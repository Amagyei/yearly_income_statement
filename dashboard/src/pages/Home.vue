<template>
  <div class="min-h-screen bg-background flex items-center justify-center">
    <div class="text-center">
      <h1 class="text-2xl font-bold mb-4">Welcome to Yearly Income Statement Dashboard</h1>
      <p class="text-muted-foreground mb-6">Redirecting to dashboard...</p>
      <Button @click="goToDashboard" class="w-full max-w-xs">
        Go to Dashboard
      </Button>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui'
import { session } from '@/data/session'

const router = useRouter()

const goToDashboard = () => {
  router.push('/dashboard')
}

onMounted(() => {
  // Check if user is authenticated before redirecting
  if (session.isAuthenticated()) {
    // Auto-redirect to dashboard after a short delay
    setTimeout(() => {
      goToDashboard()
    }, 1000)
  } else {
    // Redirect to login if not authenticated
    router.push('/login')
  }
})
</script>
