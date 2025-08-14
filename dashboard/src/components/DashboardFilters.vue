<template>
  <Card class="mb-6 bg-gradient-card shadow-dashboard-md border-table-border">
    <CardHeader class="pb-4">
      <div class="flex items-center justify-between">
        <CardTitle class="text-dashboard-header flex items-center gap-2">
          <Filter class="h-5 w-5 text-primary" />
          Dashboard Controls
        </CardTitle>
        <div class="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            @click="onRefresh"
            class="text-muted-foreground border-table-border hover:bg-table-header"
          >
            <RefreshCw class="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button
            variant="outline"
            size="sm"
            @click="onExport"
            class="text-muted-foreground border-table-border hover:bg-table-header"
          >
            <Download class="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>
    </CardHeader>
    
    <CardContent class="space-y-4">
                        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                    <div class="space-y-2">
                      <Label class="text-dashboard-subheader flex items-center gap-2">
                        <Calendar class="h-4 w-4" />
                        Fiscal Year
                      </Label>
                      <select 
                        v-model="selectedYear" 
                        @change="handleYearChange(selectedYear)"
                        class="w-full px-3 py-2 border border-table-border rounded-md focus:ring-primary focus:border-primary bg-background text-foreground"
                      >
                        <option value="">Select fiscal year</option>
                        <option v-for="fiscalYear in fiscalYears" :key="fiscalYear" :value="fiscalYear">
                          {{ fiscalYear }}
                        </option>
                      </select>
                    </div>
                    
                    <div class="space-y-2">
                      <Label class="text-dashboard-subheader flex items-center gap-2">
                        <Calendar class="h-4 w-4" />
                        Month
                      </Label>
                      <select 
                        v-model="selectedMonth" 
                        @change="handleMonthChange"
                        class="w-full px-3 py-2 border border-table-border rounded-md focus:ring-primary focus:border-primary bg-background text-foreground"
                      >
                        <option value="">Select month</option>
                        <option value="1">January</option>
                        <option value="2">February</option>
                        <option value="3">March</option>
                        <option value="4">April</option>
                        <option value="5">May</option>
                        <option value="6">June</option>
                        <option value="7">July</option>
                        <option value="8">August</option>
                        <option value="9">September</option>
                        <option value="10">October</option>
                        <option value="11">November</option>
                        <option value="12">December</option>
                      </select>
                    </div>
                    
                    <div class="space-y-2">
                      <Label class="text-dashboard-subheader flex items-center gap-2">
                        <Building class="h-4 w-4" />
                        Cost Center
                      </Label>
                      <select 
                        v-model="selectedCostCenter" 
                        @change="handleCostCenterChange"
                        class="w-full px-3 py-2 border border-table-border rounded-md focus:ring-primary focus:border-primary bg-background text-foreground"
                      >
                        <option value="">All Cost Centers</option>
                        <option v-for="costCenter in costCenters" :key="costCenter" :value="costCenter">
                          {{ costCenter }}
                        </option>
                      </select>
                    </div>
                    
                    <div class="flex flex-col space-y-2">
                      <div class="flex items-center space-x-2">
                        <input
                          id="global-hide-zeros"
                          type="checkbox"
                          v-model="hideZeroRows"
                          @change="handleHideZerosChange"
                          class="h-5 w-5 text-primary"
                        />
                        <label for="global-hide-zeros" class="text-sm cursor-pointer text-dashboard-subheader">
                          Hide Zero Rows
                        </label>
                      </div>
                      <Button 
                        variant="outline" 
                        @click="clearFilters"
                        class="w-full border-table-border hover:bg-table-header text-muted-foreground"
                      >
                        Clear Filters
                      </Button>
                    </div>
                  </div>
      
                        <div v-if="selectedYear" class="text-center text-sm text-muted-foreground">
                    <p>Current Year: <span class="font-medium text-primary text-lg">{{ selectedYear }}</span></p>
                    <p v-if="selectedMonth">Selected Month: <span class="font-medium text-primary text-lg">{{ getMonthName(selectedMonth) }}</span></p>
                    <p v-if="selectedCostCenter">Selected Cost Center: <span class="font-medium text-primary text-lg">{{ selectedCostCenter }}</span></p>
                    <p>Data loads automatically as you type</p>
                    <p class="text-xs mt-1">Press Enter or type to apply changes</p>
                    <p v-if="selectedMonth" class="text-xs mt-1">Month selection will automatically update the dashboard</p>
                    <p v-if="selectedCostCenter" class="text-xs mt-1">Cost center selection will automatically update the dashboard</p>
                  </div>
    </CardContent>
  </Card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui'
import { Button } from '@/components/ui'
import { Label } from '@/components/ui'
import { Input } from '@/components/ui'
import { Filter, RefreshCw, Download, Calendar, Building } from 'lucide-vue-next'
import apiService from '../services/api'

const props = defineProps({
  onFiltersChange: {
    type: Function,
    required: true
  },
  onRefresh: {
    type: Function,
    required: true
  },
  onExport: {
    type: Function,
    required: true
  }
})

const emit = defineEmits(['filtersChange', 'refresh', 'export', 'hideZerosChange'])

// State
const selectedYear = ref('') // Default to empty until fiscal years are loaded
const selectedMonth = ref('') // Default to no month selected
const selectedCostCenter = ref('') // Default to no cost center selected
const costCenters = ref([]) // List of available cost centers
const fiscalYears = ref([]) // List of available fiscal years
const hideZeroRows = ref(false) // Global hide zero rows toggle

// Methods
const handleYearChange = (year) => {
  console.log('Year changed to:', year)
  selectedYear.value = year
  if (!year || year.trim() === '') return
  
  const filters = { 
    fiscal_year: year.trim(),
    month: selectedMonth.value || undefined,
    cost_center: selectedCostCenter.value || undefined
  }
  console.log('Emitting filters:', filters)
  emit('filtersChange', filters)
}

const handleMonthChange = (event) => {
  const month = event.target.value
  console.log('Month changed to:', month)
  selectedMonth.value = month
  const filters = { 
    fiscal_year: selectedYear.value,
    month: month || undefined,
    cost_center: selectedCostCenter.value || undefined
  }
  console.log('Emitting filters:', filters)
  emit('filtersChange', filters)
}

const handleCostCenterChange = (event) => {
  const costCenter = event.target.value
  console.log('Cost center changed to:', costCenter)
  selectedCostCenter.value = costCenter
  const filters = { 
    fiscal_year: selectedYear.value,
    month: selectedMonth.value || undefined,
    cost_center: costCenter || undefined
  }
  console.log('Emitting filters:', filters)
  emit('filtersChange', filters)
}

const clearFilters = () => {
  selectedYear.value = ''
  selectedMonth.value = ''
  selectedCostCenter.value = ''
  hideZeroRows.value = false
  emit('filtersChange', {})
  emit('hideZerosChange', false)
}

const handleHideZerosChange = () => {
  console.log('Hide zeros changed to:', hideZeroRows.value)
  emit('hideZerosChange', hideZeroRows.value)
}

const getMonthName = (monthNumber) => {
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ]
  return months[parseInt(monthNumber) - 1] || ''
}

const onRefresh = () => {
  emit('refresh')
}

const onExport = () => {
  emit('export')
}

// Load cost centers from API
const loadCostCenters = async () => {
  try {
    const costCentersData = await apiService.getCostCenters()
    costCenters.value = costCentersData || []
    console.log('Loaded cost centers:', costCenters.value)
  } catch (error) {
    console.error('Failed to load cost centers:', error)
    costCenters.value = []
  }
}

// Load fiscal years from API
const loadFiscalYears = async () => {
  try {
    const fiscalYearsData = await apiService.getFiscalYears()
    fiscalYears.value = fiscalYearsData || []
    console.log('Loaded fiscal years:', fiscalYears.value)
    
    // Set default to the most recent fiscal year if available
    if (fiscalYears.value.length > 0 && !selectedYear.value) {
      selectedYear.value = fiscalYears.value[0]
      handleYearChange(selectedYear.value)
    }
  } catch (error) {
    console.error('Failed to load fiscal years:', error)
    fiscalYears.value = []
  }
}

// Trigger initial year selection on mount
onMounted(async () => {
  // Load fiscal years first
  await loadFiscalYears()
  
  // Load cost centers
  await loadCostCenters()
})
</script> 