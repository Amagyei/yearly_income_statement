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
            @click="goToTestPage"
            class="flex items-center gap-2"
          >
            <TestTube class="h-4 w-4" />
            Test API
          </Button>
          <Button 
            variant="outline"
            @click="goToErpnextDashboard"
            class="flex items-center gap-2"
          >
            <BarChart3 class="h-4 w-4" />
            ERPNext Dashboard
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
        @hide-zeros-change="handleHideZerosChange"
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
        <!-- Main Dashboard Table with Minimize -->
        <Card class="bg-gradient-card shadow-dashboard-lg border-table-border mb-8">
          <CardHeader class="flex items-center justify-between px-4 py-2">
            <div class="flex items-center space-x-3">
              <Button 
                variant="ghost" 
                size="sm"
                @click="minimizeMainDashboard = !minimizeMainDashboard"
                class="p-1"
              >
                {{ minimizeMainDashboard ? '▶' : '▼' }}
              </Button>
              <CardTitle class="text-dashboard-header font-bold text-lg">Main Dashboard Overview</CardTitle>
              <div class="text-sm text-muted-foreground ml-2">
                Complete financial overview with all accounts and sections
              </div>
            </div>
          </CardHeader>
          <CardContent class="p-0" v-if="!minimizeMainDashboard">
        <DashboardTable 
          :filters="currentFilters"
          :data="dashboardData"
          :summary-data="summaryData"
          :hide-zero-rows="globalHideZeroRows"
        />
          </CardContent>
        </Card>

        <!-- Direct Revenue Table -->
        <Card class="bg-gradient-card shadow-dashboard-lg border-table-border mt-8">
          <CardHeader class="flex items-center justify-between px-4 py-2">
            <div class="flex items-center space-x-3">
              <Button 
                variant="ghost" 
                size="sm"
                @click="minimizeDirectRevenue = !minimizeDirectRevenue"
                class="p-1"
              >
                {{ minimizeDirectRevenue ? '▶' : '▼' }}
              </Button>
              <CardTitle class="text-dashboard-header font-bold text-lg">Direct Revenue (Core Business Income)</CardTitle>
              <div class="text-sm text-muted-foreground ml-2">
                Room, Food, Beverage, Spa & other operational income
              </div>
            </div>
          </CardHeader>
          <CardContent class="p-0" v-if="!minimizeDirectRevenue">
            <div class="overflow-x-auto">
              <Table>
                <TableHeader class="bg-table-header">
                  <TableRow class="border-table-border">
                    <TableHead class="w-auto min-w-[200px] max-w-[800px] border-r border-table-border sticky left-0 bg-table-header z-10 whitespace-nowrap">
                      Account
                    </TableHead>
                    <!-- Period Sections -->
                    <TableHead colspan="5" class="text-center border-r border-table-border bg-green-500/5">
                      <div class="text-dashboard-header font-semibold">Current Month</div>
                    </TableHead>
                    <TableHead colspan="5" class="text-center border-r border-table-border bg-green-500/5">
                      <div class="text-dashboard-header font-semibold">Year to Date</div>
                    </TableHead>
                    <TableHead colspan="5" class="text-center bg-green-500/5">
                      <div class="text-dashboard-header font-semibold">Forecast</div>
                    </TableHead>
                    <!-- Monthly subheaders -->
                    <TableHead v-for="(m, midx) in MONTHLY_COLUMNS" :key="`dr-msh-${midx}`" class="text-center text-dashboard-subheader py-1">
                      <div class="text-xs">{{ m }}</div>
                    </TableHead>
                  </TableRow>
                  <TableRow class="border-table-border">
                    <TableHead class="border-r border-table-border sticky left-0 bg-table-header z-10"></TableHead>
                    <!-- Subheaders for each period -->
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`cm-${idx}`" 
                      class="text-center border-r border-table-border text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`ytd-${idx}`" 
                      class="text-center border-r border-table-border text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`fc-${idx}`" 
                      class="text-center text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <!-- Monthly subheaders with Actual/Budget values -->
                    <TableHead v-for="(m, midx) in MONTHLY_COLUMNS" :key="`dr-sub-${midx}`" class="text-center text-dashboard-subheader py-1">
                      <div class="text-xs">{{ getMonthlySubheaderValue(midx) }}</div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <!-- Group by report_class with a subheader and totals -->
                  <template v-for="(group, gIdx) in groupByReportClass(directRevenueData)" :key="`dr-group-${gIdx}`">
                    <!-- Sub-header row for report_class -->
                    <TableRow class="bg-green-500/10 font-medium">
                      <TableCell class="font-semibold text-green-700 border-r border-table-border sticky left-0 z-10" :style="{ paddingLeft: '20px' }">
                        {{ group.report_class || 'Other' }}
                      </TableCell>
                      <!-- Current Month totals: Last Year, Budget, Actual, (ratios blank) -->
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <!-- Year to Date totals: Last Year, Budget, Actual, (ratios blank) -->
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <!-- Forecast totals: Last Year, Budget, Actual, (ratios blank) -->
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.budget) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.actual) }}</TableCell>
                      <TableCell class="text-right py-1"></TableCell>
                      <TableCell class="text-right py-1"></TableCell>
                      <!-- Monthly placeholder cells -->
                      <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`mrow-total-${gIdx}-${midx}`" class="text-right py-1">
                        {{ formatCurrency(getMonthlyTotalValue(group, midx)) }}
                      </TableCell>
                    </TableRow>

                    <!-- Account rows under this report_class -->
                    <template v-for="row in group.rows" :key="row.account || row.account_name">
                    <TableRow 
                      v-if="!globalHideZeroRows || hasData(row)"
                      class="hover:bg-green-50"
                    >
                        <TableCell class="py-2 border-r border-table-border" :style="{ paddingLeft: '40px' }">
                        {{ row.account_name || row.account }}
                      </TableCell>
                        <!-- Current Month (5 subcolumns) -->
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.currentMonth?.lastYear || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.currentMonth?.budget || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.currentMonth?.actual || 0) }}</TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.currentMonth?.actBudThisYear)" class="block text-right">
                            {{ typeof row.currentMonth?.actBudThisYear === 'string' ? row.currentMonth?.actBudThisYear : formatPercentage(row.currentMonth?.actBudThisYear) }}
                          </span>
                      </TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.currentMonth?.actVsLastYear)" class="block text-right">
                            {{ typeof row.currentMonth?.actVsLastYear === 'string' ? row.currentMonth?.actVsLastYear : formatPercentage(row.currentMonth?.actVsLastYear) }}
                          </span>
                      </TableCell>
                        <!-- Year to Date (5 subcolumns) -->
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.yearToDate?.lastYear || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.yearToDate?.budget || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.yearToDate?.actual || 0) }}</TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.yearToDate?.actBudThisYear)" class="block text-right">
                            {{ typeof row.yearToDate?.actBudThisYear === 'string' ? row.yearToDate?.actBudThisYear : formatPercentage(row.yearToDate?.actBudThisYear) }}
                          </span>
                      </TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.yearToDate?.actVsLastYear)" class="block text-right">
                            {{ typeof row.yearToDate?.actVsLastYear === 'string' ? row.yearToDate?.actVsLastYear : formatPercentage(row.yearToDate?.actVsLastYear) }}
                          </span>
                        </TableCell>
                        <!-- Forecast (5 subcolumns) -->
                        <TableCell class="text-right py-2">{{ formatCurrency(row.forecast?.lastYear || 0) }}</TableCell>
                        <TableCell class="text-right py-2">{{ formatCurrency(row.forecast?.budget || 0) }}</TableCell>
                        <TableCell class="text-right py-2">{{ formatCurrency(row.forecast?.actual || 0) }}</TableCell>
                      <TableCell class="text-right py-2">
                          <span :class="getPercentageClass(row.forecast?.actBudThisYear)" class="block text-right">
                            {{ typeof row.forecast?.actBudThisYear === 'string' ? row.forecast?.actBudThisYear : formatPercentage(row.forecast?.actBudThisYear) }}
                          </span>
                      </TableCell>
                      <TableCell class="text-right py-2">
                          <span :class="getPercentageClass(row.forecast?.actVsLastYear)" class="block text-right">
                            {{ typeof row.forecast?.actVsLastYear === 'string' ? row.forecast?.actVsLastYear : formatPercentage(row.forecast?.actVsLastYear) }}
                          </span>
                      </TableCell>
                      <!-- Monthly placeholder cells -->
                      <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`mrow-${row.account || row.account_name}-${midx}`" class="text-right py-2">
                        {{ formatCurrency(getMonthlyCellValue(row, midx)) }}
                      </TableCell>
                    </TableRow>
                    </template>
                  </template>
                  <!-- Direct Revenue Total -->
                  <TableRow class="border-t-2 border-green-500 bg-green-500/5 font-bold">
                    <TableCell class="font-bold py-3 border-r border-table-border">TOTAL DIRECT REVENUE</TableCell>
                    <!-- Current Month Totals: Last Year, Budget, Actual, (ratios blank) -->
                    <TableCell class="text-right font-bold py-3 border-r border-table-border">{{ formatCurrency(directRevenueTotal.currentMonth?.lastYear || 0) }}</TableCell>
                    <TableCell class="text-right font-bold py-3 border-r border-table-border">{{ formatCurrency(directRevenueTotal.currentMonth?.budget || 0) }}</TableCell>
                    <TableCell class="text-right font-bold py-3 border-r border-table-border">{{ formatCurrency(directRevenueTotal.currentMonth?.actual || 0) }}</TableCell>
                    <TableCell class="text-right font-bold py-3 border-r border-table-border"></TableCell>
                    <TableCell class="text-right font-bold py-3 border-r border-table-border"></TableCell>
                    <!-- Year to Date Totals: Last Year, Budget, Actual, (ratios blank) -->
                    <TableCell class="text-right font-bold py-3 border-r border-table-border">{{ formatCurrency(directRevenueTotal.yearToDate?.lastYear || 0) }}</TableCell>
                    <TableCell class="text-right font-bold py-3 border-r border-table-border">{{ formatCurrency(directRevenueTotal.yearToDate?.budget || 0) }}</TableCell>
                    <TableCell class="text-right font-bold py-3 border-r border-table-border">{{ formatCurrency(directRevenueTotal.yearToDate?.actual || 0) }}</TableCell>
                    <TableCell class="text-right font-bold py-3 border-r border-table-border"></TableCell>
                    <TableCell class="text-right font-bold py-3 border-r border-table-border"></TableCell>
                    <!-- Forecast Totals: Last Year, Budget, Actual, (ratios blank) -->
                    <TableCell class="text-right font-bold py-3">{{ formatCurrency(directRevenueTotal.forecast?.lastYear || 0) }}</TableCell>
                    <TableCell class="text-right font-bold py-3">{{ formatCurrency(directRevenueTotal.forecast?.budget || 0) }}</TableCell>
                    <TableCell class="text-right font-bold py-3">{{ formatCurrency(directRevenueTotal.forecast?.actual || 0) }}</TableCell>
                    <TableCell class="text-right font-bold py-3"></TableCell>
                    <TableCell class="text-right font-bold py-3"></TableCell>
                    <!-- Monthly placeholder cells -->
                    <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`mtotal-${midx}`" class="text-right font-bold py-3">
                      {{ formatCurrency(getMonthlyTotalValue({ rows: directRevenueData }, midx)) }}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <!-- Cost of Sales Table -->
        <Card class="bg-gradient-card shadow-dashboard-lg border-table-border mt-8">
          <CardHeader class="flex items-center justify-between px-4 py-2">
            <div class="flex items-center space-x-3">
              <Button 
                variant="ghost" 
                size="sm"
                @click="minimizeCostOfSales = !minimizeCostOfSales"
                class="p-1"
              >
                {{ minimizeCostOfSales ? '▶' : '▼' }}
              </Button>
              <CardTitle class="text-dashboard-header font-bold text-lg">Direct Expenses (Cost of Sales)</CardTitle>
              <div class="text-sm text-muted-foreground ml-2">
                All direct costs including cost of sales (Food, Beverage, Room, and other operational costs)
              </div>
            </div>
          </CardHeader>
          <CardContent class="p-0" v-if="!minimizeCostOfSales">
            <div class="overflow-x-auto">
              <Table>
                <TableHeader class="bg-table-header">
                  <TableRow class="border-table-border">
                    <TableHead class="w-auto min-w-[200px] max-w-[800px] border-r border-table-border sticky left-0 bg-table-header z-10 whitespace-nowrap">
                      Account
                    </TableHead>
                    <!-- Period Sections -->
                    <TableHead colspan="5" class="text-center border-r border-table-border bg-red-500/5">
                      <div class="text-dashboard-header font-semibold">Current Month</div>
                    </TableHead>
                    <TableHead colspan="5" class="text-center border-r border-table-border bg-red-500/5">
                      <div class="text-dashboard-header font-semibold">Year to Date</div>
                    </TableHead>
                    <TableHead colspan="5" class="text-center bg-red-500/5">
                      <div class="text-dashboard-header font-semibold">Forecast</div>
                    </TableHead>
                    <!-- Monthly subheaders -->
                    <TableHead v-for="(m, midx) in MONTHLY_COLUMNS" :key="`cos-msh-${midx}`" class="text-center text-dashboard-subheader py-1">
                      <div class="text-xs">{{ m }}</div>
                    </TableHead>
                  </TableRow>
                  <TableRow class="border-table-border">
                    <TableHead class="border-r border-table-border sticky left-0 bg-table-header z-10"></TableHead>
                    <!-- Subheaders for each period -->
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`cm-${idx}`" 
                      class="text-center border-r border-table-border text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`ytd-${idx}`" 
                      class="text-center border-r border-table-border text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`fc-${idx}`" 
                      class="text-center text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <!-- Monthly subheaders with Actual/Budget values -->
                    <TableHead v-for="(m, midx) in MONTHLY_COLUMNS" :key="`cos-sub-${midx}`" class="text-center text-dashboard-subheader py-1">
                      <div class="text-xs">{{ getMonthlySubheaderValue(midx) }}</div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <!-- Group by report_class -->
                  <template v-for="(group, gIdx) in groupByReportClass(costOfSalesData)" :key="`cos-group-${gIdx}`">
                    <!-- Subheader row for each report_class group -->
                    <TableRow class="bg-orange-500/10 font-medium">
                      <TableCell class="font-semibold text-orange-700 border-r border-table-border sticky left-0 z-10" :style="{ paddingLeft: '20px' }">
                        {{ group.report_class }}
                      </TableCell>
                      <!-- Current Month totals -->
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.totals.currentMonth.actual / group.totals.currentMonth.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.totals.currentMonth.actual / group.totals.currentMonth.lastYear) }}</TableCell>
                      <!-- Year to Date totals -->
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.totals.yearToDate.actual / group.totals.yearToDate.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.totals.yearToDate.actual / group.totals.yearToDate.lastYear) }}</TableCell>
                      <!-- Forecast totals -->
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.budget) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.actual) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatPercentage(group.totals.forecast.actual / group.totals.forecast.budget) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatPercentage(group.totals.forecast.actual / group.totals.forecast.lastYear) }}</TableCell>
                      <!-- Monthly placeholder cells -->
                      <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`mrow-total-${gIdx}-${midx}`" class="text-right py-1">
                        {{ formatCurrency(getMonthlyTotalValue(group, midx)) }}
                      </TableCell>
                    </TableRow>
                    <!-- Individual account rows -->
                    <TableRow v-for="row in group.rows" :key="`cos-${row.account}`" v-show="!globalHideZeroRows || hasData(row)">
                      <TableCell class="py-2 border-r border-table-border" :style="{ paddingLeft: '40px' }">
                        {{ row.account_name || row.account }}
                      </TableCell>
                      <!-- Current Month -->
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(row.currentMonth?.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(row.currentMonth?.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(row.currentMonth?.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(row.currentMonth?.actBudThisYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(row.currentMonth?.actVsLastYear) }}</TableCell>
                      <!-- Year to Date -->
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(row.yearToDate?.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(row.yearToDate?.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(row.yearToDate?.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(row.yearToDate?.actBudThisYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(row.yearToDate?.actVsLastYear) }}</TableCell>
                      <!-- Forecast -->
                      <TableCell class="text-right py-1">{{ formatCurrency(row.forecast?.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(row.forecast?.budget) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(row.forecast?.actual) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatPercentage(row.forecast?.actBudThisYear) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatPercentage(row.forecast?.actVsLastYear) }}</TableCell>
                      <!-- Monthly cells -->
                      <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`cos-mrow-${row.account || row.account_name}-${midx}`" class="text-right py-1">
                        {{ formatCurrency(getMonthlyCellValue(row, midx)) }}
                      </TableCell>
                    </TableRow>
                  </template>
                  <!-- Grand Total Row -->
                  <TableRow class="border-t-2 border-orange-500 bg-orange-500/5 font-bold">
                    <TableCell class="font-bold py-3 border-r border-table-border">TOTAL COST OF SALES</TableCell>
                    <!-- Current Month total -->
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(costOfSalesTotal.currentMonth.lastYear) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(costOfSalesTotal.currentMonth.budget) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(costOfSalesTotal.currentMonth.actual) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(costOfSalesTotal.currentMonth.actual / costOfSalesTotal.currentMonth.budget) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(costOfSalesTotal.currentMonth.actual / costOfSalesTotal.currentMonth.lastYear) }}</TableCell>
                    <!-- Year to Date total -->
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(costOfSalesTotal.yearToDate.lastYear) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(costOfSalesTotal.yearToDate.budget) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(costOfSalesTotal.yearToDate.actual) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(costOfSalesTotal.yearToDate.actual / costOfSalesTotal.yearToDate.budget) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(costOfSalesTotal.yearToDate.actual / costOfSalesTotal.yearToDate.lastYear) }}</TableCell>
                    <!-- Forecast total -->
                    <TableCell class="text-right py-1">{{ formatCurrency(costOfSalesTotal.forecast.lastYear) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatCurrency(costOfSalesTotal.forecast.budget) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatCurrency(costOfSalesTotal.forecast.actual) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatPercentage(costOfSalesTotal.forecast.actual / costOfSalesTotal.forecast.budget) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatPercentage(costOfSalesTotal.forecast.actual / costOfSalesTotal.forecast.lastYear) }}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <!-- Gross Profit Table -->
        <Card class="bg-gradient-card shadow-dashboard-lg border-table-border mt-8">
          <CardHeader class="flex items-center justify-between px-4 py-2">
            <div class="flex items-center space-x-3">
              <Button 
                variant="ghost" 
                size="sm"
                @click="minimizeGrossProfit = !minimizeGrossProfit"
                class="p-1"
              >
                {{ minimizeGrossProfit ? '▶' : '▼' }}
              </Button>
              <CardTitle class="text-dashboard-header font-bold text-lg">Gross Profit</CardTitle>
              <div class="text-sm text-muted-foreground ml-2">
                Direct Revenue minus Cost of Sales
              </div>
            </div>
          </CardHeader>
          <CardContent class="p-0" v-if="!minimizeGrossProfit">
            <div class="overflow-x-auto">
              <Table>
                <TableHeader class="bg-table-header">
                  <TableRow class="border-table-border">
                    <TableHead class="w-auto min-w-[200px] max-w-[800px] border-r border-table-border sticky left-0 bg-table-header z-10 whitespace-nowrap">
                      Account
                    </TableHead>
                    <!-- Period Sections -->
                    <TableHead colspan="5" class="text-center border-r border-table-border bg-green-500/5">
                      <div class="text-dashboard-header font-semibold">Current Month</div>
                    </TableHead>
                    <TableHead colspan="5" class="text-center border-r border-table-border bg-green-500/5">
                      <div class="text-dashboard-header font-semibold">Year to Date</div>
                    </TableHead>
                    <TableHead colspan="5" class="text-center bg-green-500/5">
                      <div class="text-dashboard-header font-semibold">Forecast</div>
                    </TableHead>
                    <!-- Monthly subheaders -->
                    <TableHead v-for="(m, midx) in MONTHLY_COLUMNS" :key="`gp-msh-${midx}`" class="text-center text-dashboard-subheader py-1">
                      <div class="text-xs">{{ m }}</div>
                    </TableHead>
                  </TableRow>
                  <TableRow class="border-table-border">
                    <TableHead class="border-r border-table-border sticky left-0 bg-table-header z-10"></TableHead>
                    <!-- Subheaders for each period -->
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`cm-${idx}`" 
                      class="text-center border-r border-table-border text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`ytd-${idx}`" 
                      class="text-center border-table-border text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`fc-${idx}`" 
                      class="text-center text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <!-- Monthly subheaders with Actual/Budget values -->
                    <TableHead v-for="(m, midx) in MONTHLY_COLUMNS" :key="`gp-sub-${midx}`" class="text-center text-dashboard-subheader py-1">
                      <div class="text-xs">{{ getMonthlySubheaderValue(midx) }}</div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <!-- Gross Profit by Report Class -->
                  <template v-for="(group, gIdx) in grossProfitByReportClass" :key="`gp-group-${gIdx}`">
                    <!-- Report Class Header -->
                    <TableRow class="bg-green-500/10 font-medium">
                      <TableCell class="font-semibold text-green-700 border-r border-table-border sticky left-0 z-10" :style="{ paddingLeft: '20px' }">
                        {{ group.report_class }}
                      </TableCell>
                      <!-- Blank cells to span columns for header row -->
                      <TableCell class="py-1" colspan="15"></TableCell>
                    </TableRow>

                    <!-- Direct Revenue Totals Row -->
                    <TableRow class="hover:bg-green-50">
                      <TableCell class="py-2 border-r border-table-border" :style="{ paddingLeft: '40px' }">
                        Direct Revenue (Totals)
                    </TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.directTotals.currentMonth.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.directTotals.currentMonth.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.directTotals.currentMonth.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.directTotals.currentMonth.actual / group.directTotals.currentMonth.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.directTotals.currentMonth.actual / group.directTotals.currentMonth.lastYear) }}</TableCell>

                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.directTotals.yearToDate.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.directTotals.yearToDate.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.directTotals.yearToDate.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.directTotals.yearToDate.actual / group.directTotals.yearToDate.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.directTotals.yearToDate.actual / group.directTotals.yearToDate.lastYear) }}</TableCell>

                      <TableCell class="text-right py-1">{{ formatCurrency(group.directTotals.forecast.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.directTotals.forecast.budget) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.directTotals.forecast.actual) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatPercentage(group.directTotals.forecast.actual / group.directTotals.forecast.budget) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatPercentage(group.directTotals.forecast.actual / group.directTotals.forecast.lastYear) }}</TableCell>
                      <!-- Monthly totals for Direct Revenue -->
                      <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`gp-dir-mrow-total-${gIdx}-${midx}`" class="text-right py-1">
                        {{ formatCurrency(sumMonthlyRows(group.directRows, midx)) }}
                      </TableCell>
                    </TableRow>

                    <!-- Cost of Sales Totals Row -->
                    <TableRow class="hover:bg-orange-50">
                      <TableCell class="py-2 border-r border-table-border" :style="{ paddingLeft: '40px' }">
                        Cost of Sales (Totals)
                    </TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.costTotals.currentMonth.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.costTotals.currentMonth.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.costTotals.currentMonth.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.costTotals.currentMonth.actual / group.costTotals.currentMonth.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.costTotals.currentMonth.actual / group.costTotals.currentMonth.lastYear) }}</TableCell>

                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.costTotals.yearToDate.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.costTotals.yearToDate.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.costTotals.yearToDate.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.costTotals.yearToDate.actual / group.costTotals.yearToDate.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.costTotals.yearToDate.actual / group.costTotals.yearToDate.lastYear) }}</TableCell>

                      <TableCell class="text-right py-1">{{ formatCurrency(group.costTotals.forecast.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.costTotals.forecast.budget) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.costTotals.forecast.actual) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatPercentage(group.costTotals.forecast.actual / group.costTotals.forecast.budget) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatPercentage(group.costTotals.forecast.actual / group.costTotals.forecast.lastYear) }}</TableCell>
                      <!-- Monthly totals for Cost of Sales -->
                      <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`gp-cost-mrow-total-${gIdx}-${midx}`" class="text-right py-1">
                        {{ formatCurrency(sumMonthlyRows(group.costRows, midx)) }}
                      </TableCell>
                    </TableRow>

                    <!-- Gross Profit Row -->
                    <TableRow class="border-t bg-green-500/5 font-medium">
                      <TableCell class="font-semibold py-2 border-r border-table-border" :style="{ paddingLeft: '40px' }">
                        Gross Profit (Revenue - Cost)
                    </TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.grossTotals.currentMonth.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.grossTotals.currentMonth.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.grossTotals.currentMonth.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.grossTotals.currentMonth.actual / group.directTotals.currentMonth.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.grossTotals.currentMonth.actual / group.directTotals.currentMonth.lastYear) }}</TableCell>

                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.grossTotals.yearToDate.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.grossTotals.yearToDate.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.grossTotals.yearToDate.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.grossTotals.yearToDate.actual / group.directTotals.yearToDate.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(group.grossTotals.yearToDate.actual / group.directTotals.yearToDate.lastYear) }}</TableCell>

                      <TableCell class="text-right py-1">{{ formatCurrency(group.grossTotals.forecast.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.grossTotals.forecast.budget) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.grossTotals.forecast.actual) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatPercentage(group.grossTotals.forecast.actual / group.directTotals.forecast.budget) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatPercentage(group.grossTotals.forecast.actual / group.directTotals.forecast.lastYear) }}</TableCell>
                      <!-- Monthly Gross Profit = Direct - Cost -->
                      <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`gp-gross-mrow-total-${gIdx}-${midx}`" class="text-right py-1">
                        {{ formatCurrency(getMonthlyGrossValue(group, midx)) }}
                      </TableCell>
                    </TableRow>
                  </template>
                  
                  <!-- Grand Total Row -->
                  <TableRow class="border-t-2 border-green-500 bg-green-500/5 font-bold">
                    <TableCell class="font-bold py-3 border-r border-table-border">TOTAL GROSS PROFIT</TableCell>
                    <!-- Current Month -->
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(grossProfitTotal.currentMonth.lastYear) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(grossProfitTotal.currentMonth.budget) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(grossProfitTotal.currentMonth.actual) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(grossProfitTotal.currentMonth.actual / grossProfitTotal.currentMonth.budget) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(grossProfitTotal.currentMonth.actual / grossProfitTotal.currentMonth.lastYear) }}</TableCell>
                    <!-- Year to Date -->
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(grossProfitTotal.yearToDate.lastYear) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(grossProfitTotal.yearToDate.budget) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(grossProfitTotal.yearToDate.actual) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(grossProfitTotal.yearToDate.actual / grossProfitTotal.yearToDate.budget) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatPercentage(grossProfitTotal.yearToDate.actual / grossProfitTotal.yearToDate.lastYear) }}</TableCell>
                    <!-- Forecast -->
                    <TableCell class="text-right py-1">{{ formatCurrency(grossProfitTotal.forecast.lastYear) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatCurrency(grossProfitTotal.forecast.budget) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatCurrency(grossProfitTotal.forecast.actual) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatPercentage(grossProfitTotal.forecast.actual / grossProfitTotal.forecast.budget) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatPercentage(grossProfitTotal.forecast.actual / grossProfitTotal.forecast.lastYear) }}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <!-- Salaries & Wages Table -->
        <Card class="bg-gradient-card shadow-dashboard-lg border-table-border mt-8">
          <CardHeader class="flex items-center justify-between px-4 py-2">
            <div class="flex items-center space-x-3">
              <Button 
                variant="ghost" 
                size="sm"
                @click="minimizeSalariesWages = !minimizeSalariesWages"
                class="p-1"
              >
                {{ minimizeSalariesWages ? '▶' : '▼' }}
              </Button>
              <CardTitle class="text-dashboard-header font-bold text-lg">Salaries & Wages</CardTitle>
              <div class="text-sm text-muted-foreground ml-2">
                Employee compensation, benefits, and payroll expenses.
              </div>
            </div>
          </CardHeader>
          <CardContent class="p-0" v-if="!minimizeSalariesWages">
            <div class="overflow-x-auto">
              <Table>
                <TableHeader class="bg-table-header">
                  <TableRow class="border-table-border">
                    <TableHead class="w-auto min-w-[200px] max-w-[800px] border-r border-table-border sticky left-0 bg-table-header z-10 whitespace-nowrap">
                      Account
                    </TableHead>
                    <!-- Period Sections -->
                    <TableHead colspan="5" class="text-center border-r border-table-border bg-blue-500/5">
                      <div class="text-dashboard-header font-semibold">Current Month</div>
                    </TableHead>
                    <TableHead colspan="5" class="text-center border-r border-table-border bg-blue-500/5">
                      <div class="text-dashboard-header font-semibold">Year to Date</div>
                    </TableHead>
                    <TableHead colspan="5" class="text-center bg-blue-500/5">
                      <div class="text-dashboard-header font-semibold">Forecast</div>
                    </TableHead>
                    <!-- Monthly subheaders -->
                    <TableHead v-for="(m, midx) in MONTHLY_COLUMNS" :key="`sw-msh-${midx}`" class="text-center text-dashboard-subheader py-1">
                      <div class="text-xs">{{ m }}</div>
                    </TableHead>
                  </TableRow>
                  <TableRow class="border-table-border">
                    <TableHead class="border-r border-table-border sticky left-0 bg-table-header z-10"></TableHead>
                    <!-- Subheaders for each period -->
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`cm-${idx}`" 
                      class="text-center border-r border-table-border text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`ytd-${idx}`" 
                      class="text-center border-r border-table-border text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`fc-${idx}`" 
                      class="text-center text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <!-- Monthly subheaders with Actual/Budget values -->
                    <TableHead v-for="(m, midx) in MONTHLY_COLUMNS" :key="`sw-sub-${midx}`" class="text-center text-dashboard-subheader py-1">
                      <div class="text-xs">{{ getMonthlySubheaderValue(midx) }}</div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <!-- Group by report_class with a subheader and totals -->
                  <template v-for="(group, gIdx) in groupByReportClass(salariesWagesData)" :key="`sw-group-${gIdx}`">
                    <!-- Sub-header row for report_class -->
                    <TableRow class="bg-blue-500/10 font-medium">
                      <TableCell class="font-semibold text-blue-700 border-r border-table-border sticky left-0 z-10" :style="{ paddingLeft: '20px' }">
                        {{ group.report_class || 'Other' }}
                      </TableCell>
                      <!-- Current Month totals: Last Year, Budget, Actual, (ratios blank) -->
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <!-- Year to Date totals: Last Year, Budget, Actual, (ratios blank) -->
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <!-- Forecast totals: Last Year, Budget, Actual, (ratios blank) -->
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.budget) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.actual) }}</TableCell>
                      <TableCell class="text-right py-1"></TableCell>
                      <TableCell class="text-right py-1"></TableCell>
                      <!-- Monthly placeholder cells -->
                      <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`sw-mrow-total-${gIdx}-${midx}`" class="text-right py-1">
                        {{ formatCurrency(getMonthlyTotalValue(group, midx)) }}
                      </TableCell>
                    </TableRow>

                    <!-- Account rows under this report_class -->
                    <template v-for="row in group.rows" :key="row.account || row.account_name">
                    <TableRow 
                      v-if="!globalHideZeroRows || hasData(row)"
                      class="hover:bg-blue-50"
                    >
                        <TableCell class="py-2 border-r border-table-border" :style="{ paddingLeft: '40px' }">
                        {{ row.account_name || row.account }}
                      </TableCell>
                        <!-- Current Month (5 subcolumns) -->
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.currentMonth?.lastYear || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.currentMonth?.budget || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.currentMonth?.actual || 0) }}</TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.currentMonth?.actBudThisYear)" class="block text-right">
                            {{ typeof row.currentMonth?.actBudThisYear === 'string' ? row.currentMonth?.actBudThisYear : formatPercentage(row.currentMonth?.actBudThisYear) }}
                          </span>
                      </TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.currentMonth?.actVsLastYear)" class="block text-right">
                            {{ typeof row.currentMonth?.actVsLastYear === 'string' ? row.currentMonth?.actVsLastYear : formatPercentage(row.currentMonth?.actVsLastYear) }}
                          </span>
                      </TableCell>
                        <!-- Year to Date (5 subcolumns) -->
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.yearToDate?.lastYear || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.yearToDate?.budget || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.yearToDate?.actual || 0) }}</TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.yearToDate?.actBudThisYear)" class="block text-right">
                            {{ typeof row.yearToDate?.actBudThisYear === 'string' ? row.yearToDate?.actBudThisYear : formatPercentage(row.yearToDate?.actBudThisYear) }}
                          </span>
                      </TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.yearToDate?.actVsLastYear)" class="block text-right">
                            {{ typeof row.yearToDate?.actVsLastYear === 'string' ? row.yearToDate?.actVsLastYear : formatPercentage(row.yearToDate?.actVsLastYear) }}
                          </span>
                        </TableCell>
                        <!-- Forecast (5 subcolumns) -->
                        <TableCell class="text-right py-2">{{ formatCurrency(row.forecast?.lastYear || 0) }}</TableCell>
                        <TableCell class="text-right py-2">{{ formatCurrency(row.forecast?.budget || 0) }}</TableCell>
                        <TableCell class="text-right py-2">{{ formatCurrency(row.forecast?.actual || 0) }}</TableCell>
                      <TableCell class="text-right py-2">
                          <span :class="getPercentageClass(row.forecast?.actBudThisYear)" class="block text-right">
                            {{ typeof row.forecast?.actBudThisYear === 'string' ? row.forecast?.actBudThisYear : formatPercentage(row.forecast?.actBudThisYear) }}
                          </span>
                      </TableCell>
                      <TableCell class="text-right py-2">
                          <span :class="getPercentageClass(row.forecast?.actVsLastYear)" class="block text-right">
                            {{ typeof row.forecast?.actVsLastYear === 'string' ? row.forecast?.actVsLastYear : formatPercentage(row.forecast?.actVsLastYear) }}
                          </span>
                      </TableCell>
                      <!-- Monthly placeholder cells -->
                      <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`sw-mrow-${row.account || row.account_name}-${midx}`" class="text-right py-2">
                        {{ formatCurrency(getMonthlyCellValue(row, midx)) }}
                      </TableCell>
                    </TableRow>
                  </template>
                  </template>
                  <!-- Salaries & Wages Total -->
                  <TableRow class="border-t-2 border-blue-500 bg-blue-500/5 font-bold">
                    <TableCell class="font-bold py-3 border-r border-table-border">TOTAL SALARIES & WAGES</TableCell>
                    <!-- Current Month -->
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(salariesWagesTotal.currentMonth.lastYear) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(salariesWagesTotal.currentMonth.budget) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(salariesWagesTotal.currentMonth.actual) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                    <!-- Year to Date -->
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(salariesWagesTotal.yearToDate.lastYear) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(salariesWagesTotal.yearToDate.budget) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(salariesWagesTotal.yearToDate.actual) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                    <!-- Forecast -->
                    <TableCell class="text-right py-1">{{ formatCurrency(salariesWagesTotal.forecast.lastYear) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatCurrency(salariesWagesTotal.forecast.budget) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatCurrency(salariesWagesTotal.forecast.actual) }}</TableCell>
                    <TableCell class="text-right py-1"></TableCell>
                    <TableCell class="text-right py-1"></TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <!-- Payroll Burden Table -->
        <Card class="bg-gradient-card shadow-dashboard-lg border-table-border mt-8">
          <CardHeader class="flex items-center justify-between px-4 py-2">
            <div class="flex items-center space-x-3">
              <Button 
                variant="ghost" 
                size="sm"
                @click="minimizePayrollBurden = !minimizePayrollBurden"
                class="p-1"
              >
                {{ minimizePayrollBurden ? '▶' : '▼' }}
              </Button>
              <CardTitle class="text-dashboard-header font-bold text-lg">Payroll Burden</CardTitle>
              <div class="text-sm text-muted-foreground ml-2">
                Employer statutory costs: social security, pensions, taxes, benefits
              </div>
            </div>
          </CardHeader>
          <CardContent class="p-0" v-if="!minimizePayrollBurden">
            <div class="overflow-x-auto">
              <Table>
                <TableHeader class="bg-table-header">
                  <TableRow class="border-table-border">
                    <TableHead class="w-auto min-w-[200px] max-w-[800px] border-r border-table-border sticky left-0 bg-table-header z-10 whitespace-nowrap">
                      Account
                    </TableHead>
                    <!-- Period Sections -->
                    <TableHead colspan="5" class="text-center border-r border-table-border bg-purple-500/5">
                      <div class="text-dashboard-header font-semibold">Current Month</div>
                    </TableHead>
                    <TableHead colspan="5" class="text-center border-r border-table-border bg-purple-500/5">
                      <div class="text-dashboard-header font-semibold">Year to Date</div>
                    </TableHead>
                    <TableHead colspan="5" class="text-center bg-purple-500/5">
                      <div class="text-dashboard-header font-semibold">Forecast</div>
                    </TableHead>
                    <!-- Monthly subheaders -->
                    <TableHead v-for="(m, midx) in MONTHLY_COLUMNS" :key="`bur-msh-${midx}`" class="text-center text-dashboard-subheader py-1">
                      <div class="text-xs">{{ m }}</div>
                    </TableHead>
                  </TableRow>
                  <TableRow class="border-table-border">
                    <TableHead class="border-r border-table-border sticky left-0 bg-table-header z-10"></TableHead>
                    <!-- Subheaders for each period -->
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`bur-cm-${idx}`" 
                      class="text-center border-r border-table-border text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`bur-ytd-${idx}`" 
                      class="text-center border-r border-table-border text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`bur-fc-${idx}`" 
                      class="text-center text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <!-- Monthly subheaders with Actual/Budget values -->
                    <TableHead v-for="(m, midx) in MONTHLY_COLUMNS" :key="`bur-sub-${midx}`" class="text-center text-dashboard-subheader py-1">
                      <div class="text-xs">{{ getMonthlySubheaderValue(midx) }}</div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <!-- Group by report_class -->
                  <template v-for="(group, gIdx) in groupByReportClass(payrollBurdenData)" :key="`bur-group-${gIdx}`">
                    <!-- Subheader row for each report_class group -->
                    <TableRow class="bg-purple-500/10 font-medium">
                      <TableCell class="font-semibold text-purple-700 border-r border-table-border sticky left-0 z-10" :style="{ paddingLeft: '20px' }">
                        {{ group.report_class || 'Payroll Burden' }}
                    </TableCell>
                      <!-- Current Month totals -->
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <!-- Year to Date totals -->
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <!-- Forecast totals -->
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.budget) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.actual) }}</TableCell>
                      <TableCell class="text-right py-1"></TableCell>
                      <TableCell class="text-right py-1"></TableCell>
                      <!-- Monthly placeholder cells -->
                      <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`bur-mrow-total-${gIdx}-${midx}`" class="text-right py-1">
                        {{ formatCurrency(getMonthlyTotalValue(group, midx)) }}
                    </TableCell>
                    </TableRow>
                    
                    <!-- Individual account rows -->
                    <TableRow v-for="row in group.rows" :key="`bur-${row.account}`" class="hover:bg-purple-50" v-show="!globalHideZeroRows || hasData(row)">
                      <TableCell class="py-2 border-r border-table-border" :style="{ paddingLeft: '40px' }">
                        {{ row.account_name || row.account }}
                    </TableCell>
                      <!-- Current Month -->
                      <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.currentMonth?.lastYear || 0) }}</TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.currentMonth?.budget || 0) }}</TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.currentMonth?.actual || 0) }}</TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.currentMonth?.actBudThisYear)" class="block text-right">
                            {{ typeof row.currentMonth?.actBudThisYear === 'string' ? row.currentMonth?.actBudThisYear : formatPercentage(row.currentMonth?.actBudThisYear) }}
                          </span>
                    </TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.currentMonth?.actVsLastYear)" class="block text-right">
                            {{ typeof row.currentMonth?.actVsLastYear === 'string' ? row.currentMonth?.actVsLastYear : formatPercentage(row.currentMonth?.actVsLastYear) }}
                          </span>
                      </TableCell>
                        <!-- Year to Date (5 subcolumns) -->
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.yearToDate?.lastYear || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.yearToDate?.budget || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.yearToDate?.actual || 0) }}</TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.yearToDate?.actBudThisYear)" class="block text-right">
                            {{ typeof row.yearToDate?.actBudThisYear === 'string' ? row.yearToDate?.actBudThisYear : formatPercentage(row.yearToDate?.actBudThisYear) }}
                          </span>
                      </TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.yearToDate?.actVsLastYear)" class="block text-right">
                            {{ typeof row.yearToDate?.actVsLastYear === 'string' ? row.yearToDate?.actVsLastYear : formatPercentage(row.yearToDate?.actVsLastYear) }}
                          </span>
                        </TableCell>
                        <!-- Forecast (5 subcolumns) -->
                        <TableCell class="text-right py-2">{{ formatCurrency(row.forecast?.lastYear || 0) }}</TableCell>
                        <TableCell class="text-right py-2">{{ formatCurrency(row.forecast?.budget || 0) }}</TableCell>
                        <TableCell class="text-right py-2">{{ formatCurrency(row.forecast?.actual || 0) }}</TableCell>
                      <TableCell class="text-right py-2">
                          <span :class="getPercentageClass(row.forecast?.actBudThisYear)" class="block text-right">
                            {{ typeof row.forecast?.actBudThisYear === 'string' ? row.forecast?.actBudThisYear : formatPercentage(row.forecast?.actBudThisYear) }}
                          </span>
                      </TableCell>
                      <TableCell class="text-right py-2">
                          <span :class="getPercentageClass(row.forecast?.actVsLastYear)" class="block text-right">
                            {{ typeof row.forecast?.actVsLastYear === 'string' ? row.forecast?.actVsLastYear : formatPercentage(row.forecast?.actVsLastYear) }}
                          </span>
                    </TableCell>
                      <!-- Monthly placeholder cells -->
                      <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`bur-mrow-${row.account || row.account_name}-${midx}`" class="text-right py-2">
                        {{ formatCurrency(getMonthlyCellValue(row, midx)) }}
                      </TableCell>
                    </TableRow>
                  </template>
                  
                  <!-- Grand Total Row -->
                  <TableRow class="bg-purple-500/5 border-purple-500 font-bold border-t-2">
                    <TableCell class="font-bold py-3 border-r border-table-border">TOTAL PAYROLL BURDEN</TableCell>
                    <!-- Current Month total -->
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(payrollBurdenTotal?.currentMonth?.lastYear || 0) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(payrollBurdenTotal?.currentMonth?.budget || 0) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(payrollBurdenTotal?.currentMonth?.actual || 0) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                    <!-- Year to Date total -->
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(payrollBurdenTotal?.yearToDate?.lastYear || 0) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(payrollBurdenTotal?.yearToDate?.budget || 0) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(payrollBurdenTotal?.yearToDate?.actual || 0) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                    <!-- Forecast total -->
                    <TableCell class="text-right py-1">{{ formatCurrency(payrollBurdenTotal?.forecast?.lastYear || 0) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatCurrency(payrollBurdenTotal?.forecast?.budget || 0) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatCurrency(payrollBurdenTotal?.forecast?.actual || 0) }}</TableCell>
                    <TableCell class="text-right py-1"></TableCell>
                    <TableCell class="text-right py-1"></TableCell>
                    <!-- Monthly placeholder cells -->
                    <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`bur-mtotal-${midx}`" class="text-right py-1">
                      {{ formatCurrency(getMonthlyTotalValue(payrollBurdenTotal, midx)) }}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <!-- Indirect Expenses Table -->
        <Card class="bg-gradient-card shadow-dashboard-lg border-table-border mt-8">
          <CardHeader class="flex items-center justify-between px-4 py-2">
            <div class="flex items-center space-x-3">
              <Button 
                variant="ghost" 
                size="sm"
                @click="minimizeIndirectExpenses = !minimizeIndirectExpenses"
                class="p-1"
              >
                {{ minimizeIndirectExpenses ? '▶' : '▼' }}
              </Button>
              <CardTitle class="text-dashboard-header font-bold text-lg">Indirect Expenses</CardTitle>
              <div class="text-sm text-muted-foreground ml-2">
                Administrative, overhead, and other indirect costs
              </div>
            </div>
          </CardHeader>
          <CardContent class="p-0" v-if="!minimizeIndirectExpenses">
            <div class="overflow-x-auto">
              <Table>
                <TableHeader class="bg-table-header">
                  <TableRow class="border-table-border">
                    <TableHead class="w-auto min-w-[200px] max-w-[800px] border-r border-table-border sticky left-0 bg-table-header z-10 whitespace-nowrap">
                      Account
                    </TableHead>
                    <!-- Period Sections -->
                    <TableHead colspan="5" class="text-center border-r border-table-border bg-indigo-500/5">
                      <div class="text-dashboard-header font-semibold">Current Month</div>
                    </TableHead>
                    <TableHead colspan="5" class="text-center border-r border-table-border bg-indigo-500/5">
                      <div class="text-dashboard-header font-semibold">Year to Date</div>
                    </TableHead>
                    <TableHead colspan="5" class="text-center bg-indigo-500/5">
                      <div class="text-dashboard-header font-semibold">Forecast</div>
                    </TableHead>
                    <!-- Monthly subheaders -->
                    <TableHead v-for="(m, midx) in MONTHLY_COLUMNS" :key="`ie-msh-${midx}`" class="text-center text-dashboard-subheader py-1">
                      <div class="text-xs">{{ m }}</div>
                    </TableHead>
                  </TableRow>
                  <TableRow class="border-table-border">
                    <TableHead class="border-r border-table-border sticky left-0 bg-table-header z-10"></TableHead>
                    <!-- Subheaders for each period -->
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`ie-cm-${idx}`" 
                      class="text-center border-r border-table-border text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`ie-ytd-${idx}`" 
                      class="text-center border-r border-table-border text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <TableHead 
                      v-for="(header, idx) in ['Last Year', 'Budget', 'Actual', 'Act/Bud This Year', 'Act/Last Year']" 
                      :key="`ie-fc-${idx}`" 
                      class="text-center text-dashboard-subheader py-1"
                    >
                      <div class="text-xs">{{ header }}</div>
                    </TableHead>
                    <!-- Monthly subheaders with Actual/Budget values -->
                    <TableHead v-for="(m, midx) in MONTHLY_COLUMNS" :key="`ie-sub-${midx}`" class="text-center text-dashboard-subheader py-1">
                      <div class="text-xs">{{ getMonthlySubheaderValue(midx) }}</div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <!-- Group by report_class -->
                  <template v-for="(group, gIdx) in groupByReportClass(indirectExpensesData)" :key="`ie-group-${gIdx}`">
                    <!-- Sub-header row for report_class -->
                    <TableRow class="bg-indigo-500/10 font-medium">
                      <TableCell class="font-semibold text-indigo-700 border-r border-table-border sticky left-0 z-10" :style="{ paddingLeft: '20px' }">
                        {{ group.report_class || 'Other' }}
                      </TableCell>
                      <!-- Current Month totals: Last Year, Budget, Actual, (ratios blank) -->
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.currentMonth.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <!-- Year to Date totals: Last Year, Budget, Actual, (ratios blank) -->
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.budget) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(group.totals.yearToDate.actual) }}</TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                      <!-- Forecast totals: Last Year, Budget, Actual, (ratios blank) -->
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.lastYear) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.budget) }}</TableCell>
                      <TableCell class="text-right py-1">{{ formatCurrency(group.totals.forecast.actual) }}</TableCell>
                      <TableCell class="text-right py-1"></TableCell>
                      <TableCell class="text-right py-1"></TableCell>
                      <!-- Monthly placeholder cells -->
                      <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`ie-mrow-total-${gIdx}-${midx}`" class="text-right py-1">
                        {{ formatCurrency(getMonthlyTotalValue(group, midx)) }}
                      </TableCell>
                    </TableRow>

                    <!-- Account rows under this report_class -->
                    <template v-for="row in group.rows" :key="row.account || row.account_name">
                    <TableRow 
                      v-if="!globalHideZeroRows || hasData(row)"
                      class="hover:bg-indigo-50"
                    >
                        <TableCell class="py-2 border-r border-table-border" :style="{ paddingLeft: '40px' }">
                        {{ row.account_name || row.account }}
                      </TableCell>
                        <!-- Current Month (5 subcolumns) -->
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.currentMonth?.lastYear || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.currentMonth?.budget || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.currentMonth?.actual || 0) }}</TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.currentMonth?.actBudThisYear)" class="block text-right">
                            {{ typeof row.currentMonth?.actBudThisYear === 'string' ? row.currentMonth?.actBudThisYear : formatPercentage(row.currentMonth?.actBudThisYear) }}
                          </span>
                      </TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.currentMonth?.actVsLastYear)" class="block text-right">
                            {{ typeof row.currentMonth?.actVsLastYear === 'string' ? row.currentMonth?.actVsLastYear : formatPercentage(row.currentMonth?.actVsLastYear) }}
                          </span>
                      </TableCell>
                        <!-- Year to Date (5 subcolumns) -->
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.yearToDate?.lastYear || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.yearToDate?.budget || 0) }}</TableCell>
                        <TableCell class="text-right py-2 border-r border-table-border">{{ formatCurrency(row.yearToDate?.actual || 0) }}</TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.yearToDate?.actBudThisYear)" class="block text-right">
                            {{ typeof row.yearToDate?.actBudThisYear === 'string' ? row.yearToDate?.actBudThisYear : formatPercentage(row.yearToDate?.actBudThisYear) }}
                          </span>
                      </TableCell>
                      <TableCell class="text-right py-2 border-r border-table-border">
                          <span :class="getPercentageClass(row.yearToDate?.actVsLastYear)" class="block text-right">
                            {{ typeof row.yearToDate?.actVsLastYear === 'string' ? row.yearToDate?.actVsLastYear : formatPercentage(row.yearToDate?.actVsLastYear) }}
                          </span>
                        </TableCell>
                        <!-- Forecast (5 subcolumns) -->
                        <TableCell class="text-right py-2">{{ formatCurrency(row.forecast?.lastYear || 0) }}</TableCell>
                        <TableCell class="text-right py-2">{{ formatCurrency(row.forecast?.budget || 0) }}</TableCell>
                        <TableCell class="text-right py-2">{{ formatCurrency(row.forecast?.actual || 0) }}</TableCell>
                      <TableCell class="text-right py-2">
                          <span :class="getPercentageClass(row.forecast?.actBudThisYear)" class="block text-right">
                            {{ typeof row.forecast?.actBudThisYear === 'string' ? row.forecast?.actBudThisYear : formatPercentage(row.forecast?.actBudThisYear) }}
                          </span>
                      </TableCell>
                      <TableCell class="text-right py-2">
                          <span :class="getPercentageClass(row.forecast?.actVsLastYear)" class="block text-right">
                            {{ typeof row.forecast?.actVsLastYear === 'string' ? row.forecast?.actVsLastYear : formatPercentage(row.forecast?.actVsLastYear) }}
                          </span>
                      </TableCell>
                      <!-- Monthly placeholder cells -->
                      <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`ie-mrow-${row.account || row.account_name}-${midx}`" class="text-right py-2">
                        {{ formatCurrency(getMonthlyCellValue(row, midx)) }}
                      </TableCell>
                    </TableRow>
                    </template>
                  </template>
                  
                  <!-- Grand Total Row -->
                  <TableRow class="border-t-2 border-indigo-500 bg-indigo-500/5 font-bold">
                    <TableCell class="font-bold py-3 border-r border-table-border">TOTAL INDIRECT EXPENSES</TableCell>
                    <!-- Current Month total -->
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(indirectExpensesTotal?.currentMonth?.lastYear || 0) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(indirectExpensesTotal?.currentMonth?.budget || 0) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(indirectExpensesTotal?.currentMonth?.actual || 0) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                    <!-- Year to Date total -->
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(indirectExpensesTotal?.yearToDate?.lastYear || 0) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(indirectExpensesTotal?.yearToDate?.budget || 0) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border">{{ formatCurrency(indirectExpensesTotal?.yearToDate?.actual || 0) }}</TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                    <TableCell class="text-right py-1 border-r border-table-border"></TableCell>
                    <!-- Forecast total -->
                    <TableCell class="text-right py-1">{{ formatCurrency(indirectExpensesTotal?.forecast?.lastYear || 0) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatCurrency(indirectExpensesTotal?.forecast?.budget || 0) }}</TableCell>
                    <TableCell class="text-right py-1">{{ formatCurrency(indirectExpensesTotal?.forecast?.actual || 0) }}</TableCell>
                    <TableCell class="text-right py-1"></TableCell>
                    <TableCell class="text-right py-1"></TableCell>
                    <!-- Monthly placeholder cells -->
                    <TableCell v-for="(m, midx) in MONTHLY_COLUMNS" :key="`ie-mtotal-${midx}`" class="text-right py-1">
                      {{ formatCurrency(getMonthlyTotalValue(indirectExpensesTotal, midx)) }}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
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
import { RefreshCw, Download, AlertCircle, BarChart3, TestTube, ChevronDown, ChevronRight } from 'lucide-vue-next'
import DashboardFilters from './DashboardFilters.vue'
import DashboardTable from './DashboardTable.vue'
import apiService from '../services/api'
import { session } from '../data/session'
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from '@/components/ui'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui'

// State
const loading = ref(false)
const error = ref(null)
const dashboardData = ref([])
const summaryData = ref({})
const currentFilters = ref({}) 
const globalHideZeroRows = ref(false) // Global hide zero rows state

// Duplicate-call guards
let filterChangeDebounce = null
const lastLoadAt = ref(0)

// Direct Revenue and Cost of Sales state
const minimizeDirectRevenue = ref(false)
const minimizeCostOfSales = ref(false)
const directRevenueData = ref([])
const directRevenueTotal = ref({})
const costOfSalesData = ref([])
const costOfSalesTotal = ref({})
const minimizeGrossProfit = ref(false)
const grossProfitTotal = ref({})

// Main Dashboard state
const minimizeMainDashboard = ref(false)

// Month labels for monthly placeholder columns - dynamically generated from fiscal year
const MONTHLY_COLUMNS = computed(() => {
  const fiscalYear = currentFilters.value?.fiscal_year || '25'
  const yearSuffix = fiscalYear.toString().slice(-2) // Get last 2 digits of year
  return [
    `Jan ${yearSuffix}`, `Feb ${yearSuffix}`, `Mar ${yearSuffix}`, `Apr ${yearSuffix}`, `May ${yearSuffix}`, `Jun ${yearSuffix}`,
    `Jul ${yearSuffix}`, `Aug ${yearSuffix}`, `Sep ${yearSuffix}`, `Oct ${yearSuffix}`, `Nov ${yearSuffix}`, `Dec ${yearSuffix}`,
    'YTD'
  ]
})

// Computed property to determine monthly subheader values based on selected month
// Logic: If April (4) is selected, then Jan-Apr show "Actual", May-Dec show "Budget"
// YTD column always shows "Forecast"
const getMonthlySubheaderValue = computed(() => {
  return (monthIndex) => {
    // monthIndex 0-11 represents Jan-Dec, monthIndex 12 is YTD
    if (monthIndex === 12) return 'Forecast' // YTD column always shows Forecast
    
    const selectedMonth = currentFilters.value?.month
    if (!selectedMonth) return 'Actual' // Default to Actual if no month selected
    
    const selectedMonthNum = parseInt(selectedMonth)
    // If selected month is 0 or invalid, default to Actual
    if (selectedMonthNum < 1 || selectedMonthNum > 12) return 'Actual'
    
    // Months 1 through selectedMonth show "Actual", rest show "Budget"
    // monthIndex is 0-based, so we need to add 1 to compare with selectedMonth
    const shouldShowActual = (monthIndex + 1) <= selectedMonthNum
    return shouldShowActual ? 'Actual' : 'Budget'
  }
})

// Salaries & Wages state
const minimizeSalariesWages = ref(false)
const salariesWagesData = ref([])
const salariesWagesTotal = ref({})

// Regex for Salaries & Wages matching (report_class only)
const SALARY_REGEX = /(salary|salaries|wage|wages)/i

// Payroll Burden state
const minimizePayrollBurden = ref(false)
const payrollBurdenData = ref([])
const payrollBurdenTotal = ref({})

// Regex for Payroll Burden matching (report_class only)
const PAYROLL_BURDEN_REGEX = /(burden|statutory|employer|social|pension|ssnit)/i

// Indirect Expenses state
const minimizeIndirectExpenses = ref(false)
const indirectExpensesData = ref([])
const indirectExpensesTotal = computed(() => apiService.calculateTotal(indirectExpensesData.value))

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

const goToTestPage = () => {
  router.push('/test')
}

const goToErpnextDashboard = () => {
  router.push('/erpnext-dashboard')
}

// Methods
const handleFiltersChange = (filters) => {
  currentFilters.value = { ...currentFilters.value, ...filters }
  // Debounce to avoid rapid repeated loads (e.g., multiple emits on mount)
  if (filterChangeDebounce) clearTimeout(filterChangeDebounce)
  filterChangeDebounce = setTimeout(() => {
  loadDashboardData()
  }, 300)
}

const handleHideZerosChange = (hideZeros) => {
  globalHideZeroRows.value = hideZeros
}

const loadDashboardData = async () => {
  // Prevent overlapping and very frequent reloads
  if (loading.value) return
  const now = Date.now()
  if (now - lastLoadAt.value < 1200) return
  lastLoadAt.value = now

  loading.value = true
  error.value = null

  try {
    // Load main dashboard data
    const dashboardResponse = await apiService.getDashboardData(currentFilters.value)
    
    if (dashboardResponse && dashboardResponse.dashboard_data) {
      dashboardData.value = dashboardResponse.dashboard_data
      summaryData.value = dashboardResponse.summary_data || {}
    } else {
      dashboardData.value = []
      summaryData.value = {}
    }

    // Load Direct Revenue and Cost of Sales data with current filters
    try {
      const directRevenueResponse = await apiService.getDirectRevenueData(currentFilters.value)
      if (directRevenueResponse && Array.isArray(directRevenueResponse) && directRevenueResponse.length > 0) {
        directRevenueData.value = directRevenueResponse
        directRevenueTotal.value = apiService.calculateTotal(directRevenueResponse)
      } else {
        // Fallback: derive from dashboardData canonical structure
        const derivedDR = (dashboardData.value || []).filter(r => r?.type === 'account' && r?.section === 'Direct Revenue')
        directRevenueData.value = derivedDR
        directRevenueTotal.value = apiService.calculateTotal(derivedDR)
      }

      const costOfSalesResponse = await apiService.getCostOfSalesData(currentFilters.value)
      if (costOfSalesResponse && Array.isArray(costOfSalesResponse) && costOfSalesResponse.length > 0) {
        costOfSalesData.value = costOfSalesResponse
        costOfSalesTotal.value = apiService.calculateTotal(costOfSalesResponse)
      } else {
        // Fallback: derive from dashboardData with improved filtering logic
        const derivedCOS = (dashboardData.value || []).filter(r => {
          if (!r || r.type !== 'account' || r.root_type !== 'Expense') return false

          const section = (r.section || '').toString()
          const accountName = (r.account_name || r.account || '').toString()
          const reportClass = (r.report_class || '').toString()

          // Primary logic: accounts in Cost of Sales section
          if (section === 'Cost of Sales') return true

          // Secondary logic: accounts with 'Cost' in name from specific report classes
          if (accountName.toLowerCase().includes('cost') &&
              (reportClass === 'Other Cost of Sales' || reportClass === 'Other Expense')) {
            return true
          }

          // Tertiary logic: original report class filtering
          if (['Food', 'Beverage', 'Room', 'Other Costs'].includes(reportClass)) {
            return true
          }

          return false
        })
        costOfSalesData.value = derivedCOS
        costOfSalesTotal.value = apiService.calculateTotal(derivedCOS)
      }

      // Calculate Gross Profit
      grossProfitTotal.value = {
        currentMonth: {
          lastYear: directRevenueTotal.value.currentMonth.lastYear - costOfSalesTotal.value.currentMonth.lastYear,
          budget: directRevenueTotal.value.currentMonth.budget - costOfSalesTotal.value.currentMonth.budget,
          actual: directRevenueTotal.value.currentMonth.actual - costOfSalesTotal.value.currentMonth.actual,
        },
        yearToDate: {
          lastYear: directRevenueTotal.value.yearToDate.lastYear - costOfSalesTotal.value.yearToDate.lastYear,
          budget: directRevenueTotal.value.yearToDate.budget - costOfSalesTotal.value.yearToDate.budget,
          actual: directRevenueTotal.value.yearToDate.actual - costOfSalesTotal.value.yearToDate.actual,
        },
        forecast: {
          lastYear: directRevenueTotal.value.forecast.lastYear - costOfSalesTotal.value.forecast.lastYear,
          budget: directRevenueTotal.value.forecast.budget - costOfSalesTotal.value.forecast.budget,
          actual: directRevenueTotal.value.forecast.actual - costOfSalesTotal.value.forecast.actual,
        }
      }

      // Derive Salaries & Wages using section field
      const salaryAccounts = (dashboardData.value || []).filter(r => {
        if (!r || r.type !== 'account' || r.root_type !== 'Expense') return false
        const section = (r.section || '').toString()
        return section === 'Salaries & Wages'
      })
      salariesWagesData.value = salaryAccounts
      salariesWagesTotal.value = apiService.calculateTotal(salaryAccounts)

      // Derive Payroll Burden using section field
      const burdenAccounts = (dashboardData.value || []).filter(r => {
        if (!r || r.type !== 'account' || r.root_type !== 'Expense') return false
        const section = (r.section || '').toString()
        return section === 'Payroll Burden'
      })
      
      // Ensure the data has the correct structure for groupByReportClass
      const transformedBurdenData = burdenAccounts.map(item => ({
        account: item.account || item.account_name,
        account_name: item.account_name || item.account,
        report_class: item.report_class || 'Payroll Burden',
        currentMonth: {
          lastYear: item.currentMonth?.lastYear || 0,
          budget: item.currentMonth?.budget || 0,
          actual: item.currentMonth?.actual || 0
        },
        yearToDate: {
          lastYear: item.yearToDate?.lastYear || 0,
          budget: item.yearToDate?.budget || 0,
          actual: item.yearToDate?.actual || 0
        },
        forecast: {
          lastYear: item.forecast?.lastYear || 0,
          budget: item.forecast?.budget || 0,
          actual: item.forecast?.actual || 0
        }
      }))
      
      payrollBurdenData.value = transformedBurdenData
      payrollBurdenTotal.value = apiService.calculateTotal(transformedBurdenData)
      
      // Debug: Log the data being loaded
      console.log('Payroll Burden Data:', transformedBurdenData)
      console.log('Payroll Burden Total:', payrollBurdenTotal.value)

      // Load Indirect Expenses data
      try {
        // Strictly include only accounts classified as Indirect Expenses by backend
        const indirectExpensesAccounts = (dashboardData.value || []).filter(r => {
          if (!r || r.type !== 'account' || r.root_type !== 'Expense') return false
          const section = (r.section || '').toString()
          // Exclude all other expense categories - only include true Indirect Expenses
          if (section === 'Cost of Sales' || section === 'Direct Expenses' ||
              section === 'Salaries & Wages' || section === 'Payroll Burden') return false
          return section === 'Indirect Expenses'
        })
        
        // Transform to match expected structure
        const transformedIndirectData = indirectExpensesAccounts.map(item => ({
          account: item.account || item.account_name,
          account_name: item.account_name || item.account,
          report_class: item.report_class || 'Other',
          currentMonth: {
            lastYear: item.currentMonth?.lastYear || 0,
            budget: item.currentMonth?.budget || 0,
            actual: item.currentMonth?.actual || 0
          },
          yearToDate: {
            lastYear: item.yearToDate?.lastYear || 0,
            budget: item.yearToDate?.budget || 0,
            actual: item.yearToDate?.actual || 0
          },
          forecast: {
            lastYear: item.forecast?.lastYear || 0,
            budget: item.forecast?.budget || 0,
            actual: item.forecast?.actual || 0
          }
        }))
        
        indirectExpensesData.value = transformedIndirectData
        
        // Debug: Log the Indirect Expenses data and section breakdown
        console.log('Indirect Expenses Accounts Found:', indirectExpensesAccounts.length)
        console.log('Indirect Expenses Data:', transformedIndirectData)
        console.log('Indirect Expenses Total:', indirectExpensesTotal.value)
        
        const sectionBreakdown = (dashboardData.value || []).reduce((acc, r) => {
          const s = r?.section || 'Unknown'
          acc[s] = (acc[s] || 0) + (r?.type === 'account' ? 1 : 0)
          return acc
        }, {})
        console.log('Section breakdown (account rows):', sectionBreakdown)
        
      } catch (ieError) {
        console.error('Error processing indirect expenses:', ieError)
        indirectExpensesData.value = []
      }

    } catch (apiError) {
      // Set empty data if the specific APIs fail
      directRevenueData.value = [] // Set to empty array if no data
      costOfSalesData.value = [] // Set to empty array if no data
      directRevenueTotal.value = {}
      costOfSalesTotal.value = {}
      grossProfitTotal.value = {} // Set to empty if data fails
      // Salaries & Wages fallback
      const salaryAccounts = (dashboardData.value || []).filter(r => {
        if (!r || r.type !== 'account' || r.root_type !== 'Expense') return false
        const rc = (r.report_class || '').toString()
        return rc === 'Salaries & Wages' || SALARY_REGEX.test(rc)
      })
      salariesWagesData.value = salaryAccounts
      salariesWagesTotal.value = apiService.calculateTotal(salaryAccounts)

      // Payroll Burden fallback
      const burdenAccounts = (dashboardData.value || []).filter(r => {
        if (!r || r.type !== 'account' || r.root_type !== 'Expense') return false
        const rc = (r.report_class || '').toString()
        return rc === 'Payroll Burden' || PAYROLL_BURDEN_REGEX.test(rc)
      })
      payrollBurdenData.value = burdenAccounts
      payrollBurdenTotal.value = apiService.calculateTotal(burdenAccounts)
    }

  } catch (err) {
    error.value = err.message || 'Failed to load dashboard data'
  } finally {
    loading.value = false
  }
}

const loadFilterOptions = async () => {
  // No filter options to load
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
    error.value = 'Failed to export data'
  }
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('en-US', {
    style: 'decimal',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

const hasData = (row) => {
  if (!row) return false
  const periods = ['currentMonth', 'yearToDate', 'forecast']
  const metrics = ['lastYear', 'budget', 'actual']
  for (const p of periods) {
    for (const m of metrics) {
      const value = row?.[p]?.[m]
      if (typeof value === 'number' && Math.abs(value) > 0) return true
    }
  }
  return false
}

const formatPercentage = (value) => {
  if (value === null || value === undefined || isNaN(value)) return '0.00%'
  return `${(value * 100).toFixed(2)}%`
}

const getPercentageClass = (value) => {
  if (value === null || value === undefined || isNaN(value)) return 'text-gray-500'
  if (typeof value === 'string') return 'text-gray-500'
  if (value > 0) return 'text-success'
  if (value < 0) return 'text-destructive'
  return 'text-gray-500'
}

// Group rows by report_class with totals (Actual for each period)
const groupByReportClass = (rows) => {
  const initTotals = () => ({ lastYear: 0, budget: 0, actual: 0 })
  const groupsMap = new Map()
  
  for (const r of rows || []) {
    const key = r.report_class || 'Other'
    
    if (!groupsMap.has(key)) {
      groupsMap.set(key, { 
        report_class: key, 
        rows: [], 
        totals: { currentMonth: initTotals(), yearToDate: initTotals(), forecast: initTotals() }
      })
    }
    const g = groupsMap.get(key)
    g.rows.push(r)
    const add = (acc, val) => acc + (typeof val === 'number' && !isNaN(val) ? val : 0)
    g.totals.currentMonth.lastYear = add(g.totals.currentMonth.lastYear, r.currentMonth?.lastYear)
    g.totals.currentMonth.budget = add(g.totals.currentMonth.budget, r.currentMonth?.budget)
    g.totals.currentMonth.actual = add(g.totals.currentMonth.actual, r.currentMonth?.actual)

    g.totals.yearToDate.lastYear = add(g.totals.yearToDate.lastYear, r.yearToDate?.lastYear)
    g.totals.yearToDate.budget = add(g.totals.yearToDate.budget, r.yearToDate?.budget)
    g.totals.yearToDate.actual = add(g.totals.yearToDate.actual, r.yearToDate?.actual)

    g.totals.forecast.lastYear = add(g.totals.forecast.lastYear, r.forecast?.lastYear)
    g.totals.forecast.budget = add(g.totals.forecast.budget, r.forecast?.budget)
    g.totals.forecast.actual = add(g.totals.forecast.actual, r.forecast?.actual)
  }
  
  return Array.from(groupsMap.values())
}

// Computed: Calculate Gross Profit by Report Class
const grossProfitByReportClass = computed(() => {
  const revGroups = groupByReportClass(directRevenueData.value)
  const cosGroups = groupByReportClass(costOfSalesData.value)

  const normalize = (s) => (s || 'Other').trim()

  // Build lookup maps with normalized keys
  const revMap = new Map()
  for (const g of revGroups) {
    revMap.set(normalize(g.report_class), g)
  }
  const cosMap = new Map()
  for (const g of cosGroups) {
    cosMap.set(normalize(g.report_class), g)
  }

  // Union of keys from both sides
  const keys = new Set([...revMap.keys(), ...cosMap.keys()])

  const zeroTotals = () => ({ lastYear: 0, budget: 0, actual: 0 })
  const emptyPeriods = () => ({ currentMonth: zeroTotals(), yearToDate: zeroTotals(), forecast: zeroTotals() })

  const result = []
  for (const key of keys) {
    const revGroup = revMap.get(key)
    const cosGroup = cosMap.get(key)

    const displayName = (revGroup?.report_class) || (cosGroup?.report_class) || 'Other'
    const directTotals = revGroup?.totals || emptyPeriods()
    const costTotals = cosGroup?.totals || emptyPeriods()

    const grossTotals = {
      currentMonth: {
        lastYear: (directTotals.currentMonth.lastYear || 0) - (costTotals.currentMonth.lastYear || 0),
        budget: (directTotals.currentMonth.budget || 0) - (costTotals.currentMonth.budget || 0),
        actual: (directTotals.currentMonth.actual || 0) - (costTotals.currentMonth.actual || 0)
      },
      yearToDate: {
        lastYear: (directTotals.yearToDate.lastYear || 0) - (costTotals.yearToDate.lastYear || 0),
        budget: (directTotals.yearToDate.budget || 0) - (costTotals.yearToDate.budget || 0),
        actual: (directTotals.yearToDate.actual || 0) - (costTotals.yearToDate.actual || 0)
      },
      forecast: {
        lastYear: (directTotals.forecast.lastYear || 0) - (costTotals.forecast.lastYear || 0),
        budget: (directTotals.forecast.budget || 0) - (costTotals.forecast.budget || 0),
        actual: (directTotals.forecast.actual || 0) - (costTotals.forecast.actual || 0)
      }
    }

    result.push({
      report_class: displayName,
      directTotals,
      costTotals,
      grossTotals,
      directRows: revGroup?.rows || [],
      costRows: cosGroup?.rows || []
    })
  }

  return result
})

// Lifecycle
onMounted(async () => {
  await loadFilterOptions()
  // Initial load (will be skipped if filters-change fires immediately and triggers within debounce window)
  loadDashboardData()
})

// Development: Enable debug mode with keyboard shortcut
if (process.env.NODE_ENV === 'development') {
  document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.shiftKey && e.key === 'D') {
      showDebug.value = !showDebug.value
    }
  })
}

const calculateTotal = (data) => {
  return {
    currentMonth: {
      lastYear: data.totals.currentMonth.lastYear,
      budget: data.totals.currentMonth.budget,
      actual: data.totals.currentMonth.actual
    },
    yearToDate: {
      lastYear: data.totals.yearToDate.lastYear,
      budget: data.totals.yearToDate.budget,
      actual: data.totals.yearToDate.actual
    },
    forecast: {
      lastYear: data.totals.forecast.lastYear,
      budget: data.totals.forecast.budget,
      actual: data.totals.forecast.actual
    }
  }
}

// Helpers to render monthly cells
const getMonthlyCellValue = (row, monthIndex) => {
  if (!row) return 0
  if (monthIndex === 12) return row.forecast?.actual || 0
  const monthNumber = monthIndex + 1
  const selectedMonth = currentFilters.value?.month
  const monthly = row.monthly || {}
  const monthData = monthly[monthNumber] || {}
  if (!selectedMonth) return monthData.actual || 0
  const selectedMonthNum = parseInt(selectedMonth)
  if (isNaN(selectedMonthNum)) return monthData.actual || 0
  return monthNumber <= selectedMonthNum ? (monthData.actual || 0) : (monthData.budget || 0)
}

const getMonthlyTotalValue = (group, monthIndex) => {
  if (!group) return 0
  const rows = Array.isArray(group.rows) ? group.rows : []
  if (monthIndex === 12) return rows.reduce((s, r) => s + (r.forecast?.actual || 0), 0)
  const monthNumber = monthIndex + 1
  const selectedMonth = currentFilters.value?.month
  const selectedMonthNum = parseInt(selectedMonth)
  return rows.reduce((sum, r) => {
    const monthly = r.monthly || {}
    const monthData = monthly[monthNumber] || {}
    if (!selectedMonth || isNaN(selectedMonthNum)) return sum + (monthData.actual || 0)
    const value = monthNumber <= selectedMonthNum ? (monthData.actual || 0) : (monthData.budget || 0)
    return sum + value
  }, 0)
}

// Sum monthly values for an arbitrary array of rows
const sumMonthlyRows = (rows, monthIndex) => {
  const list = Array.isArray(rows) ? rows : []
  if (monthIndex === 12) return list.reduce((s, r) => s + (r.forecast?.actual || 0), 0)
  const monthNumber = monthIndex + 1
  const selectedMonth = currentFilters.value?.month
  const selectedMonthNum = parseInt(selectedMonth)
  return list.reduce((sum, r) => {
    const monthData = (r.monthly || {})[monthNumber] || {}
    if (!selectedMonth || isNaN(selectedMonthNum)) return sum + (monthData.actual || 0)
    return sum + (monthNumber <= selectedMonthNum ? (monthData.actual || 0) : (monthData.budget || 0))
  }, 0)
}

// Monthly gross = monthly direct - monthly cost
const getMonthlyGrossValue = (group, monthIndex) => {
  return sumMonthlyRows(group.directRows, monthIndex) - sumMonthlyRows(group.costRows, monthIndex)
}

</script> 