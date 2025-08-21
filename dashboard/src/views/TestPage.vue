<template>
  <div class="min-h-screen bg-background">
    <div class="container mx-auto p-6 space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-dashboard-header">Test API Dashboard</h1>
          <p class="text-muted-foreground mt-2">Test and validate the ERPNext P&L mirror functionality</p>
        </div>
        <div class="flex items-center gap-4">
          <Button 
            variant="outline" 
            @click="runAllTests"
            :disabled="loading"
            class="flex items-center gap-2"
          >
            <RefreshCw :class="['h-4 w-4', { 'animate-spin': loading }]" />
            {{ loading ? 'Running Tests...' : 'Run All Tests' }}
          </Button>
          <Button 
            @click="exportTestResults"
            :disabled="!testResults || Object.keys(testResults).length === 0"
            class="flex items-center gap-2"
          >
            <Download class="h-4 w-4" />
            Export Results
          </Button>
          <Button 
            variant="outline" 
            @click="goBack"
            class="flex items-center gap-2"
          >
            <ArrowLeft class="h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
      </div>

      <!-- Test Controls -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle class="text-sm">Test Filters</CardTitle>
          </CardHeader>
          <CardContent class="space-y-3">
            <div>
              <Label>Company</Label>
              <Input v-model="testFilters.company" placeholder="Company name" />
            </div>
            <div>
              <Label>Fiscal Year</Label>
              <Input v-model="testFilters.fiscal_year" placeholder="2025" />
            </div>
            <div>
              <Label>Periodicity</Label>
              <select v-model="testFilters.periodicity" class="w-full p-2 border rounded">
                <option value="Yearly">Yearly</option>
                <option value="Half-Yearly">Half-Yearly</option>
                <option value="Quarterly">Quarterly</option>
                <option value="Monthly">Monthly</option>
              </select>
            </div>
            <div>
              <Label>Accumulated Values</Label>
              <input type="checkbox" v-model="testFilters.accumulated_values" class="ml-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle class="text-sm">Individual Tests</CardTitle>
          </CardHeader>
          <CardContent class="space-y-2">
            <Button 
              @click="testConnection" 
              variant="outline" 
              size="sm" 
              class="w-full"
            >
              Test Connection
            </Button>
            <Button 
              @click="testPeriodList" 
              variant="outline" 
              size="sm" 
              class="w-full"
            >
              Test Period List
            </Button>
            <Button 
              @click="testIncomeData" 
              variant="outline" 
              size="sm" 
              class="w-full"
            >
              Test Income Data
            </Button>
            <Button 
              @click="testExpenseData" 
              variant="outline" 
              size="sm" 
              class="w-full"
            >
              Test Expense Data
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle class="text-sm">Advanced Tests</CardTitle>
          </CardHeader>
          <CardContent class="space-y-2">
            <Button 
              @click="testColumns" 
              variant="outline" 
              size="sm" 
              class="w-full"
            >
              Test Columns
            </Button>
            <Button 
              @click="testCompletePnl" 
              variant="outline" 
              size="sm" 
              class="w-full"
            >
              Test Complete P&L
            </Button>
            <Button 
              @click="testGrowthView" 
              variant="outline" 
              size="sm" 
              class="w-full"
            >
              Test Growth View
            </Button>
            <Button 
              @click="testMarginView" 
              variant="outline" 
              size="sm" 
              class="w-full"
            >
              Test Margin View
            </Button>
            <Button 
              @click="testGLEntries" 
              variant="outline" 
              size="sm" 
              class="w-full"
            >
              Test GL Entries
            </Button>
            <Button 
              @click="testDashboardDataStructure" 
              variant="outline" 
              size="sm" 
              class="w-full"
            >
              Test Dashboard Data Structure
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle class="text-sm">Performance & Comparison</CardTitle>
          </CardHeader>
          <CardContent class="space-y-2">
            <Button 
              @click="testPerformance" 
              variant="outline" 
              size="sm" 
              class="w-full"
            >
              Performance Test
            </Button>
            <Button 
              @click="compareWithErpnext" 
              variant="outline" 
              size="sm" 
              class="w-full"
            >
              Compare with ERPNext
            </Button>
            <Button 
              @click="getTestSummary" 
              variant="outline" 
              size="sm" 
              class="w-full"
            >
              Get Test Summary
            </Button>
          </CardContent>
        </Card>
      </div>

      <!-- Test Results -->
      <div v-if="testResults && Object.keys(testResults).length > 0">
        <Card>
          <CardHeader>
            <CardTitle>Test Results</CardTitle>
            <p class="text-sm text-muted-foreground">
              Results from the latest test execution
            </p>
          </CardHeader>
          <CardContent>
            <div class="space-y-4">
              <!-- Summary -->
              <div v-if="testResults.summary" class="bg-muted/50 p-4 rounded-lg">
                <h3 class="font-semibold mb-2">Test Summary</h3>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span class="font-medium">Total Tests:</span>
                    <span class="ml-2">{{ testResults.summary.total_tests || 0 }}</span>
                  </div>
                  <div>
                    <span class="font-medium">Successful:</span>
                    <span class="ml-2 text-green-600">{{ testResults.summary.successful_tests || 0 }}</span>
                  </div>
                  <div>
                    <span class="font-medium">Failed:</span>
                    <span class="ml-2 text-red-600">{{ testResults.summary.failed_tests || 0 }}</span>
                  </div>
                  <div>
                    <span class="font-medium">Success Rate:</span>
                    <span class="ml-2">
                      {{ testResults.summary.total_tests > 0 
                        ? Math.round((testResults.summary.successful_tests / testResults.summary.total_tests) * 100) 
                        : 0 }}%
                    </span>
                  </div>
                </div>
              </div>

              <!-- Individual Test Results -->
              <div class="space-y-3">
                <div v-for="(result, testName) in testResults.results || testResults" :key="testName" class="border rounded-lg p-3">
                  <div class="flex items-center justify-between mb-2">
                    <h4 class="font-medium capitalize">{{ testName.replace(/([A-Z])/g, ' $1').trim() }}</h4>
                    <div class="flex items-center gap-2">
                      <span 
                        :class="[
                          'px-2 py-1 rounded-full text-xs font-medium',
                          result?.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        ]"
                      >
                        {{ result?.success ? 'PASSED' : 'FAILED' }}
                      </span>
                    </div>
                  </div>
                  
                  <div v-if="result?.success" class="text-sm text-muted-foreground">
                    <pre class="whitespace-pre-wrap text-xs bg-muted p-2 rounded">{{ JSON.stringify(result, null, 2) }}</pre>
                  </div>
                  
                  <div v-else-if="result?.error" class="text-sm text-red-600">
                    <strong>Error:</strong> {{ result.error }}
                    <pre v-if="result.traceback" class="whitespace-pre-wrap text-xs bg-red-50 p-2 rounded mt-2">{{ result.traceback }}</pre>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="flex items-center gap-3">
          <RefreshCw class="h-6 w-6 animate-spin text-primary" />
          <span class="text-lg text-muted-foreground">Running tests...</span>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
        <div class="flex items-center gap-3">
          <AlertCircle class="h-5 w-5 text-destructive" />
          <div>
            <h3 class="font-semibold text-destructive">Test Execution Error</h3>
            <p class="text-sm text-muted-foreground mt-1">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Debug Info -->
      <div v-if="showDebug" class="mt-8 p-4 bg-muted/50 rounded-lg">
        <h4 class="font-semibold mb-2">Debug Information</h4>
        <pre class="text-xs overflow-auto">{{ debugInfo }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui'
import { Input } from '@/components/ui'
import { Label } from '@/components/ui'
import { 
  RefreshCw, 
  Download, 
  AlertCircle, 
  ArrowLeft 
} from 'lucide-vue-next'
// import testApiService from '../services/testApi'

// State
const loading = ref(false)
const error = ref(null)
const testResults = ref({})
const showDebug = ref(false)
const router = useRouter()

// Test filters
const testFilters = reactive({
  company: 'Western Serene Atlantic Hotel Ltd',
  fiscal_year: '2025',
  periodicity: 'Yearly',
  accumulated_values: false
})

// Computed
const debugInfo = computed(() => ({
  testFilters: testFilters,
  testResults: testResults.value,
  loading: loading.value,
  error: error.value
}))

// Methods
const goBack = () => {
  router.push('/dashboard')
}

const runAllTests = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log('Running all tests with filters:', testFilters)
    // const results = await testApiService.runAllTests(testFilters)
    testResults.value = { success: false, error: 'testApi service not available' }
    console.log('All tests completed:', results)
  } catch (err) {
    console.error('Failed to run tests:', err)
    error.value = err.message || 'Failed to run tests'
  } finally {
    loading.value = false
  }
}

const testConnection = async () => {
  loading.value = true
  error.value = null
  
  try {
    // const result = await testApiService.testConnection()
    testResults.value = { connection: { success: false, error: 'testApi service not available' } }
  } catch (err) {
    error.value = err.message || 'Connection test failed'
  } finally {
    loading.value = false
  }
}

const testPeriodList = async () => {
  loading.value = true
  error.value = null
  
  try {
    // const result = await testApiService.testPeriodListGeneration(testFilters)
    testResults.value = { periodList: { success: false, error: 'testApi service not available' } }
  } catch (err) {
    error.value = err.message || 'Period list test failed'
  } finally {
    loading.value = false
  }
}

const testIncomeData = async () => {
  loading.value = true
  error.value = null
  
  try {
    // const result = await testApiService.testIncomeDataGeneration(testFilters)
    testResults.value = { income: { success: false, error: 'testApi service not available' } }
  } catch (err) {
    error.value = err.message || 'Income data test failed'
  } finally {
    loading.value = false
  }
}

const testExpenseData = async () => {
  loading.value = true
  error.value = null
  
  try {
    // const result = await testApiService.testExpenseDataGeneration(testFilters)
    testResults.value = { expense: { success: false, error: 'testApi service not available' } }
  } catch (err) {
    error.value = err.message || 'Expense data test failed'
  } finally {
    loading.value = false
  }
}

const testColumns = async () => {
  loading.value = true
  error.value = null
  
  try {
    // const result = await testApiService.testColumnsGeneration(testFilters)
    testResults.value = { columns: { success: false, error: 'testApi service not available' } }
  } catch (err) {
    error.value = err.message || 'Columns test failed'
  } finally {
    loading.value = false
  }
}

const testCompletePnl = async () => {
  loading.value = true
  error.value = null
  
  try {
    // const result = await testApiService.testCompletePnlExecution(testFilters)
    testResults.value = { completePnl: { success: false, error: 'testApi service not available' } }
  } catch (err) {
    error.value = err.message || 'Complete P&L test failed'
  } finally {
    loading.value = false
  }
}

const testGrowthView = async () => {
  loading.value = true
  error.value = null
  
  try {
    // const result = await testApiService.testGrowthViewComputation(testFilters)
    testResults.value = { growth: { success: false, error: 'testApi service not available' } }
  } catch (err) {
    error.value = err.message || 'Growth view test failed'
  } finally {
    loading.value = false
  }
}

const testMarginView = async () => {
  loading.value = true
  error.value = null
  
  try {
    // const result = await testApiService.testMarginViewComputation(testFilters)
    testResults.value = { margin: { success: false, error: 'testApi service not available' } }
  } catch (err) {
    error.value = err.message || 'Margin view test failed'
  } finally {
    loading.value = false
  }
}

const testGLEntries = async () => {
  loading.value = true
  error.value = null
  
  try {
    // const result = await testApiService.testGLEntries(testFilters)
    testResults.value = { glEntries: { success: false, error: 'testApi service not available' } }
  } catch (err) {
    error.value = err.message || 'GL entries test failed'
  } finally {
    loading.value = false
  }
}

const testDashboardDataStructure = async () => {
  loading.value = true
  error.value = null
  
  try {
    // const result = await testApiService.testDashboardDataStructure(testFilters)
    testResults.value = { dashboardDataStructure: { success: false, error: 'testApi service not available' } }
  } catch (err) {
    error.value = err.message || 'Dashboard data structure test failed'
  } finally {
    loading.value = false
  }
}

const testPerformance = async () => {
  loading.value = true
  error.value = null
  
  try {
    // const result = await testApiService.testPerformance(testFilters, 5)
    testResults.value = { performance: { success: false, error: 'testApi service not available' } }
  } catch (err) {
    error.value = err.message || 'Performance test failed'
  } finally {
    loading.value = false
  }
}

const compareWithErpnext = async () => {
  loading.value = true
  error.value = null
  
  try {
    // const result = await testApiService.compareWithErpnext(testFilters)
    testResults.value = { comparison: { success: false, error: 'testApi service not available' } }
  } catch (err) {
    error.value = err.message || 'Comparison test failed'
  } finally {
    loading.value = false
  }
}

const getTestSummary = async () => {
  loading.value = true
  error.value = null
  
  try {
    // const result = await testApiService.getTestSummary()
    testResults.value = { summary: result }
  } catch (err) {
    error.value = err.message || 'Summary test failed'
  } finally {
    loading.value = false
  }
}

const exportTestResults = () => {
  if (!testResults.value || Object.keys(testResults.value).length === 0) return
  
  const blob = new Blob([JSON.stringify(testResults.value, null, 2)], {
    type: 'application/json'
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `test-results-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// Development: Enable debug mode with keyboard shortcut
if (process.env.NODE_ENV === 'development') {
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'D') {
      showDebug.value = !showDebug.value
    }
  })
}
</script>
