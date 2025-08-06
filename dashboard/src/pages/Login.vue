<template>
  <div class="min-h-screen bg-background flex items-center justify-center">
    <div class="w-full max-w-md">
      <Card class="p-6">
        <CardHeader class="text-center">
          <CardTitle class="text-2xl font-bold">Login to Dashboard</CardTitle>
          <p class="text-muted-foreground mt-2">Enter your credentials to access the Yearly Income Statement Dashboard</p>
        </CardHeader>
        <CardContent>
          <form @submit.prevent="handleLogin" class="space-y-4">
            <div class="space-y-2">
              <Label for="email">Username/Email</Label>
              <Input
                id="email"
                v-model="form.email"
                type="text"
                placeholder="admin@example.com"
                required
                :disabled="loading"
              />
            </div>
            <div class="space-y-2">
              <Label for="password">Password</Label>
              <Input
                id="password"
                v-model="form.password"
                type="password"
                placeholder="••••••••"
                required
                :disabled="loading"
              />
            </div>
            
            <div v-if="error" class="bg-destructive/10 border border-destructive/20 rounded-lg p-3">
              <p class="text-sm text-destructive">{{ error }}</p>
            </div>
            
            <Button 
              type="submit" 
              class="w-full" 
              :disabled="loading"
              @click="handleLogin"
            >
              <RefreshCw v-if="loading" class="h-4 w-4 animate-spin mr-2" />
              {{ loading ? 'Logging in...' : 'Login' }}
            </Button>
            
            <!-- Test button -->
            <button 
              type="button"
              @click="testLogin"
              class="w-full bg-blue-500 text-white p-2 rounded mt-2"
            >
              Test Login
            </button>
          </form>
        </CardContent>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui'
import { Button } from '@/components/ui'
import { Input } from '@/components/ui'
import { Label } from '@/components/ui'
import { RefreshCw } from 'lucide-vue-next'
import { session } from '../data/session'

const router = useRouter()
const loading = ref(false)
const error = ref('')

const form = reactive({
  email: '',
  password: ''
})

const handleLogin = async () => {
  console.log('Login attempt started')
  console.log('Form data:', form)
  loading.value = true
  error.value = ''
  
  try {
    console.log('Calling session.login with:', form.email, form.password)
    const result = await session.login(form.email, form.password)
    console.log('Login result:', result)
    
    if (result.success) {
      console.log('Login successful, redirecting to dashboard')
      // Login successful
      router.push('/dashboard')
    } else {
      console.log('Login failed:', result.error)
      error.value = result.error
    }
  } catch (err) {
    console.error('Login error:', err)
    error.value = 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}

// Test function
const testLogin = () => {
  console.log('Test login clicked')
  handleLogin()
}
</script>
