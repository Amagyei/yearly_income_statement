<template>
  <div class="min-h-screen bg-background">
    <div class="container mx-auto p-6 space-y-6">
      <!-- Header -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-dashboard-header">ERPNext P&L Dashboard</h1>
          <p class="text-muted-foreground mt-2">Direct ERPNext function mirror with real data representation</p>
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
            @click="goBack"
            class="flex items-center gap-2"
          >
            <ArrowLeft class="h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
      </div>

      <!-- ERPNext Filters -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader>
            <CardTitle class="text-sm">Company & Fiscal Year</CardTitle>
          </CardHeader>
          <CardContent class="space-y-3">
            <div>
              <Label>Company</Label>
              <Input v-model="filters.company" placeholder="Company name" />
            </div>
            <div>
              <Label>From Fiscal Year</Label>
              <Input v-model="filters.from_fiscal_year" placeholder="2025" />
            </div>
            <div>
              <Label>To Fiscal Year</Label>
              <Input v-model="filters.to_fiscal_year" placeholder="2025" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle class="text-sm">Period & View Settings</CardTitle>
          </CardHeader>
          <CardContent class="space-y-3">
            <div>
              <Label>Periodicity</Label>
              <select v-model="filters.periodicity" class="w-full p-2 border rounded">
                <option value="Yearly">Yearly</option>
                <option value="Half-Yearly">Half-Yearly</option>
                <option value="Quarterly">Quarterly</option>
                <option value="Monthly">Monthly</option>
              </select>
            </div>
            <div>
              <Label>Selected View</Label>
              <select v-model="filters.selected_view" class="w-full p-2 border rounded">
                <option value="Report">Report View</option>
                <option value="Growth">Growth View</option>
                <option value="Margin">Margin View</option>
              </select>
            </div>
            <div>
              <Label>Accumulated Values</Label>
              <input type="checkbox" v-model="filters.accumulated_values" class="ml-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle class="text-sm">Additional Filters</CardTitle>
          </CardHeader>
          <CardContent class="space-y-3">
            <div>
              <Label>Cost Center</Label>
              <Input v-model="filters.cost_center" placeholder="Optional" />
            </div>
            <div>
              <Label>Project</Label>
              <Input v-model="filters.project" placeholder="Optional" />
            </div>
            <div>
              <Label>Include Default FB Entries</Label>
              <input type="checkbox" v-model="filters.include_default_book_entries" class="ml-2" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle class="text-sm">Data Controls</CardTitle>
          </CardHeader>
          <CardContent class="space-y-3">
            <div>
              <Label>Hide Zero Values</Label>
              <input type="checkbox" v-model="hideZeroValues" class="ml-2" />
            </div>
            <div>
              <Label>Show Indent</Label>
              <input type="checkbox" v-model="showIndent" class="ml-2" />
            </div>
            <div>
              <Label>Max Rows</Label>
              <Input v-model="maxRows" type="number" placeholder="100" />
            </div>
          </CardContent>
        </Card>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <div class="flex items-center gap-3">
          <RefreshCw class="h-6 w-6 animate-spin text-primary" />
          <span class="text-lg text-muted-foreground">Loading ERPNext P&L data...</span>
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
        <!-- Summary Cards -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card class="bg-gradient-card border-table-border">
            <CardContent class="p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-muted-foreground">Total Income</p>
                  <p class="text-2xl font-bold text-dashboard-header">{{ formatCurrency(summaryData.total_income || 0) }}</p>
                </div>
                <DollarSign class="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card class="bg-gradient-card border-table-border">
            <CardContent class="p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-muted-foreground">Total Expenses</p>
                  <p class="text-2xl font-bold text-dashboard-header">{{ formatCurrency(summaryData.total_expenses || 0) }}</p>
                </div>
                <BarChart3 class="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card class="bg-gradient-card border-table-border">
            <CardContent class="p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-muted-foreground">Net Profit/Loss</p>
                  <p class="text-2xl font-bold text-dashboard-header">{{ formatCurrency(summaryData.net_profit || 0) }}</p>
                </div>
                <TrendingUp class="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>

          <Card class="bg-gradient-card border-table-border">
            <CardContent class="p-4">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-muted-foreground">Periods</p>
                  <p class="text-2xl font-bold text-dashboard-header">{{ periodList.length }}</p>
                </div>
                <PieChart class="h-8 w-8 text-primary" />
              </div>
            </CardContent>
          </Card>
        </div>

        <!-- Income Table -->
        <Card class="bg-gradient-card shadow-dashboard-lg border-table-border mt-8">
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
              <CardTitle class="text-dashboard-header font-bold text-lg">Income</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="p-0" v-if="!minimizeIncome">
            <div class="overflow-x-auto">
              <Table>
                <TableHeader class="bg-table-header">
                  <TableRow class="border-table-border">
                    <TableHead class="w-auto min-w-[200px] max-w-[800px] border-r border-table-border sticky left-0 bg-table-header z-10 whitespace-nowrap">
                      <Button 
                        variant="ghost" 
                        @click="handleSort('category')"
                        class="h-auto p-0 font-semibold text-dashboard-header hover:bg-transparent"
                      >
                        <ArrowUpDown class="h-4 w-4" />
                      </Button>
                    </TableHead>
                    
                    <!-- Period Columns -->
                    <TableHead 
                      v-for="period in periodList" 
                      :key="period.key" 
                      class="text-center border-r border-table-border bg-primary/5"
                    >
                      <div class="text-dashboard-header font-semibold">{{ period.label }}</div>
                    </TableHead>
                    
                    <!-- Total Column -->
                    <TableHead class="text-center bg-success/5">
                      <div class="text-dashboard-header font-semibold">Total</div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <template v-for="row in incomeData" :key="row.account || row.account_name">
                    <TableRow 
                      v-if="!hideZeroValues || hasData(row)"
                      :class="getRowClass(row)"
                    >
                      <TableCell class="font-medium py-2 border-r border-table-border">
                        {{ row.account_name || row.account }}
                      </TableCell>
                      <TableCell 
                        v-for="period in periodList" 
                        :key="period.key"
                        class="text-right py-2 border-r border-table-border"
                      >
                        {{ formatCurrency(row[period.key] || 0) }}
                      </TableCell>
                      <TableCell class="text-right font-medium py-2">
                        {{ formatCurrency(row.total || 0) }}
                      </TableCell>
                    </TableRow>
                  </template>
                  <!-- Income Total -->
                  <TableRow class="border-t-2 border-primary bg-primary/5 font-bold">
                    <TableCell class="font-bold py-3 border-r border-table-border">TOTAL INCOME</TableCell>
                    <TableCell 
                      v-for="period in periodList" 
                      :key="period.key"
                      class="text-right font-bold py-3 border-r border-table-border"
                    >
                      {{ formatCurrency(incomeTotal[period.key] || 0) }}
                    </TableCell>
                    <TableCell class="text-right font-bold py-3">
                      {{ formatCurrency(incomeTotal.total || 0) }}
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
              <CardTitle class="text-dashboard-header font-bold text-lg">Cost of Sales</CardTitle>
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
                    <TableHead 
                      v-for="period in periodList" 
                      :key="period.key" 
                      class="text-center border-r border-table-border bg-orange-500/5"
                    >
                      <div class="text-dashboard-header font-semibold">{{ period.label }}</div>
                    </TableHead>
                    <TableHead class="text-center bg-success/5">
                      <div class="text-dashboard-header font-semibold">Total</div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <template v-for="row in costOfSalesData" :key="row.account || row.account_name">
                    <TableRow 
                      v-if="!hideZeroValues || hasData(row)"
                      :class="getRowClass(row)"
                    >
                      <TableCell class="font-medium py-2 border-r border-table-border">
                        {{ row.account_name || row.account }}
                      </TableCell>
                      <TableCell 
                        v-for="period in periodList" 
                        :key="period.key"
                        class="text-right py-2 border-r border-table-border"
                      >
                        {{ formatCurrency(row[period.key] || 0) }}
                      </TableCell>
                      <TableCell class="text-right font-medium py-2">
                        {{ formatCurrency(row.total || 0) }}
                      </TableCell>
                    </TableRow>
                  </template>
                  <!-- Cost of Sales Total -->
                  <TableRow class="border-t-2 border-orange-500 bg-orange-500/5 font-bold">
                    <TableCell class="font-bold py-3 border-r border-table-border">TOTAL COST OF SALES</TableCell>
                    <TableCell 
                      v-for="period in periodList" 
                      :key="period.key"
                      class="text-right font-bold py-3 border-r border-table-border"
                    >
                      {{ formatCurrency(costOfSalesTotal[period.key] || 0) }}
                    </TableCell>
                    <TableCell class="text-right font-bold py-3">
                      {{ formatCurrency(costOfSalesTotal.total || 0) }}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <!-- Gross Profit Table -->
        <Card class="bg-gradient-card shadow-dashboard-lg border-table-border mt-8">
          <CardHeader class="px-4 py-2">
            <CardTitle class="text-dashboard-header font-bold text-lg">Gross Profit</CardTitle>
          </CardHeader>
          <CardContent class="p-0">
            <div class="overflow-x-auto">
              <Table>
                <TableHeader class="bg-table-header">
                  <TableRow class="border-table-border">
                    <TableHead class="w-auto min-w-[200px] max-w-[800px] border-r border-table-border sticky left-0 bg-table-header z-10 whitespace-nowrap">
                      Description
                    </TableHead>
                    <TableHead 
                      v-for="period in periodList" 
                      :key="period.key" 
                      class="text-center border-r border-table-border bg-success/5"
                    >
                      <div class="text-dashboard-header font-semibold">{{ period.label }}</div>
                    </TableHead>
                    <TableHead class="text-center bg-success/5">
                      <div class="text-dashboard-header font-semibold">Total</div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow class="bg-success/5">
                    <TableCell class="font-medium py-2 border-r border-table-border">Gross Profit</TableCell>
                    <TableCell 
                      v-for="period in periodList" 
                      :key="period.key"
                      class="text-right py-2 border-r border-table-border"
                    >
                      {{ formatCurrency(grossProfitTotals[period.key] || 0) }}
                    </TableCell>
                    <TableCell class="text-right font-medium py-2">
                      {{ formatCurrency(grossProfitTotals.total || 0) }}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <!-- Salaries and Wages Table -->
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
              <CardTitle class="text-dashboard-header font-bold text-lg">Salaries and Wages</CardTitle>
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
                    <TableHead 
                      v-for="period in periodList" 
                      :key="period.key" 
                      class="text-center border-r border-table-border bg-purple-500/5"
                    >
                      <div class="text-dashboard-header font-semibold">{{ period.label }}</div>
                    </TableHead>
                    <TableHead class="text-center bg-success/5">
                      <div class="text-dashboard-header font-semibold">Total</div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <template v-for="row in salariesWagesData" :key="row.account || row.account_name">
                    <TableRow 
                      v-if="!hideZeroValues || hasData(row)"
                      :class="getRowClass(row)"
                    >
                      <TableCell class="font-medium py-2 border-r border-table-border">
                        {{ row.account_name || row.account }}
                      </TableCell>
                      <TableCell 
                        v-for="period in periodList" 
                        :key="period.key"
                        class="text-right py-2 border-r border-table-border"
                      >
                        {{ formatCurrency(row[period.key] || 0) }}
                      </TableCell>
                      <TableCell class="text-right font-medium py-2">
                        {{ formatCurrency(row.total || 0) }}
                      </TableCell>
                    </TableRow>
                  </template>
                  <!-- Salaries and Wages Total -->
                  <TableRow class="border-t-2 border-purple-500 bg-purple-500/5 font-bold">
                    <TableCell class="font-bold py-3 border-r border-table-border">TOTAL SALARIES AND WAGES</TableCell>
                    <TableCell 
                      v-for="period in periodList" 
                      :key="period.key"
                      class="text-right font-bold py-3 border-r border-table-border"
                    >
                      {{ formatCurrency(salariesWagesTotal[period.key] || 0) }}
                    </TableCell>
                    <TableCell class="text-right font-bold py-3">
                      {{ formatCurrency(salariesWagesTotal.total || 0) }}
                    </TableCell>
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
                    <TableHead 
                      v-for="period in periodList" 
                      :key="period.key" 
                      class="text-center border-r border-table-border bg-slate-500/5"
                    >
                      <div class="text-dashboard-header font-semibold">{{ period.label }}</div>
                    </TableHead>
                    <TableHead class="text-center bg-success/5">
                      <div class="text-dashboard-header font-semibold">Total</div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <template v-for="row in payrollBurdenData" :key="row.account || row.account_name">
                    <TableRow 
                      v-if="!hideZeroValues || hasData(row)"
                      :class="getRowClass(row)"
                    >
                      <TableCell class="font-medium py-2 border-r border-table-border">
                        {{ row.account_name || row.account }}
                      </TableCell>
                      <TableCell 
                        v-for="period in periodList" 
                        :key="period.key"
                        class="text-right py-2 border-r border-table-border"
                      >
                        {{ formatCurrency(row[period.key] || 0) }}
                      </TableCell>
                      <TableCell class="text-right font-medium py-2">
                        {{ formatCurrency(row.total || 0) }}
                      </TableCell>
                    </TableRow>
                  </template>
                  <!-- Payroll Burden Total -->
                  <TableRow class="border-t-2 border-slate-500 bg-slate-500/5 font-bold">
                    <TableCell class="font-bold py-3 border-r border-table-border">TOTAL PAYROLL BURDEN</TableCell>
                    <TableCell 
                      v-for="period in periodList" 
                      :key="period.key"
                      class="text-right font-bold py-3 border-r border-table-border"
                    >
                      {{ formatCurrency(payrollBurdenTotal[period.key] || 0) }}
                    </TableCell>
                    <TableCell class="text-right font-bold py-3">
                      {{ formatCurrency(payrollBurdenTotal.total || 0) }}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <!-- Combined Payroll Total -->
        <Card class="bg-gradient-card shadow-dashboard-lg border-table-border mt-8">
          <CardHeader class="px-4 py-2">
            <CardTitle class="text-dashboard-header font-bold text-lg">Combined Payroll</CardTitle>
          </CardHeader>
          <CardContent class="p-0">
            <div class="overflow-x-auto">
              <Table>
                <TableHeader class="bg-table-header">
                  <TableRow class="border-table-border">
                    <TableHead class="w-auto min-w-[200px] max-w-[800px] border-r border-table-border sticky left-0 bg-table-header z-10 whitespace-nowrap">
                      Description
                    </TableHead>
                    <TableHead 
                      v-for="period in periodList" 
                      :key="period.key" 
                      class="text-center border-r border-table-border bg-warning/5"
                    >
                      <div class="text-dashboard-header font-semibold">{{ period.label }}</div>
                    </TableHead>
                    <TableHead class="text-center bg-success/5">
                      <div class="text-dashboard-header font-semibold">Total</div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow class="bg-warning/5">
                    <TableCell class="font-medium py-2 border-r border-table-border">Combined Payroll Total</TableCell>
                    <TableCell 
                      v-for="period in periodList" 
                      :key="period.key"
                      class="text-right py-2 border-r border-table-border"
                    >
                      {{ formatCurrency(combinedPayrollTotal[period.key] || 0) }}
                    </TableCell>
                    <TableCell class="text-right font-medium py-2">
                      {{ formatCurrency(combinedPayrollTotal.total || 0) }}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <!-- Other Expenses Table -->
        <Card class="bg-gradient-card shadow-dashboard-lg border-table-border mt-8">
          <CardHeader class="flex items-center justify-between px-4 py-2">
            <div class="flex items-center space-x-3">
              <Button 
                variant="ghost" 
                size="sm"
                @click="minimizeOtherExpenses = !minimizeOtherExpenses"
                class="p-1"
              >
                {{ minimizeOtherExpenses ? '▶' : '▼' }}
              </Button>
              <CardTitle class="text-dashboard-header font-bold text-lg">Other Expenses</CardTitle>
            </div>
          </CardHeader>
          <CardContent class="p-0" v-if="!minimizeOtherExpenses">
            <div class="overflow-x-auto">
              <Table>
                <TableHeader class="bg-table-header">
                  <TableRow class="border-table-border">
                    <TableHead class="w-auto min-w-[200px] max-w-[800px] border-r border-table-border sticky left-0 bg-table-header z-10 whitespace-nowrap">
                      Account
                    </TableHead>
                    <TableHead 
                      v-for="period in periodList" 
                      :key="period.key" 
                      class="text-center border-r border-table-border bg-destructive/5"
                    >
                      <div class="text-dashboard-header font-semibold">{{ period.label }}</div>
                    </TableHead>
                    <TableHead class="text-center bg-success/5">
                      <div class="text-dashboard-header font-semibold">Total</div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <template v-for="row in otherExpensesData" :key="row.account || row.account_name">
                    <TableRow 
                      v-if="!hideZeroValues || hasData(row)"
                      :class="getRowClass(row)"
                    >
                      <TableCell class="font-medium py-2 border-r border-table-border">
                        {{ row.account_name || row.account }}
                      </TableCell>
                      <TableCell 
                        v-for="period in periodList" 
                        :key="period.key"
                        class="text-right py-2 border-r border-table-border"
                      >
                        {{ formatCurrency(row[period.key] || 0) }}
                      </TableCell>
                      <TableCell class="text-right font-medium py-2">
                        {{ formatCurrency(row.total || 0) }}
                      </TableCell>
                    </TableRow>
                  </template>
                  <!-- Other Expenses Total -->
                  <TableRow class="border-t-2 border-destructive bg-destructive/5 font-bold">
                    <TableCell class="font-bold py-3 border-r border-table-border">TOTAL OTHER EXPENSES</TableCell>
                    <TableCell 
                      v-for="period in periodList" 
                      :key="period.key"
                      class="text-right font-bold py-3 border-r border-table-border"
                    >
                      {{ formatCurrency(otherExpensesTotal[period.key] || 0) }}
                    </TableCell>
                    <TableCell class="text-right font-bold py-3">
                      {{ formatCurrency(otherExpensesTotal.total || 0) }}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>

        <!-- Period Information -->
        <Card>
          <CardHeader>
            <CardTitle>Period Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 class="font-semibold mb-2">Generated Periods</h4>
                <div class="space-y-1 text-sm">
                  <div v-for="period in periodList" :key="period.key" class="flex justify-between">
                    <span>{{ period.label }}</span>
                    <span class="text-muted-foreground">
                      {{ formatDate(period.from_date) }} - {{ formatDate(period.to_date) }}
                    </span>
                  </div>
                </div>
              </div>
              <div>
                <h4 class="font-semibold mb-2">Data Summary</h4>
                <div class="space-y-1 text-sm">
                  <div class="flex justify-between">
                    <span>Total Rows:</span>
                    <span>{{ dashboardData.length }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span>Periods:</span>
                    <span>{{ periodList.length }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span>View Mode:</span>
                    <span>{{ filters.selected_view }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span>Accumulated:</span>
                    <span>{{ filters.accumulated_values ? 'Yes' : 'No' }}</span>
                  </div>
                </div>
              </div>
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
            No P&L data found for the selected filters. Try adjusting your filters or check if data exists for the selected period.
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Button } from '@/components/ui'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui'
import { Input } from '@/components/ui'
import { Label } from '@/components/ui'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui'
import { 
  RefreshCw, 
  Download, 
  AlertCircle, 
  ArrowLeft,
  BarChart3,
  DollarSign,
  TrendingUp,
  PieChart,
  ArrowUpDown
} from 'lucide-vue-next'
import testApiService from '../services/testApi'

// State
const loading = ref(false)
const error = ref(null)
const dashboardData = ref([])
const summaryData = ref({})
const periodList = ref([])
const showDebug = ref(false)
const router = useRouter()

// Dashboard settings
const hideZeroValues = ref(false)
const showIndent = ref(true)
const maxRows = ref(100)

// Table minimize states
const minimizeIncome = ref(false)
const minimizeCostOfSales = ref(false)
const minimizeSalariesWages = ref(false)
const minimizePayrollBurden = ref(false)
const minimizeOtherExpenses = ref(false)

// Filters (ERPNext P&L format)
const filters = reactive({
  company: 'Western Serene Atlantic Hotel Ltd',
  from_fiscal_year: '2025',
  to_fiscal_year: '2025',
  periodicity: 'Yearly',
  selected_view: 'Report',
  accumulated_values: false,
  cost_center: '',
  project: '',
  include_default_book_entries: true
})

// Computed
// Data section computed properties
const incomeData = computed(() => {
  if (!dashboardData.value.length) return []
  // Filter for income accounts based on account structure
  return dashboardData.value.filter(row => 
    row.account?.startsWith('400') || 
    row.account_name?.toLowerCase().includes('income') ||
    row.account_name?.toLowerCase().includes('revenue')
  )
})

const costOfSalesData = computed(() => {
  if (!dashboardData.value.length) return []
  // Filter for cost of sales accounts based on account structure
  return dashboardData.value.filter(row => 
    row.account?.startsWith('500') && 
    (row.account_name?.toLowerCase().includes('cost') || 
     row.account_name?.toLowerCase().includes('sales') ||
     row.account_name?.toLowerCase().includes('food') ||
     row.account_name?.toLowerCase().includes('beverage'))
  )
})

const salariesWagesData = computed(() => {
  if (!dashboardData.value.length) return []
  // Filter for salary and wage accounts based on account structure
  return dashboardData.value.filter(row => 
    row.account?.startsWith('500') && 
    (row.account_name?.toLowerCase().includes('salary') || 
     row.account_name?.toLowerCase().includes('wage') ||
     row.account_name?.toLowerCase().includes('payroll') ||
     row.account_name?.toLowerCase().includes('staff'))
  )
})

const payrollBurdenData = computed(() => {
  if (!dashboardData.value.length) return []
  // Filter for payroll burden accounts based on account structure
  return dashboardData.value.filter(row => 
    row.account?.startsWith('500') && 
    (row.account_name?.toLowerCase().includes('tax') || 
     row.account_name?.toLowerCase().includes('benefit') ||
     row.account_name?.toLowerCase().includes('burden') ||
     row.account_name?.toLowerCase().includes('social') ||
     row.account_name?.toLowerCase().includes('insurance'))
  )
})

const otherExpensesData = computed(() => {
  if (!dashboardData.value.length) return []
  // Filter for other expense accounts (not covered above)
  return dashboardData.value.filter(row => 
    row.account?.startsWith('500') && 
    !row.account_name?.toLowerCase().includes('salary') &&
    !row.account_name?.toLowerCase().includes('wage') &&
    !row.account_name?.toLowerCase().includes('payroll') &&
    !row.account_name?.toLowerCase().includes('staff') &&
    !row.account_name?.toLowerCase().includes('tax') &&
    !row.account_name?.toLowerCase().includes('benefit') &&
    !row.account_name?.toLowerCase().includes('burden') &&
    !row.account_name?.toLowerCase().includes('social') &&
    !row.account_name?.toLowerCase().includes('insurance') &&
    !row.account_name?.toLowerCase().includes('cost') &&
    !row.account_name?.toLowerCase().includes('sales') &&
    !row.account_name?.toLowerCase().includes('food') &&
    !row.account_name?.toLowerCase().includes('beverage')
  )
})

// Total calculations
const incomeTotal = computed(() => {
  return calculateTotals(incomeData.value, periodList.value)
})

const costOfSalesTotal = computed(() => {
  return calculateTotals(costOfSalesData.value, periodList.value)
})

const salariesWagesTotal = computed(() => {
  return calculateTotals(salariesWagesData.value, periodList.value)
})

const payrollBurdenTotal = computed(() => {
  return calculateTotals(payrollBurdenData.value, periodList.value)
})

const otherExpensesTotal = computed(() => {
  return calculateTotals(otherExpensesData.value, periodList.value)
})

const grossProfitTotals = computed(() => {
  const totals = {}
  periodList.value.forEach(period => {
    totals[period.key] = (incomeTotal.value[period.key] || 0) - (costOfSalesTotal.value[period.key] || 0)
  })
  totals.total = (incomeTotal.value.total || 0) - (costOfSalesTotal.value.total || 0)
  return totals
})

const combinedPayrollTotal = computed(() => {
  const totals = {}
  periodList.value.forEach(period => {
    totals[period.key] = (salariesWagesTotal.value[period.key] || 0) + (payrollBurdenTotal.value[period.key] || 0)
  })
  totals.total = (salariesWagesTotal.value.total || 0) + (payrollBurdenTotal.value.total || 0)
  return totals
})

const filteredData = computed(() => {
  let data = dashboardData.value
  
  // Apply zero value filtering
  if (hideZeroValues.value) {
    data = data.filter(row => {
      if (row.indent === 0) return true // Keep headers
      if (row.account_name?.includes('TOTAL')) return true // Keep totals
      
      // Check if any period has non-zero values
      return periodList.value.some(period => {
        const value = row[period.key]
        return value && Math.abs(Number(value)) > 0.01
      })
    })
  }
  
  // Apply row limit
  if (maxRows.value > 0) {
    data = data.slice(0, maxRows.value)
  }
  
  return data
})

const debugInfo = computed(() => ({
  filters: filters,
  dashboardData: dashboardData.value,
  periodList: periodList.value,
  summaryData: summaryData.value,
  loading: loading.value,
  error: error.value,
  hideZeroValues: hideZeroValues.value,
  showIndent: showIndent.value,
  maxRows: maxRows.value
}))

// Methods
const goBack = () => {
  router.push('/dashboard')
}

const refreshData = async () => {
  loading.value = true
  error.value = null
  
  try {
    console.log('Loading ERPNext P&L data with filters:', filters)
    
    // Step 1: Get period list using ERPNext function
    const periodResponse = await testApiService.testPeriodListGeneration(filters)
    if (periodResponse.success) {
      periodList.value = periodResponse.period_list
    } else {
      throw new Error('Failed to generate period list')
    }
    
    // Step 2: Get complete P&L execution using ERPNext functions
    const pnlResponse = await testApiService.testCompletePnlExecution(filters)
    if (pnlResponse.success) {
      // Extract the actual financial data from the ERPNext response
      const sampleData = pnlResponse.sample_data
      if (sampleData) {
        // Build the complete dataset from ERPNext response
        const data = []
        
        // Add income data
        if (sampleData.first_income_row) {
          data.push(sampleData.first_income_row)
        }
        
        // Add expense data
        if (sampleData.first_expense_row) {
          data.push(sampleData.first_expense_row)
        }
        
        // Add net profit/loss
        if (sampleData.net_profit_loss) {
          data.push(sampleData.net_profit_loss)
        }
        
        dashboardData.value = data
      } else {
        dashboardData.value = []
      }
      
      // Extract summary data from actual ERPNext values
      if (pnlResponse.execution_summary) {
        const sampleData = pnlResponse.sample_data
        summaryData.value = {
          total_income: sampleData?.first_income_row?.total || 0,
          total_expenses: sampleData?.first_expense_row?.total || 0,
          net_profit: sampleData?.net_profit_loss?.total || 0
        }
      }
    } else {
      throw new Error('Failed to execute P&L')
    }
    
    console.log('ERPNext P&L data loaded successfully')
    
  } catch (err) {
    console.error('Failed to load ERPNext P&L data:', err)
    error.value = err.message || 'Failed to load ERPNext P&L data'
  } finally {
    loading.value = false
  }
}

const exportData = async () => {
  try {
    const exportData = {
      filters: filters,
      periodList: periodList.value,
      dashboardData: dashboardData.value,
      summaryData: summaryData.value,
      exportDate: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `erpnext-pnl-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
  } catch (err) {
    console.error('Export failed:', err)
    error.value = 'Export failed: ' + err.message
  }
}

// Helper functions
const calculateTotals = (data, periods) => {
  const totals = {}
  periods.forEach(period => {
    totals[period.key] = data.reduce((sum, row) => {
      return sum + (Number(row[period.key]) || 0)
    }, 0)
  })
  totals.total = data.reduce((sum, row) => {
    return sum + (Number(row.total) || 0)
  }, 0)
  return totals
}

const hasData = (row) => {
  if (!periodList.value.length) return true
  return periodList.value.some(period => {
    const value = row[period.key]
    return value && Math.abs(Number(value)) > 0.01
  })
}

const getRowClass = (row) => {
  if (row.account?.startsWith('400')) {
    return 'hover:bg-green-50'
  } else if (row.account?.startsWith('500')) {
    return 'hover:bg-red-50'
  }
  return 'hover:bg-muted/50'
}

const handleSort = (field) => {
  // Simple sort implementation - can be enhanced later
  console.log('Sorting by:', field)
}

const formatCurrency = (value) => {
  if (!value || isNaN(value)) return '0.00'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'GHS',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(Math.abs(value))
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    })
  } catch {
    return dateString
  }
}

// Load initial data
onMounted(() => {
  refreshData()
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
