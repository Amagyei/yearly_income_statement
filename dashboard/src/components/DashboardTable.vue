<template>
  <div class="space-y-6">
    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <Card class="bg-gradient-card border-table-border">
        <CardContent class="p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-muted-foreground">Total Budget</p>
              <p class="text-2xl font-bold text-dashboard-header">{{ formatNumber(summaryData.totalBudget) }}</p>
            </div>
            <DollarSign class="h-8 w-8 text-primary" />
          </div>
        </CardContent>
      </Card>

      <Card class="bg-gradient-card border-table-border">
        <CardContent class="p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-muted-foreground">Total Actual</p>
              <p class="text-2xl font-bold text-dashboard-header">{{ formatNumber(summaryData.totalActual) }}</p>
            </div>
            <BarChart3 class="h-8 w-8 text-primary" />
          </div>
        </CardContent>
      </Card>

      <Card class="bg-gradient-card border-table-border">
        <CardContent class="p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-muted-foreground">Variance</p>
              <p class="text-2xl font-bold text-dashboard-header">{{ formatNumber(summaryData.variance) }}</p>
            </div>
            <TrendingUp class="h-8 w-8 text-primary" />
          </div>
        </CardContent>
      </Card>

      <Card class="bg-gradient-card border-table-border">
        <CardContent class="p-4">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-muted-foreground">Variance %</p>
              <p class="text-2xl font-bold text-dashboard-header">{{ formatPercentage(summaryData.variancePercentage) }}</p>
            </div>
            <PieChart class="h-8 w-8 text-primary" />
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Main Data Table -->
    <Card class="bg-gradient-card shadow-dashboard-lg border-table-border">
      <CardHeader>
        <CardTitle class="text-dashboard-header">Expense Dashboard</CardTitle>
      </CardHeader>
      <CardContent class="p-0">
        <div class="overflow-x-auto">
          <Table>
            <TableHeader class="bg-table-header">
              <TableRow class="border-table-border">
                <TableHead class="w-[200px] border-r border-table-border sticky left-0 bg-table-header z-10">
                  <Button 
                    variant="ghost" 
                    @click="handleSort('category')"
                    class="h-auto p-0 font-semibold text-dashboard-header hover:bg-transparent"
                  >
                    Other Expenses
                    <ArrowUpDown class="ml-2 h-4 w-4" />
                  </Button>
                </TableHead>
                
                <!-- Current Month Section -->
                <TableHead colSpan="5" class="text-center border-r border-table-border bg-primary/5">
                  <div class="text-dashboard-header font-semibold">Current Month</div>
                </TableHead>
                
                <!-- Year to Date Section -->
                <TableHead colSpan="5" class="text-center border-r border-table-border bg-success/5">
                  <div class="text-dashboard-header font-semibold">Year to Date</div>
                </TableHead>
                
                <!-- Forecast Section -->
                <TableHead colSpan="5" class="text-center bg-warning/5">
                  <div class="text-dashboard-header font-semibold">Forecast</div>
                </TableHead>
              </TableRow>
              
              <TableRow class="border-table-border">
                <TableHead class="border-r border-table-border sticky left-0 bg-table-header z-10"></TableHead>
                
                <!-- Current Month Subheaders -->
                <TableHead 
                  v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                  :key="`cm-${idx}`" 
                  class="text-center border-r border-table-border text-dashboard-subheader py-1"
                >
                  <Button
                    variant="ghost"
                    @click="handleSort(`currentMonth.${header.toLowerCase().replace(/\s+/g, '').replace('/', 'To')}`)"
                    class="h-auto p-1 text-xs hover:bg-transparent"
                  >
                    {{ header }}
                    <ArrowUpDown class="ml-1 h-3 w-3" />
                  </Button>
                </TableHead>
                
                <!-- Year to Date Subheaders -->
                <TableHead 
                  v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                  :key="`ytd-${idx}`" 
                  class="text-center border-r border-table-border text-dashboard-subheader py-1"
                >
                  <Button
                    variant="ghost"
                    @click="handleSort(`yearToDate.${header.toLowerCase().replace(/\s+/g, '').replace('/', 'To')}`)"
                    class="h-auto p-1 text-xs hover:bg-transparent"
                  >
                    {{ header }}
                    <ArrowUpDown class="ml-1 h-3 w-3" />
                  </Button>
                </TableHead>
                
                <!-- Forecast Subheaders -->
                <TableHead 
                  v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                  :key="`fc-${idx}`" 
                  :class="`text-center text-dashboard-subheader py-1 ${idx < 4 ? 'border-r border-table-border' : ''}`"
                >
                  <Button
                    variant="ghost"
                    @click="handleSort(`forecast.${header.toLowerCase().replace(/\s+/g, '').replace('/', 'To')}`)"
                    class="h-auto p-1 text-xs hover:bg-transparent"
                  >
                    {{ header }}
                    <ArrowUpDown class="ml-1 h-3 w-3" />
                  </Button>
                </TableHead>
              </TableRow>
            </TableHeader>
            
            <TableBody>
              <TableRow 
                v-for="row in sortedData" 
                :key="`${row.type}-${row.category}`" 
                :class="getRowClass(row)"
              >
                <TableCell :class="getCategoryCellClass(row)">
                  {{ getCategoryDisplay(row) }}
                </TableCell>
                
                <!-- Current Month Data -->
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row.currentMonth.lastYear) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row.currentMonth.budget) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row.currentMonth.actual) }}
                </TableCell>
                <TableCell class="text-right py-1">
                  <span :class="getPercentageClass(row.currentMonth.actBudThisYear)" class="block text-right">
                    {{ typeof row.currentMonth.actBudThisYear === 'string' ? row.currentMonth.actBudThisYear : formatPercentage(row.currentMonth.actBudThisYear) }}
                  </span>
                </TableCell>
                <TableCell class="text-right py-1">
                  <span :class="getPercentageClass(row.currentMonth.actVsLastYear)" class="block text-right">
                    {{ typeof row.currentMonth.actVsLastYear === 'string' ? row.currentMonth.actVsLastYear : formatPercentage(row.currentMonth.actVsLastYear) }}
                  </span>
                </TableCell>
                
                <!-- Year to Date Data -->
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row.yearToDate.lastYear) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row.yearToDate.budget) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row.yearToDate.actual) }}
                </TableCell>
                <TableCell class="text-right py-1">
                  <span :class="getPercentageClass(row.yearToDate.actBudThisYear)" class="block text-right">
                    {{ typeof row.yearToDate.actBudThisYear === 'string' ? row.yearToDate.actBudThisYear : formatPercentage(row.yearToDate.actBudThisYear) }}
                  </span>
                </TableCell>
                <TableCell class="text-right py-1">
                  <span :class="getPercentageClass(row.yearToDate.actVsLastYear)" class="block text-right">
                    {{ typeof row.yearToDate.actVsLastYear === 'string' ? row.yearToDate.actVsLastYear : formatPercentage(row.yearToDate.actVsLastYear) }}
                  </span>
                </TableCell>
                
                <!-- Forecast Data -->
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row.forecast.lastYear) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row.forecast.budget) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row.forecast.actual) }}
                </TableCell>
                <TableCell class="text-right py-1">
                  <span :class="getPercentageClass(row.forecast.actBudThisYear)" class="block text-right">
                    {{ typeof row.forecast.actBudThisYear === 'string' ? row.forecast.actBudThisYear : formatPercentage(row.forecast.actBudThisYear) }}
                  </span>
                </TableCell>
                <TableCell class="text-right py-1">
                  <span :class="getPercentageClass(row.forecast.actVsLastYear)" class="block text-right">
                    {{ typeof row.forecast.actVsLastYear === 'string' ? row.forecast.actVsLastYear : formatPercentage(row.forecast.actVsLastYear) }}
                  </span>
                </TableCell>
              </TableRow>
              
              <!-- Totals Row -->
              <TableRow class="border-t-2 border-primary bg-primary/5 font-semibold">
                <TableCell class="font-bold border-r border-table-border sticky left-0 bg-primary/5 z-10 py-1">
                  TOTAL
                </TableCell>
                
                <!-- Current Month Totals -->
                <TableCell class="text-right border-r border-table-border py-1">{{ formatNumber(totals.currentMonth.lastYear) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-1">{{ formatNumber(totals.currentMonth.budget) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-1">{{ formatNumber(totals.currentMonth.actual) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-1">
                  {{ formatPercentage((totals.currentMonth.actual / totals.currentMonth.budget) * 100) }}
                </TableCell>
                <TableCell class="text-right border-r border-table-border py-1">
                  {{ formatPercentage((totals.currentMonth.actVsLastYear / totals.currentMonth.lastYear) * 100) }}
                </TableCell>
                
                <!-- Year to Date Totals -->
                <TableCell class="text-right border-r border-table-border py-1">{{ formatNumber(totals.yearToDate.lastYear) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-1">{{ formatNumber(totals.yearToDate.budget) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-1">{{ formatNumber(totals.yearToDate.actual) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-1">
                  {{ formatPercentage((totals.yearToDate.actual / totals.yearToDate.budget) * 100) }}
                </TableCell>
                <TableCell class="text-right border-r border-table-border py-1">
                  {{ formatPercentage((totals.yearToDate.actual / totals.yearToDate.lastYear) * 100) }}
                </TableCell>
                
                <!-- Forecast Totals -->
                <TableCell class="text-right border-r border-table-border py-1">{{ formatNumber(totals.forecast.lastYear) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-1">{{ formatNumber(totals.forecast.budget) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-1">{{ formatNumber(totals.forecast.actual) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-1">
                  {{ formatPercentage((totals.forecast.actual / totals.forecast.budget) * 100) }}
                </TableCell>
                <TableCell class="text-right py-1">
                  {{ formatPercentage((totals.forecast.actual / totals.forecast.lastYear) * 100) }}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui'
import { Button } from '@/components/ui'
import { Badge } from '@/components/ui'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui'
import { ArrowUpDown, TrendingUp, TrendingDown, Minus, BarChart3, PieChart, DollarSign } from 'lucide-vue-next'

const props = defineProps({
  filters: {
    type: Object,
    required: true
  },
  data: {
    type: Array,
    default: () => []
  },
  summaryData: {
    type: Object,
    default: () => ({})
  }
})

const sortConfig = ref(null)

// Utility function for number formatting - ensures positive values
const formatNumber = (value) => {
  if (value === null || value === undefined) return '0'
  const num = Math.abs(parseFloat(value)) // Take absolute value to ensure positive
  if (isNaN(num)) return '0'
  return num.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  })
}

const formatPercentage = (value) => {
  if (value === null || value === undefined) return '0%'
  const num = Math.abs(parseFloat(value)) // Take absolute value to ensure positive
  if (isNaN(num)) return '0%'
  return `${num.toFixed(1)}%`
}

const getPercentageClass = (value) => {
  if (value === null || value === undefined || value === 'N/A') return 'text-muted-foreground'
  const num = Math.abs(parseFloat(value)) // Take absolute value for display
  if (isNaN(num)) return 'text-muted-foreground'
  
  const isPositive = num >= 100
  const isNeutral = Math.abs(num - 100) < 1
  
  return `flex items-center gap-1 font-medium ${
    isNeutral ? 'text-status-neutral' : 
    isPositive ? 'text-status-positive' : 'text-status-negative'
  }`
}

const getVarianceColor = (actual, budget) => {
  if (!budget || budget === 0) return 'text-muted-foreground'
  const variance = ((actual - budget) / budget) * 100
  return variance > 0 ? 'text-status-negative' : 'text-status-positive'
}

const calculateTotals = (data) => {
  return data.reduce((acc, item) => ({
    currentMonth: {
      budget: acc.currentMonth.budget + Math.abs(item.currentMonth.budget || 0),
      actual: acc.currentMonth.actual + Math.abs(item.currentMonth.actual || 0),
      actToBudget: acc.currentMonth.actToBudget + (typeof item.currentMonth.actToBudget === 'number' ? Math.abs(item.currentMonth.actToBudget) : 0),
      thisYear: acc.currentMonth.thisYear + (typeof item.currentMonth.thisYear === 'number' ? Math.abs(item.currentMonth.thisYear) : 0),
      actToLastYear: acc.currentMonth.actToLastYear + (typeof item.currentMonth.actToLastYear === 'number' ? Math.abs(item.currentMonth.actToLastYear) : 0),
    },
    yearToDate: {
      lastYear: acc.yearToDate.lastYear + Math.abs(item.yearToDate.lastYear || 0),
      budget: acc.yearToDate.budget + Math.abs(item.yearToDate.budget || 0),
      actual: acc.yearToDate.actual + Math.abs(item.yearToDate.actual || 0),
    },
    forecast: {
      lastYear: acc.forecast.lastYear + Math.abs(item.forecast.lastYear || 0),
      budget: acc.forecast.budget + Math.abs(item.forecast.budget || 0),
      actual: acc.forecast.actual + Math.abs(item.forecast.actual || 0),
    }
  }), {
    currentMonth: { budget: 0, actual: 0, actToBudget: 0, thisYear: 0, actToLastYear: 0 },
    yearToDate: { lastYear: 0, budget: 0, actual: 0 },
    forecast: { lastYear: 0, budget: 0, actual: 0 }
  })
}

const totals = computed(() => calculateTotals(props.data))

const handleSort = (key) => {
  sortConfig.value = {
    key,
    direction: sortConfig.value?.key === key && sortConfig.value.direction === 'asc' ? 'desc' : 'asc'
  }
}

// Helper methods for structured data display
const getRowClass = (row) => {
  const baseClass = 'border-table-border transition-dashboard'
  
  switch (row.type) {
    case 'header':
      return `${baseClass} bg-primary/10 hover:bg-primary/15 font-bold`
    case 'sub_header':
      return `${baseClass} bg-secondary/10 hover:bg-secondary/15 font-semibold`
    case 'total':
      return `${baseClass} bg-success/10 hover:bg-success/15 font-semibold`
    case 'summary':
      return `${baseClass} bg-warning/10 hover:bg-warning/15 font-bold`
    default:
      return `${baseClass} hover:bg-table-header/50`
  }
}

const getCategoryCellClass = (row) => {
  const baseClass = 'border-r border-table-border sticky left-0 z-10 py-1'
  
  switch (row.type) {
    case 'header':
      return `${baseClass} bg-primary/10 font-bold text-lg text-primary`
    case 'sub_header':
      return `${baseClass} bg-secondary/10 font-semibold text-base text-secondary-foreground`
    case 'total':
      return `${baseClass} bg-success/10 font-semibold text-base text-success-foreground`
    case 'summary':
      return `${baseClass} bg-warning/10 font-bold text-lg text-warning-foreground`
    default:
      return `${baseClass} bg-background font-medium`
  }
}

const getCategoryDisplay = (row) => {
  switch (row.type) {
    case 'header':
      return row.category.toUpperCase()
    case 'sub_header':
      return `  ${row.category}` // Indent sub-headers
    case 'total':
      return `    ${row.category}` // Indent totals
    case 'summary':
      return `*** ${row.category} ***` // Highlight summaries
    default:
      return row.category
  }
}

const sortedData = computed(() => {
  if (!sortConfig.value) return props.data
  
  return [...props.data].sort((a, b) => {
    let aValue, bValue
    
    if (sortConfig.value.key === 'category') {
      return sortConfig.value.direction === 'asc' 
        ? a.category.localeCompare(b.category)
        : b.category.localeCompare(a.category)
    }
    
    // Handle nested sorting for financial data
    const [period, metric] = sortConfig.value.key.split('.')
    aValue = a[period][metric]
    bValue = b[period][metric]
    
    return sortConfig.value.direction === 'asc' ? aValue - bValue : bValue - aValue
  })
})
</script> 