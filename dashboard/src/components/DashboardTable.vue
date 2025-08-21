<template>
  <Card class="bg-gradient-card shadow-dashboard-lg border-table-border">
    <CardHeader class="flex items-center justify-between px-4 py-2">
      <div class="flex items-center space-x-3">
        <Button 
          variant="ghost" 
          size="sm"
          @click="minimizeIncome = !minimizeIncome"
          class="p-1"
        >
          {{ minimizeIncome ? '▶' : '▼' }}
        </Button>
        <CardTitle class="text-dashboard-header font-bold text-lg">Income Statement</CardTitle>
      </div>
    </CardHeader>
    
    <CardContent class="p-0" v-if="!minimizeIncome">
      <div class="overflow-x-auto">
        <Table>
          <TableHeader class="bg-table-header">
            <TableRow class="border-table-border">
              <TableHead class="w-auto min-w-[200px] max-w-[800px] border-r border-table-border sticky left-0 bg-table-header z-10 whitespace-nowrap">
                <div class="text-dashboard-header font-semibold">Category</div>
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
                <div class="text-xs">{{ header }}</div>
              </TableHead>
              
              <!-- Year to Date Subheaders -->
              <TableHead 
                v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                :key="`ytd-${idx}`" 
                class="text-center border-r border-table-border text-dashboard-subheader py-1"
              >
                <div class="text-xs">{{ header }}</div>
              </TableHead>
              
              <!-- Forecast Subheaders -->
              <TableHead 
                v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                :key="`fc-${idx}`" 
                class="text-center text-dashboard-subheader py-1"
              >
                <div class="text-xs">{{ header }}</div>
              </TableHead>
            </TableRow>
          </TableHeader>
          
          <TableBody>
            <!-- REVENUE SECTION -->
            <TableRow class="bg-primary/10 hover:bg-primary/20 border-b-2 border-primary font-bold">
              <TableCell class="font-bold border-r border-table-border sticky left-0 bg-primary/10 z-10 py-3">
                REVENUE
              </TableCell>
              <!-- Current Month Revenue Totals -->
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('currentMonth', 'lastYear')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('currentMonth', 'budget')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('currentMonth', 'actual')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <!-- Year to Date Revenue Totals -->
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('yearToDate', 'lastYear')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('yearToDate', 'budget')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('yearToDate', 'actual')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <!-- Forecast Revenue Totals -->
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('forecast', 'lastYear')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('forecast', 'budget')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('forecast', 'actual')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
            </TableRow>
            
            <!-- Revenue Data grouped by sub-headers -->
            <template v-for="group in getVisibleRevenueGroups()" :key="`rev-sub-${group.subHeader?.category}`">
              <!-- Sub-header total row -->
              <TableRow class="bg-primary/10 hover:bg-primary/20 font-medium">
                <TableCell class="font-semibold text-primary/80 border-r border-table-border sticky left-0 z-10" :style="{ paddingLeft: '20px' }">
                  {{ group.subHeader?.category || 'Revenue Group' }}
                </TableCell>
                
                <!-- Current Month Totals for Sub-header -->
                <TableCell class="text-right font-medium py-1">{{ formatCurrency(getSubHeaderTotal(group,'currentMonth','lastYear')) }}</TableCell>
                <TableCell class="text-right font-medium py-1">{{ formatCurrency(getSubHeaderTotal(group,'currentMonth','budget')) }}</TableCell>
                <TableCell class="text-right font-medium py-1">{{ formatCurrency(getSubHeaderTotal(group,'currentMonth','actual')) }}</TableCell>
                <TableCell class="text-right py-1"></TableCell>
                <TableCell class="text-right py-1"></TableCell>
                
                <!-- Year to Date Totals for Sub-header -->
                <TableCell class="text-right font-medium py-1">{{ formatCurrency(getSubHeaderTotal(group,'yearToDate','lastYear')) }}</TableCell>
                <TableCell class="text-right font-medium py-1">{{ formatCurrency(getSubHeaderTotal(group,'yearToDate','budget')) }}</TableCell>
                <TableCell class="text-right font-medium py-1">{{ formatCurrency(getSubHeaderTotal(group,'yearToDate','actual')) }}</TableCell>
                <TableCell class="text-right py-1"></TableCell>
                <TableCell class="text-right py-1"></TableCell>
                
                <!-- Forecast Totals for Sub-header -->
                <TableCell class="text-right font-medium py-1">{{ formatCurrency(getSubHeaderTotal(group,'forecast','lastYear')) }}</TableCell>
                <TableCell class="text-right font-medium py-1">{{ formatCurrency(getSubHeaderTotal(group,'forecast','budget')) }}</TableCell>
                <TableCell class="text-right font-medium py-1">{{ formatCurrency(getSubHeaderTotal(group,'forecast','actual')) }}</TableCell>
                <TableCell class="text-right py-1"></TableCell>
                <TableCell class="text-right py-1"></TableCell>
              </TableRow>

              <!-- Revenue account rows under this sub-header -->
              <template v-for="row in group.accounts" :key="`rev-account-${row.account || row.category}`">
                <TableRow :class="getRowClass(row)">
                  <TableCell :class="getCategoryCellClass(row)" :style="{ paddingLeft: '40px' }">
                    {{ getCategoryDisplay(row) }}
                  </TableCell>

                  <!-- Current Month Data -->
                  <TableCell class="text-right font-medium py-1">
                    {{ formatCurrency(row?.currentMonth?.lastYear || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatCurrency(row?.currentMonth?.budget || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatCurrency(row?.currentMonth?.actual || 0) }}
                  </TableCell>
                  <TableCell class="text-right py-1">
                    <span :class="getPercentageClass(row?.currentMonth?.actBudThisYear)" class="block text-right">
                      {{ typeof row?.currentMonth?.actBudThisYear === 'string' ? row?.currentMonth?.actBudThisYear : formatPercentage(row?.currentMonth?.actBudThisYear) }}
                    </span>
                  </TableCell>
                  <TableCell class="text-right py-1">
                    <span :class="getPercentageClass(row?.currentMonth?.actVsLastYear)" class="block text-right">
                      {{ typeof row?.currentMonth?.actVsLastYear === 'string' ? row?.currentMonth?.actVsLastYear : formatPercentage(row?.currentMonth?.actVsLastYear) }}
                    </span>
                  </TableCell>

                  <!-- Year to Date Data -->
                  <TableCell class="text-right font-medium py-1">
                    {{ formatCurrency(row?.yearToDate?.lastYear || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatCurrency(row?.yearToDate?.budget || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatCurrency(row?.yearToDate?.actual || 0) }}
                  </TableCell>
                  <TableCell class="text-right py-1">
                    <span :class="getPercentageClass(row?.yearToDate?.actBudThisYear)" class="block text-right">
                      {{ typeof row?.yearToDate?.actBudThisYear === 'string' ? row?.yearToDate?.actBudThisYear : formatPercentage(row?.yearToDate?.actBudThisYear) }}
                    </span>
                  </TableCell>
                  <TableCell class="text-right py-1">
                    <span :class="getPercentageClass(row?.yearToDate?.actVsLastYear)" class="block text-right">
                      {{ typeof row?.yearToDate?.actVsLastYear === 'string' ? row?.yearToDate?.actVsLastYear : formatPercentage(row?.yearToDate?.actVsLastYear) }}
                    </span>
                  </TableCell>

                  <!-- Forecast Data -->
                  <TableCell class="text-right font-medium py-1">
                    {{ formatCurrency(row?.forecast?.lastYear || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatCurrency(row?.forecast?.budget || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatCurrency(row?.forecast?.actual || 0) }}
                  </TableCell>
                  <TableCell class="text-right py-1">
                    <span :class="getPercentageClass(row?.forecast?.actBudThisYear)" class="block text-right">
                      {{ typeof row?.forecast?.actBudThisYear === 'string' ? row?.forecast?.actBudThisYear : formatPercentage(row?.forecast?.actBudThisYear) }}
                    </span>
                  </TableCell>
                  <TableCell class="text-right py-1">
                    <span :class="getPercentageClass(row?.forecast?.actVsLastYear)" class="block text-right">
                      {{ typeof row?.forecast?.actVsLastYear === 'string' ? row?.forecast?.actVsLastYear : formatPercentage(row?.forecast?.actVsLastYear) }}
                    </span>
                  </TableCell>
                </TableRow>
              </template>
            </template>
            
            <!-- TOTAL REVENUE ROW -->
            <TableRow class="border-t-2 border-primary bg-primary/20 font-bold">
              <TableCell class="font-bold border-r border-table-border sticky left-0 bg-primary/20 z-10 py-3">
                TOTAL REVENUE
              </TableCell>
              <!-- Current Month Revenue Totals -->
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('currentMonth', 'lastYear')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('currentMonth', 'budget')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('currentMonth', 'actual')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <!-- Year to Date Revenue Totals -->
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('yearToDate', 'lastYear')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('yearToDate', 'budget')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('yearToDate', 'actual')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <!-- Forecast Revenue Totals -->
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('forecast', 'lastYear')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('forecast', 'budget')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getRevenueTotals('forecast', 'actual')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
            </TableRow>
            
            <!-- GROSS PROFIT ROW -->
            <TableRow class="border-t-2 border-success bg-success/20 font-bold">
              <TableCell class="font-bold border-r border-table-border sticky left-0 bg-success/20 z-10 py-3">
                GROSS PROFIT
              </TableCell>
              <!-- Current Month Gross Profit -->
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getGrossProfit('currentMonth', 'lastYear')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getGrossProfit('currentMonth', 'budget')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getGrossProfit('currentMonth', 'actual')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <!-- Year to Date Gross Profit -->
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getGrossProfit('yearToDate', 'lastYear')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getGrossProfit('yearToDate', 'budget')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getGrossProfit('yearToDate', 'actual')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <!-- Forecast Gross Profit -->
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getGrossProfit('forecast', 'lastYear')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getGrossProfit('forecast', 'budget')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3">{{ formatCurrency(getGrossProfit('forecast', 'actual')) }}</TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              <TableCell class="text-right border-r border-table-border py-3"></TableCell>
            </TableRow>
            
          </TableBody>
        </Table>
      </div>
    </CardContent>
  </Card>
</template>

<script setup>
import { ref } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui'
import { Button } from '@/components/ui'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui'

// Props
const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  summaryData: {
    type: Object,
    default: () => ({})
  },
  hideZeroRows: {
    type: Boolean,
    default: false
  }
})

// Local state
const minimizeIncome = ref(false)
// Placeholder: currency code to be fetched from Company document (e.g., 'GHS', 'USD')
const companyCurrency = ref(null)

// Simple utility functions
const formatCurrency = (value) => {
  if (value === null || value === undefined || isNaN(value)) return '0.00'
  // If companyCurrency is available, use it; otherwise render as plain decimal without symbol
  if (companyCurrency.value) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: companyCurrency.value,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value)
  }
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

const formatPercentage = (value) => {
  if (value === null || value === undefined || isNaN(value)) return '0.00%'
  return `${(value * 100).toFixed(2)}%`
}

const getRowClass = (row) => {
  if (row.type === 'header') return 'bg-primary/5 hover:bg-primary/10 font-semibold'
  if (row.type === 'sub_header') return 'bg-primary/10 hover:bg-primary/20 font-medium'
  if (row.type === 'total') return 'bg-success/10 hover:bg-success/20 font-bold border-t-2 border-success'
  return 'hover:bg-gray-50'
}

const getCategoryCellClass = (row) => {
  if (row.type === 'header') return 'font-bold text-primary border-r border-table-border sticky left-0 z-10'
  if (row.type === 'sub_header') return 'font-semibold text-primary/80 border-r border-table-border sticky left-0 z-10'
  if (row.type === 'total') return 'font-bold text-success border-r border-table-border sticky left-0 z-10'
  return 'border-r border-table-border sticky left-0 z-10'
}

const getCategoryDisplay = (row) => {
  if (row.type === 'total') return row.category?.toUpperCase() || 'TOTAL'
  if (row.type === 'header') return row.category || 'Header'
  if (row.type === 'sub_header') return row.category || 'Sub Header'
  if (row.type === 'account') return row.account || row.category || 'Account'
  return row.category || row.account || 'Unknown'
}

const getPercentageClass = (value) => {
  if (value === null || value === undefined || isNaN(value)) return 'text-gray-500'
  if (typeof value === 'string') return 'text-gray-500'
  if (value > 0) return 'text-success'
  if (value < 0) return 'text-destructive'
  return 'text-gray-500'
}

// Helper functions for data organization
const getRevenueRows = () => {
  return (props.data || []).filter(row => row.root_type === 'Income')
}

const getRevenueTotals = (period, metric) => {
  const revenueRows = getRevenueRows()
  return revenueRows.reduce((total, row) => {
    return total + Math.abs(row[period]?.[metric] || 0)
  }, 0)
}

// Revenue sub-header grouping and zero-hiding helpers
const isNumber = (v) => typeof v === 'number' && !Number.isNaN(v)

const getNumeric = (value) => (isNumber(value) ? value : 0)

const getRowValue = (row, period, metric) => {
  if (!row) return 0
  return getNumeric(row?.[period]?.[metric])
}

const rowHasAnyNonZero = (row) => {
  // Check core numeric metrics across periods
  const metrics = ['lastYear', 'budget', 'actual']
  const periods = ['currentMonth', 'yearToDate', 'forecast']
  for (const p of periods) {
    for (const m of metrics) {
      if (Math.abs(getRowValue(row, p, m)) > 0) return true
    }
  }
  return false
}

const getRevenueGroups = () => {
  const revenueRows = (props.data || []).filter(r => r.root_type === 'Income')
  const groups = []
  let currentGroup = null

  for (const row of revenueRows) {
    if (row.type === 'sub_header') {
      currentGroup = { subHeader: row, accounts: [] }
      groups.push(currentGroup)
      continue
    }
    if (row.type === 'account') {
      if (!currentGroup) {
        // If there was no preceding sub_header, bucket into a generic group
        currentGroup = { subHeader: { category: 'Other Revenue', type: 'sub_header' }, accounts: [] }
        groups.push(currentGroup)
      }
      currentGroup.accounts.push(row)
    }
    // Ignore header/total rows inside the grouping block
  }
  return groups
}

const getVisibleRevenueGroups = () => {
  const groups = getRevenueGroups()
  if (!props.hideZeroRows) return groups

  // Filter out zero accounts and empty groups
  const filtered = []
  for (const g of groups) {
    const accounts = g.accounts.filter(a => rowHasAnyNonZero(a))
    if (accounts.length > 0) {
      filtered.push({ subHeader: g.subHeader, accounts })
    }
  }
  return filtered
}

const getSubHeaderTotal = (group, period, metric) => {
  if (!group) return 0
  return (group.accounts || []).reduce((sum, a) => sum + Math.abs(getRowValue(a, period, metric)), 0)
}

// ERPNext-native Direct Expenses helpers
const getDirectExpensesRows = () => {
  return (props.data || []).filter(r => 
    r.type === 'account' && r.is_cost_of_sales === true
  )
}

const getDirectExpensesGroups = () => {
  const directExpenseRows = getDirectExpensesRows()
  const groups = []
  let currentGroup = null

  for (const row of directExpenseRows) {
    if (row.type === 'sub_header') {
      currentGroup = { subHeader: row, accounts: [] }
      groups.push(currentGroup)
      continue
    }
    if (row.type === 'account') {
      if (!currentGroup) {
        // If there was no preceding sub_header, bucket into a generic group
        currentGroup = { subHeader: { category: 'Other Direct Expenses', type: 'sub_header' }, accounts: [] }
        groups.push(currentGroup)
      }
      currentGroup.accounts.push(row)
    }
  }
  return groups
}

const getVisibleDirectExpensesGroups = () => {
  const groups = getDirectExpensesGroups()
  if (!props.hideZeroRows) return groups

  // Filter out zero accounts and empty groups
  const filtered = []
  for (const g of groups) {
    const accounts = g.accounts.filter(a => rowHasAnyNonZero(a))
    if (accounts.length > 0) {
      filtered.push({ subHeader: g.subHeader, accounts })
    }
  }
  return filtered
}

const getDirectExpensesTotals = (period, metric) => {
  const directRows = getDirectExpensesRows()
  return directRows.reduce((sum, row) => {
    const value = getRowValue(row, period, metric)
    return sum + Math.abs(value)
  }, 0)
}

const getGrossProfit = (period, metric) => {
  const revenueTotal = getRevenueTotals(period, metric)
  const directExpensesTotal = getDirectExpensesTotals(period, metric)
  return revenueTotal - directExpensesTotal
}
</script>
