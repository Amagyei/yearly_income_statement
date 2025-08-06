<template>
  <div class="min-h-screen bg-background">
    <div class="container mx-auto p-6 space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-dashboard-header">Yearly Income Statement Dashboard</h1>
          <p class="text-muted-foreground mt-2">Track expenses, budgets, and forecasts across all periods</p>
        </div>
        <div class="flex items-center gap-4">
          <Button 
            variant="outline" 
            @click="refreshData"
            :disabled="loading"
            class="flex items-center gap-2"
          >
            <RefreshCw :class="['h-4 w-4', { 'animate-spin': loading }]" />
            {{ loading ? 'Loading...' : 'Refresh' }}
          </Button>
          <Button 
            @click="exportData"
            :disabled="loading"
            class="flex items-center gap-2"
          >
            <Download class="h-4 w-4" />
            Export
          </Button>
          <Button 
            variant="outline" 
            @click="logout"
            class="flex items-center gap-2"
          >
            Logout
          </Button>
        </div>
      </div>

      <!-- Filters -->
      <DashboardFilters
        @filters-change="handleFiltersChange"
        @refresh="refreshData"
        @export="exportData"
      />

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="flex items-center gap-3">
          <RefreshCw class="h-6 w-6 animate-spin text-primary" />
          <span class="text-lg text-muted-foreground">Loading dashboard data...</span>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
        <div class="flex items-center gap-3">
          <AlertCircle class="h-5 w-5 text-destructive" />
          <div>
            <h3 class="font-semibold text-destructive">Error Loading Data</h3>
            <p class="text-sm text-muted-foreground mt-1">{{ error }}</p>
          </div>
        </div>
        <Button 
          @click="refreshData" 
          variant="outline" 
          size="sm" 
          class="mt-3"
        >
          Try Again
        </Button>
      </div>

      <!-- Dashboard Content -->
      <div v-else-if="dashboardData.length > 0">
        <DashboardTable 
          :filters="currentFilters"
          :data="dashboardData"
          :summary-data="summaryData"
        />
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <div class="max-w-md mx-auto">
          <BarChart3 class="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h3 class="text-lg font-semibold text-dashboard-header mb-2">No Data Available</h3>
          <p class="text-muted-foreground mb-4">
            No expense data found for the selected filters. Try adjusting your filters or check if data exists for the selected period.
          </p>
          <Button @click="refreshData" variant="outline">
            Refresh Data
          </Button>
        </div>
      </div>

      <!-- Debug Info (Development Only) -->
      <div v-if="showDebug" class="mt-8 p-4 bg-muted/50 rounded-lg">
        <h4 class="font-semibold mb-2">Debug Information</h4>
        <pre class="text-xs overflow-auto">{{ debugInfo }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui'
import { RefreshCw, Download, AlertCircle, BarChart3 } from 'lucide-vue-next'
import DashboardFilters from './DashboardFilters.vue'
import DashboardTable from './DashboardTable.vue'
import apiService from '../services/api'
import { session } from '../data/session'

// State
const loading = ref(false)
const error = ref(null)
const dashboardData = ref([])
const summaryData = ref({})
const currentFilters = ref({ fiscal_year: '2023' }) 

// Debug mode (development only)
const showDebug = ref(false)
const router = useRouter()

// Computed
const debugInfo = computed(() => ({
  dataCount: dashboardData.value.length,
  summary: summaryData.value,
  loading: loading.value,
  error: error.value
}))

// Methods
const logout = () => {
  session.logout()
  router.push('/login')
}

// Methods
const handleFiltersChange = (filters) => {
  console.log('Filters changed:', filters)
  console.log('Previous filters:', currentFilters.value)
  currentFilters.value = { ...currentFilters.value, ...filters }
  console.log('Updated filters:', currentFilters.value)
  loadDashboardData()
}

const loadDashboardData = async () => {
  loading.value = true
  error.value = null

  try {
    console.log('Loading dashboard data with filters:', currentFilters.value)

    // Load dashboard data with current filters
    const dashboardResponse = await apiService.getComprehensiveDashboardData(currentFilters.value)
    console.log('Dashboard response:', dashboardResponse)
    dashboardData.value = apiService.transformDashboardData(dashboardResponse)

    // Load summary data with current filters
    const summaryResponse = await apiService.getSummaryData(currentFilters.value)
    console.log('Summary response:', summaryResponse)
    summaryData.value = apiService.transformSummaryData(summaryResponse)

  } catch (err) {
    console.error('Failed to load dashboard data:', err)
    error.value = err.message || 'Failed to load dashboard data'
  } finally {
    loading.value = false
  }
}

const loadFilterOptions = async () => {
  // No filter options to load
  console.log('No filter options to load')
}

const refreshData = () => {
  loadDashboardData()
}

const exportData = async () => {
  try {
    const exportResponse = await apiService.exportDashboardData({}, 'excel')
    
    // Create download link
    const blob = new Blob([JSON.stringify(exportResponse.export_data, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `dashboard-export-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

  } catch (err) {
    console.error('Failed to export data:', err)
    error.value = 'Failed to export data'
  }
}

// Lifecycle
onMounted(async () => {
  await loadFilterOptions()
  await loadDashboardData()
})

// Development: Enable debug mode with keyboard shortcut
if (process.env.NODE_ENV === 'development') {
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'D') {
      showDebug.value = !showDebug.value
    }
  })
}
</script> 