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

    <!-- Income & Expenses Table -->
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
          <CardTitle class="text-dashboard-header font-bold text-lg">Income & Expenses</CardTitle>
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
                  :class="`text-center text-dashboard-subheader py-1 ${idx < 4 ? 'border-r border-table-border' : ''}`"
                >
                  <div class="text-xs">{{ header }}</div>
                </TableHead>
              </TableRow>
            </TableHeader>
            
            <TableBody>
              <!-- INCOME SECTION -->
              <!-- Data Structure Debug (temporary) -->
              <TableRow class="bg-gray-100">
                <TableCell :colspan="16" class="text-xs text-gray-600 p-2">
                  <strong>Data Structure:</strong> 
                  Main Headers: {{ (props.data || []).filter(row => row.type === 'main_header' && row.root_type === 'Income').length }} | 
                  Sub Headers: {{ (props.data || []).filter(row => row.type === 'header' && row.root_type === 'Income').length }} | 
                  Accounts: {{ (props.data || []).filter(row => row.type === 'account' && row.root_type === 'Income').length }}
                  <br>
                  <strong>Sub Headers Found:</strong> 
                  {{ (props.data || []).filter(row => row.type === 'header' && row.root_type === 'Income').map(row => row.category).join(', ') }}
                  <br>
                  <strong>Grouped Income Data:</strong>
                  {{ groupedIncomeData.length }} sections found
                  <br>
                  <strong>Section Names:</strong>
                  {{ groupedIncomeData.map(section => section.name).join(', ') }}
                  <br>
                  <strong>EXPENSE STRUCTURE:</strong>
                  Direct Expenses (500xx): {{ (props.data || []).filter(row => row.type === 'account' && row.root_type === 'Expense' && row.account && row.account.startsWith('500')).length }} accounts |
                  Indirect Expenses (600xx+): {{ (props.data || []).filter(row => row.type === 'account' && row.root_type === 'Expense' && row.account && !row.account.startsWith('500')).length }} accounts |
                  Filtered Expense Rows: {{ expenseRows.length }} rows
                </TableCell>
              </TableRow>
              

              
              <!-- Display Grouped Revenue Headers with Totals -->
              <template v-for="section in groupedIncomeData" :key="section.name">
                <!-- Revenue Sub Header Row (e.g., "Rooms Revenue", "Food Revenue") -->
                <TableRow class="bg-primary/10 hover:bg-primary/20 border-b-2 border-primary font-bold">
                  <TableCell 
                    class="px-4 py-4 font-bold text-lg text-primary bg-primary/10 leading-relaxed border-r border-table-border sticky left-0 z-10"
                    style="min-height: 2.5rem; white-space: normal; word-wrap: break-word;"
                  >
                    {{ section.name }}
                  </TableCell>
                  <!-- Current Month Header Totals -->
                  <TableCell class="text-right border-r border-table-border py-4 font-bold">
                    {{ formatNumber(getRevenueSectionTotals(section, 'currentMonth', 'lastYear')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-4 font-bold">
                    {{ formatNumber(getRevenueSectionTotals(section, 'currentMonth', 'budget')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-4 font-bold">
                    {{ formatNumber(getRevenueSectionTotals(section, 'currentMonth', 'actual')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-4"></TableCell>
                  <TableCell class="text-right border-r border-table-border py-4"></TableCell>
                  <!-- Year to Date Header Totals -->
                  <TableCell class="text-right border-r border-table-border py-4 font-bold">
                    {{ formatNumber(getRevenueSectionTotals(section, 'yearToDate', 'lastYear')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-4 font-bold">
                    {{ formatNumber(getRevenueSectionTotals(section, 'yearToDate', 'budget')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-4 font-bold">
                    {{ formatNumber(getRevenueSectionTotals(section, 'yearToDate', 'actual')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-4"></TableCell>
                  <TableCell class="text-right border-r border-table-border py-4"></TableCell>
                  <!-- Forecast Header Totals -->
                  <TableCell class="text-right border-r border-table-border py-4 font-bold">
                    {{ formatNumber(getRevenueSectionTotals(section, 'forecast', 'lastYear')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-4 font-bold">
                    {{ formatNumber(getRevenueSectionTotals(section, 'forecast', 'budget')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-4 font-bold">
                    {{ formatNumber(getRevenueSectionTotals(section, 'forecast', 'actual')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-4"></TableCell>
                  <TableCell class="text-right border-r border-table-border py-4"></TableCell>
                </TableRow>
                
                <!-- Account Rows for this section -->
                <TableRow
                  v-for="account in section.incomeAccounts"
                  :key="account.account"
                  :class="getRowClass(account)"
                >
                  <TableCell :class="getCategoryCellClass(account)">
                    {{ getCategoryDisplay(account) }}
                  </TableCell>
                  <!-- Current Month Data -->
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(account?.currentMonth?.lastYear || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(account?.currentMonth?.budget || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(account?.currentMonth?.actual || 0) }}
                  </TableCell>
                  <TableCell class="text-right py-1">
                    <span :class="getPercentageClass(account?.currentMonth?.actBudThisYear)" class="block text-right">
                      {{ typeof account?.currentMonth?.actBudThisYear === 'string' ? account?.currentMonth?.actBudThisYear : formatPercentage(account?.currentMonth?.actBudThisYear) }}
                    </span>
                  </TableCell>
                  <TableCell class="text-right py-1">
                    <span :class="getPercentageClass(account?.currentMonth?.actVsLastYear)" class="block text-right">
                      {{ typeof account?.currentMonth?.actVsLastYear === 'string' ? account?.currentMonth?.actVsLastYear : formatPercentage(account?.currentMonth?.actVsLastYear) }}
                    </span>
                  </TableCell>
                  <!-- Year to Date Data -->
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(account?.yearToDate?.lastYear || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(account?.yearToDate?.budget || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(account?.yearToDate?.actual || 0) }}
                  </TableCell>
                  <TableCell class="text-right py-1">
                    <span :class="getPercentageClass(account?.yearToDate?.actBudThisYear)" class="block text-right">
                      {{ typeof account?.yearToDate?.actBudThisYear === 'string' ? account?.yearToDate?.actBudThisYear : formatPercentage(account?.yearToDate?.actBudThisYear) }}
                    </span>
                  </TableCell>
                  <TableCell class="text-right py-1">
                    <span :class="getPercentageClass(account?.yearToDate?.actVsLastYear)" class="block text-right">
                      {{ typeof account?.yearToDate?.actVsLastYear === 'string' ? account?.yearToDate?.actVsLastYear : formatPercentage(account?.yearToDate?.actVsLastYear) }}
                    </span>
                  </TableCell>
                  <!-- Forecast Data -->
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(account?.forecast?.lastYear || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(account?.forecast?.budget || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(account?.forecast?.actual || 0) }}
                  </TableCell>
                  <TableCell class="text-right py-1">
                    <span :class="getPercentageClass(account?.forecast?.actBudThisYear)" class="block text-right">
                      {{ typeof account?.forecast?.actBudThisYear === 'string' ? account?.forecast?.actBudThisYear : formatPercentage(account?.forecast?.actBudThisYear) }}
                    </span>
                  </TableCell>
                  <TableCell class="text-right py-1">
                    <span :class="getPercentageClass(account?.forecast?.actVsLastYear)" class="block text-right">
                      {{ typeof account?.forecast?.actVsLastYear === 'string' ? account?.forecast?.actVsLastYear : formatPercentage(account?.forecast?.actVsLastYear) }}
                    </span>
                  </TableCell>
                </TableRow>
              </template>
              
              <!-- Final Revenue Totals Row -->
              <TableRow class="border-t-2 border-primary bg-primary/10 font-bold">
                <TableCell class="font-bold border-r border-table-border sticky left-0 bg-primary/10 z-10 py-3">
                  TOTAL REVENUE
                </TableCell>
                <!-- Current Month Totals -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.currentMonth?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.currentMonth?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.currentMonth?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Year to Date Totals -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.yearToDate?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.yearToDate?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.yearToDate?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Forecast Totals -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.forecast?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.forecast?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.forecast?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              </TableRow>
              
              <!-- EXPENSES SECTION -->
              <!-- Expense Structure Debug -->
              <TableRow class="bg-red-50">
                <TableCell :colspan="16" class="text-xs text-red-600 p-2">
                  <strong>EXPENSE FILTERING DEBUG:</strong> 
                  All Expense Rows: {{ (props.data || []).filter(row => row.root_type === 'Expense').length }} |
                  Filtered Expense Rows: {{ expenseRows.length }} |
                  Direct Expenses (500xx): {{ (props.data || []).filter(row => row.type === 'account' && row.root_type === 'Expense' && row.account && row.account.startsWith('500')).length }} |
                  Indirect Expenses (600xx+): {{ (props.data || []).filter(row => row.type === 'account' && row.root_type === 'Expense' && row.account && !row.account.startsWith('500')).length }}
                  <br>
                  <strong>Expense Headers Found:</strong> 
                  {{ (props.data || []).filter(row => row.type === 'header' && row.root_type === 'Expense').map(row => row.category).join(', ') }}
                  <br>
                  <strong>Sample Direct Expense Accounts:</strong> 
                  {{ (props.data || []).filter(row => row.type === 'account' && row.root_type === 'Expense' && row.account && row.account.startsWith('500')).slice(0, 5).map(acc => acc.account).join(', ') }}
                </TableCell>
              </TableRow>
              
              <!-- Account Separation Validation Debug -->
              <TableRow class="bg-blue-50">
                <TableCell :colspan="16" class="text-xs text-blue-600 p-2">
                  <strong>ACCOUNT SEPARATION VALIDATION:</strong>
                  <br>
                  <strong>Total Accounts:</strong> 
                  Salaries: {{ validateAccountSeparation.totalAccounts.salaries }} | 
                  Payroll Burden: {{ validateAccountSeparation.totalAccounts.payrollBurden }} | 
                  Other Expenses: {{ validateAccountSeparation.totalAccounts.otherExpenses }}
                  <br>
                  <strong>Duplicates Found:</strong> 
                  {{ validateAccountSeparation.hasDuplicates ? 'YES - CHECK BELOW' : 'NO - All accounts properly separated' }}
                  <br>
                  <span v-if="validateAccountSeparation.salariesPayrollDuplicates.length > 0" class="text-red-600">
                    <strong>Salaries ↔ Payroll Burden Duplicates:</strong> {{ validateAccountSeparation.salariesPayrollDuplicates.join(', ') }}
                  </span>
                  <span v-if="validateAccountSeparation.salariesOtherDuplicates.length > 0" class="text-red-600">
                    <strong>Salaries ↔ Other Expenses Duplicates:</strong> {{ validateAccountSeparation.salariesOtherDuplicates.join(', ') }}
                  </span>
                  <span v-if="validateAccountSeparation.payrollOtherDuplicates.length > 0" class="text-red-600">
                    <strong>Payroll Burden ↔ Other Expenses Duplicates:</strong> {{ validateAccountSeparation.payrollOtherDuplicates.join(', ') }}
                  </span>
                </TableCell>
              </TableRow>
              
              <!-- Main Expenses Header -->
              
              
              <!-- Direct Expenses Header - Now acts as a Total Row -->
              <TableRow class="bg-destructive/10 hover:bg-destructive/20 border-b-2 border-destructive font-bold">
                <TableCell 
                  class="px-4 py-4 font-bold text-lg text-destructive bg-destructive/10 leading-relaxed border-r border-table-border sticky left-0 z-10"
                  style="min-height: 2.5rem; white-space: normal; word-wrap: break-word;"
                >
                  DIRECT EXPENSES
                </TableCell>
                <!-- Current Month Header Totals -->
                <TableCell class="text-right border-r border-table-border py-4 font-bold">
                  {{ formatNumber(directExpensesTotals.currentMonth?.lastYear || 0) }}
                </TableCell>
                <TableCell class="text-right border-r border-table-border py-4 font-bold">
                  {{ formatNumber(directExpensesTotals.currentMonth?.budget || 0) }}
                </TableCell>
                <TableCell class="text-right border-r border-table-border py-4 font-bold">
                  {{ formatNumber(directExpensesTotals.currentMonth?.actual || 0) }}
                </TableCell>
                <TableCell class="text-right border-r border-table-border py-4"></TableCell>
                <TableCell class="text-right border-r border-table-border py-4"></TableCell>
                <!-- Year to Date Header Totals -->
                <TableCell class="text-right border-r border-table-border py-4 font-bold">
                  {{ formatNumber(directExpensesTotals.yearToDate?.lastYear || 0) }}
                </TableCell>
                <TableCell class="text-right border-r border-table-border py-4 font-bold">
                  {{ formatNumber(directExpensesTotals.yearToDate?.budget || 0) }}
                </TableCell>
                <TableCell class="text-right border-r border-table-border py-4 font-bold">
                  {{ formatNumber(directExpensesTotals.yearToDate?.actual || 0) }}
                </TableCell>
                <TableCell class="text-right border-r border-table-border py-4"></TableCell>
                <TableCell class="text-right border-r border-table-border py-4"></TableCell>
                <!-- Forecast Header Totals -->
                <TableCell class="text-right border-r border-table-border py-4 font-bold">
                  {{ formatNumber(directExpensesTotals.forecast?.lastYear || 0) }}
                </TableCell>
                <TableCell class="text-right border-r border-table-border py-4 font-bold">
                  {{ formatNumber(directExpensesTotals.forecast?.budget || 0) }}
                </TableCell>
                <TableCell class="text-right border-r border-table-border py-4 font-bold">
                  {{ formatNumber(directExpensesTotals.forecast?.actual || 0) }}
                </TableCell>
                <TableCell class="text-right border-r border-table-border py-4"></TableCell>
                <TableCell class="text-right border-r border-table-border py-4"></TableCell>
              </TableRow>
              
              <!-- Cost of Sales Data -->
              <template v-for="section in costOfSalesData" :key="section.name">
                <!-- Section Header - Now acts as a Total Row -->
                <TableRow :class="getRowClass({type: 'header', category: section?.name})">
                  <TableCell :class="getCategoryCellClass({type: 'header', category: section?.name})" class="border-r border-table-border sticky left-0 z-10">
                    {{ section?.name?.toUpperCase() || '' }}
                  </TableCell>
                  <!-- Current Month Section Totals -->
                  <TableCell class="text-right border-r border-table-border py-1 font-bold">
                    {{ formatNumber(getSectionTotals(section, 'currentMonth', 'lastYear')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-1 font-bold">
                    {{ formatNumber(getSectionTotals(section, 'currentMonth', 'budget')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-1 font-bold">
                    {{ formatNumber(getSectionTotals(section, 'currentMonth', 'actual')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-1"></TableCell>
                  <TableCell class="text-right border-r border-table-border py-1"></TableCell>
                  <!-- Year to Date Section Totals -->
                  <TableCell class="text-right border-r border-table-border py-1 font-bold">
                    {{ formatNumber(getSectionTotals(section, 'yearToDate', 'lastYear')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-1 font-bold">
                    {{ formatNumber(getSectionTotals(section, 'yearToDate', 'budget')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-1 font-bold">
                    {{ formatNumber(getSectionTotals(section, 'yearToDate', 'actual')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-1"></TableCell>
                  <TableCell class="text-right border-r border-table-border py-1"></TableCell>
                  <!-- Forecast Section Totals -->
                  <TableCell class="text-right border-r border-table-border py-1 font-bold">
                    {{ formatNumber(getSectionTotals(section, 'forecast', 'lastYear')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-1 font-bold">
                    {{ formatNumber(getSectionTotals(section, 'forecast', 'budget')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-1 font-bold">
                    {{ formatNumber(getSectionTotals(section, 'forecast', 'actual')) }}
                  </TableCell>
                  <TableCell class="text-right border-r border-table-border py-1"></TableCell>
                  <TableCell class="text-right border-r border-table-border py-1"></TableCell>
                </TableRow>
                <!-- Expense Accounts -->
                <TableRow
                  v-for="row in (props.hideZeroRows ? (section.expenseAccounts || []).filter(hasData) : (section.expenseAccounts || []))"
                  :key="row.account"
                  :class="getRowClass(row)"
                >
                  <TableCell :class="getCategoryCellClass(row)">
                    {{ getCategoryDisplay(row) }}
                  </TableCell>
                  <!-- Current Month Data -->
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(row?.currentMonth?.lastYear || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(row?.currentMonth?.budget || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(row?.currentMonth?.actual || 0) }}
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
                    {{ formatNumber(row?.yearToDate?.lastYear || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(row?.yearToDate?.budget || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(row?.yearToDate?.actual || 0) }}
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
                    {{ formatNumber(row?.forecast?.lastYear || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(row?.forecast?.budget || 0) }}
                  </TableCell>
                  <TableCell class="text-right font-medium py-1">
                    {{ formatNumber(row?.forecast?.actual || 0) }}
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
              
              <!-- Total Cost of Sales Row -->
              <TableRow class="border-t-2 border-destructive bg-destructive/10 font-bold">
                <TableCell class="font-bold border-r border-table-border sticky left-0 bg-destructive/10 z-10 py-3">
                  TOTAL COST OF SALES
                </TableCell>
                <!-- Current Month -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.currentMonth?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.currentMonth?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.currentMonth?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Year to Date -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.yearToDate?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.yearToDate?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.yearToDate?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Forecast -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.forecast?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.forecast?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.forecast?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>


    <!-- Gross Profit Table -->
    <div class="mt-8"></div>
    <Card class="bg-gradient-card shadow-dashboard-lg border-table-border">
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
        </div>
      </CardHeader>
      <CardContent class="p-0" v-if="!minimizeGrossProfit">
        <div class="overflow-x-auto">
          <Table>
            <TableHeader class="bg-table-header">
              <TableRow class="border-table-border">
                <TableHead class="w-auto min-w-[200px] max-w-[800px] border-r border-table-border sticky left-0 bg-table-header z-10 whitespace-nowrap">
                  <div class="text-dashboard-header font-semibold">Calculation</div>
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
                  :class="`text-center text-dashboard-subheader py-1 ${idx < 4 ? 'border-r border-table-border' : ''}`"
                >
                  <div class="text-xs">{{ header }}</div>
                </TableHead>
              </TableRow>
            </TableHeader>
            
            <TableBody>
              <!-- Total Revenue Row -->
              <TableRow class="bg-primary/10 font-semibold">
                <TableCell class="font-semibold border-r border-table-border sticky left-0 bg-primary/10 z-10 py-3">
                  Total Revenue
                </TableCell>
                <!-- Current Month -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.currentMonth?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.currentMonth?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.currentMonth?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Year to Date -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.yearToDate?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.yearToDate?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.yearToDate?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Forecast -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.forecast?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.forecast?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(revenueTotals.forecast?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              </TableRow>
              
              <!-- Total Cost of Sales Row -->
              <TableRow class="bg-destructive/10 font-semibold">
                <TableCell class="font-semibold border-r border-table-border sticky left-0 bg-destructive/10 z-10 py-3">
                  Total Cost of Sales
                </TableCell>
                <!-- Current Month -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.currentMonth?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.currentMonth?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.currentMonth?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Year to Date -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.yearToDate?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.yearToDate?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.yearToDate?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Forecast -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.forecast?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.forecast?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(costOfSalesTotals.forecast?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              </TableRow>
              
              <!-- Gross Profit Row -->
              <TableRow class="border-t-2 border-success bg-success/20 font-bold">
                <TableCell class="font-bold border-r border-table-border sticky left-0 bg-success/20 z-10 py-3">
                  GROSS PROFIT
                </TableCell>
                <!-- Current Month -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(grossProfitTotals.currentMonth?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(grossProfitTotals.currentMonth?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(grossProfitTotals.currentMonth?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Year to Date -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(grossProfitTotals.yearToDate?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(grossProfitTotals.yearToDate?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(grossProfitTotals.yearToDate?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Forecast -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(grossProfitTotals.forecast?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(grossProfitTotals.forecast?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(grossProfitTotals.forecast?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <!-- Salaries and Wages Table -->
    <div class="mt-8"></div>
    <Card class="bg-gradient-card shadow-dashboard-lg border-table-border">
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
                  <Button 
                    variant="ghost" 
                    @click="handleSort('category')"
                    class="h-auto p-0 font-semibold text-dashboard-header hover:bg-transparent"
                  >
                    <ArrowUpDown class="h-4 w-4" />
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
                  :class="`text-center text-dashboard-subheader py-1 ${idx < 4 ? 'border-r border-table-border' : ''}`"
                >
                  <div class="text-xs">{{ header }}</div>
                </TableHead>
              </TableRow>
            </TableHeader>
            
            <TableBody>
              <!-- Salaries and Wages Accounts -->
              <TableRow
                v-for="row in (props.hideZeroRows ? salariesWagesData.filter(hasData) : salariesWagesData)"
                :key="row.account"
                :class="getRowClass(row)"
              >
                <TableCell :class="getCategoryCellClass(row)">
                  {{ getCategoryDisplay(row) }}
                </TableCell>
                <!-- Current Month Data -->
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.currentMonth?.lastYear || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.currentMonth?.budget || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.currentMonth?.actual || 0) }}
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
                  {{ formatNumber(row?.yearToDate?.lastYear || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.yearToDate?.budget || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.yearToDate?.actual || 0) }}
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
                  {{ formatNumber(row?.forecast?.lastYear || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.forecast?.budget || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.forecast?.actual || 0) }}
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
              
              <!-- Total Salaries and Wages Row -->
              <TableRow class="border-t-2 border-warning bg-warning/10 font-bold">
                <TableCell class="font-bold border-r border-table-border sticky left-0 bg-warning/10 z-10 py-3">
                  TOTAL SALARIES AND WAGES
                </TableCell>
                <!-- Current Month -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.currentMonth?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.currentMonth?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.currentMonth?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Year to Date -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.yearToDate?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.yearToDate?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.yearToDate?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Forecast -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.forecast?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.forecast?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.forecast?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <!-- Payroll Burden Table -->
    <div class="mt-8"></div>
    <Card class="bg-gradient-card shadow-dashboard-lg border-table-border">
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
                  <Button 
                    variant="ghost" 
                    @click="handleSort('category')"
                    class="h-auto p-0 font-semibold text-dashboard-header hover:bg-transparent"
                  >
                    <ArrowUpDown class="h-4 w-4" />
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
                  :class="`text-center text-dashboard-subheader py-1 ${idx < 4 ? 'border-r border-table-border' : ''}`"
                >
                  <div class="text-xs">{{ header }}</div>
                </TableHead>
              </TableRow>
            </TableHeader>
            
            <TableBody>
              <!-- Payroll Burden Accounts -->
              <TableRow
                v-for="row in (props.hideZeroRows ? payrollBurdenData.filter(hasData) : payrollBurdenData)"
                :key="row.account"
                :class="getRowClass(row)"
              >
                <TableCell :class="getCategoryCellClass(row)">
                  {{ getCategoryDisplay(row) }}
                </TableCell>
                <!-- Current Month Data -->
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.currentMonth?.lastYear || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.currentMonth?.budget || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.currentMonth?.actual || 0) }}
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
                  {{ formatNumber(row?.yearToDate?.lastYear || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.yearToDate?.budget || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.yearToDate?.actual || 0) }}
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
                  {{ formatNumber(row?.forecast?.lastYear || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.forecast?.budget || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.forecast?.actual || 0) }}
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
              
              <!-- Total Payroll Burden Row -->
              <TableRow class="border-t-2 border-warning bg-warning/10 font-bold">
                <TableCell class="font-bold border-r border-table-border sticky left-0 bg-warning/10 z-10 py-3">
                  TOTAL PAYROLL BURDEN
                </TableCell>
                <!-- Current Month -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.currentMonth?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.currentMonth?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.currentMonth?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Year to Date -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.yearToDate?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.yearToDate?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.yearToDate?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Forecast -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.forecast?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.forecast?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.forecast?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <!-- Combined Payroll Total Table -->
    <div class="mt-8"></div>
    <Card class="bg-gradient-card shadow-dashboard-lg border-table-border">
      <CardHeader class="flex items-center justify-between px-4 py-2">
        <div class="flex items-center space-x-3">
          <Button 
            variant="ghost" 
            size="sm"
            @click="minimizeCombinedPayroll = !minimizeCombinedPayroll"
            class="p-1"
          >
            {{ minimizeCombinedPayroll ? '▶' : '▼' }}
          </Button>
          <CardTitle class="text-dashboard-header font-bold text-lg">Total Payroll Costs</CardTitle>
        </div>
      </CardHeader>
      <CardContent class="p-0" v-if="!minimizeCombinedPayroll">
        <div class="overflow-x-auto">
          <Table>
            <TableHeader class="bg-table-header">
              <TableRow class="border-table-border">
                <TableHead class="w-auto min-w-[200px] max-w-[800px] border-r border-table-border sticky left-0 bg-table-header z-10 whitespace-nowrap">
                  <div class="text-dashboard-header font-semibold">Summary</div>
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
                  :class="`text-center text-dashboard-subheader py-1 ${idx < 4 ? 'border-r border-table-border' : ''}`"
                >
                  <div class="text-xs">{{ header }}</div>
                </TableHead>
              </TableRow>
            </TableHeader>
            
            <TableBody>
              <!-- Total Salaries and Wages Summary Row -->
              <TableRow class="bg-warning/10 font-semibold">
                <TableCell class="font-semibold border-r border-table-border sticky left-0 bg-warning/10 z-10 py-3">
                  Total Salaries and Wages
                </TableCell>
                <!-- Current Month -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.currentMonth?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.currentMonth?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.currentMonth?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Year to Date -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.yearToDate?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.yearToDate?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.yearToDate?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Forecast -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.forecast?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.forecast?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(salariesWagesTotals.forecast?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              </TableRow>
              
              <!-- Total Payroll Burden Summary Row -->
              <TableRow class="bg-warning/10 font-semibold">
                <TableCell class="font-semibold border-r border-table-border sticky left-0 bg-warning/10 z-10 py-3">
                  Total Payroll Burden
                </TableCell>
                <!-- Current Month -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.currentMonth?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.currentMonth?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.currentMonth?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Year to Date -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.yearToDate?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.yearToDate?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.yearToDate?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Forecast -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.forecast?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.forecast?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(payrollBurdenTotals.forecast?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              </TableRow>
              
              <!-- Combined Total Payroll Row -->
              <TableRow class="border-t-4 border-primary bg-primary/20 font-bold text-lg">
                <TableCell class="font-bold border-r border-table-border sticky left-0 bg-primary/20 z-10 py-3">
                  TOTAL PAYROLL COSTS
                </TableCell>
                <!-- Current Month -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedPayrollTotals.currentMonth?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedPayrollTotals.currentMonth?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedPayrollTotals.currentMonth?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Year to Date -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedPayrollTotals.yearToDate?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedPayrollTotals.yearToDate?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedPayrollTotals.yearToDate?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Forecast -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedPayrollTotals.forecast?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedPayrollTotals.forecast?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedPayrollTotals.forecast?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>

    <!-- Other Expenses Table -->
    <div class="mt-8"></div>
    <Card class="bg-gradient-card shadow-dashboard-lg border-table-border">
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
                  <Button 
                    variant="ghost" 
                    @click="handleSort('category')"
                    class="h-auto p-0 font-semibold text-dashboard-header hover:bg-transparent"
                  >
                    <ArrowUpDown class="h-4 w-4" />
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
                  :class="`text-center text-dashboard-subheader py-1 ${idx < 4 ? 'border-r border-table-border' : ''}`"
                >
                  <div class="text-xs">{{ header }}</div>
                </TableHead>
              </TableRow>
            </TableHeader>
            
            <TableBody>
              <!-- Other Expenses Accounts -->
              <TableRow
                v-for="row in (props.hideZeroRows ? combinedOtherExpensesData.filter(hasData) : combinedOtherExpensesData)"
                :key="row.account"
                :class="getRowClass(row)"
              >
                <TableCell :class="getCategoryCellClass(row)">
                  {{ getCategoryDisplay(row) }}
                </TableCell>
                <!-- Current Month Data -->
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.currentMonth?.lastYear || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.currentMonth?.budget || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.currentMonth?.actual || 0) }}
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
                  {{ formatNumber(row?.yearToDate?.lastYear || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.yearToDate?.budget || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.yearToDate?.actual || 0) }}
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
                  {{ formatNumber(row?.forecast?.lastYear || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.forecast?.budget || 0) }}
                </TableCell>
                <TableCell class="text-right font-medium py-1">
                  {{ formatNumber(row?.forecast?.actual || 0) }}
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
              
              <!-- Total Other Expenses Row -->
              <TableRow class="border-t-2 border-slate-500 bg-slate-500/10 font-bold">
                <TableCell class="font-bold border-r border-table-border sticky left-0 bg-slate-500/10 z-10 py-3">
                  TOTAL OTHER EXPENSES
                </TableCell>
                <!-- Current Month -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedOtherExpensesTotals.currentMonth?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedOtherExpensesTotals.currentMonth?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedOtherExpensesTotals.currentMonth?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Year to Date -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedOtherExpensesTotals.yearToDate?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedOtherExpensesTotals.yearToDate?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedOtherExpensesTotals.yearToDate?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <!-- Forecast -->
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedOtherExpensesTotals.forecast?.lastYear || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedOtherExpensesTotals.forecast?.budget || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3">{{ formatNumber(combinedOtherExpensesTotals.forecast?.actual || 0) }}</TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
                <TableCell class="text-right border-r border-table-border py-3"></TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui'
import { Button } from '@/components/ui'
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
  },
  hideZeroRows: {
    type: Boolean,
    default: false
  }
})

// Toggle to minimize tables
const minimizeIncome = ref(false)
const minimizeIncomeSeparate = ref(false)
const minimizeExpense = ref(false)
const minimizeGrossProfit = ref(false)
const minimizeSalariesWages = ref(false)
const minimizePayrollBurden = ref(false)
const minimizeCombinedPayroll = ref(false)
const minimizeOtherExpenses = ref(false)

// Utility function for number formatting
const formatNumber = (value) => {
  if (value === null || value === undefined || value === '') return '0'
  const num = Math.abs(Number(value))
  if (isNaN(num)) return '0'
  return num.toLocaleString('en-US', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
}

// Utility function for percentage formatting
const formatPercentage = (value) => {
  if (value === null || value === undefined || value === '' || isNaN(value)) return 'N/A'
  return `${Number(value).toFixed(1)}%`
}

// Returns true if any period has non-zero values
const hasData = (row) => {
  const periods = ['currentMonth', 'yearToDate', 'forecast']
  return periods.some(p => {
    const grp = row[p] || {}
    return Object.values(grp).some(val => {
      const numVal = Math.abs(Number(val))
      return numVal !== 0 && !isNaN(numVal) && val !== null && val !== undefined
    })
  })
}

// Calculate totals for a specific Cost of Sales section
const getSectionTotals = (section, period, metric) => {
  if (!section || !section.expenseAccounts || !Array.isArray(section.expenseAccounts)) {
    return 0
  }
  
  let total = 0
  section.expenseAccounts.forEach(account => {
    const value = account[period]?.[metric] || 0
    total += Math.abs(Number(value))
  })
  
  return total
}

// Calculate totals for a specific Revenue section
const getRevenueSectionTotals = (section, period, metric) => {
  if (!section || !section.incomeAccounts || !Array.isArray(section.incomeAccounts)) {
    return 0
  }
  
  let total = 0
  section.incomeAccounts.forEach(account => {
    const value = account[period]?.[metric] || 0
    total += Math.abs(Number(value))
  })
  
  return total
}

// Create backward-compatible structure for the existing template
const groupedDashboardData = computed(() => {
  // Use the hierarchical data directly from the API instead of hardcoding
  const incomeAccounts = (props.data || []).filter(row => 
    row.type === 'account' && row.root_type === 'Income'
  )
  
  if (incomeAccounts.length === 0) {
    return []
  }
  
  // Group accounts by their header sections
  const grouped = {}
  let currentHeader = 'Income'
  
  ;(props.data || []).forEach(row => {
    if (row.type === 'header' && row.root_type === 'Income') {
      currentHeader = row.category
      if (!grouped[currentHeader]) {
        grouped[currentHeader] = {
          name: currentHeader,
          subSections: [{
            accounts: []
          }]
        }
      }
    } else if (row.type === 'account' && row.root_type === 'Income') {
      // Find the appropriate header group
      let targetHeader = currentHeader
      // Look for the most recent header before this account
      for (let i = (props.data || []).indexOf(row) - 1; i >= 0; i--) {
        const prevRow = props.data[i]
        if (prevRow.type === 'header' && prevRow.root_type === 'Income') {
          targetHeader = prevRow.category
          break
        }
      }
      
      if (!grouped[targetHeader]) {
        grouped[targetHeader] = {
          name: targetHeader,
          subSections: [{
            accounts: []
          }]
        }
      }
      grouped[targetHeader].subSections[0].accounts.push(row)
    }
  })
  
  return Object.values(grouped)
})

// Use the hierarchical data directly from the API
const allIncomeData = computed(() => {
  return (props.data || []).filter(row => row.root_type === 'Income')
})

const expenseData = computed(() => {
  return (props.data || []).filter(row => row.root_type === 'Expense')
})

// Get main header (e.g., "INCOME")
const mainHeaderData = computed(() => {
  return (props.data || []).filter(row => row.type === 'main_header' && row.root_type === 'Income')
})

// Get sub headers (e.g., "Rooms Revenue", "Food Revenue")
const subHeaderData = computed(() => {
  return (props.data || []).filter(row => row.type === 'header' && row.root_type === 'Income')
})

// Get accounts for each sub header category
// Get accounts that belong to a specific header category - REMOVED, replaced with incomeData computed property

// Income data grouped by headers - similar to costOfSalesData
const groupedIncomeData = computed(() => {
  // Get all income accounts
  const incomeAccounts = (props.data || []).filter(row => 
    row.type === 'account' && row.root_type === 'Income'
  )
  
  // Group accounts by their header categories using more specific logic
  const grouped = {}
  
  // Initialize groups for known header categories
  const knownHeaders = ['Rooms Revenue', 'Food Revenue', 'Beverage Revenue', 'Other Revenue']
  knownHeaders.forEach(header => {
    grouped[header] = {
      name: header,
      incomeAccounts: []
    }
  })
  
  // Group accounts based on account codes and names
  incomeAccounts.forEach(account => {
    const accountCode = account.account || ''
    const accountName = account.category || ''
    
    // Extract account code from the account field
    let extractedCode = ''
    if (accountCode && typeof accountCode === 'string') {
      if (accountCode.includes(' - ')) {
        extractedCode = accountCode.split(' - ')[0]
      } else {
        extractedCode = accountCode
      }
    }
    
    // Determine which header this account belongs to
    let targetHeader = 'Other Revenue' // default
    
    // Rooms Revenue - accounts starting with 400xx or containing 'room' in name
    if (extractedCode.startsWith('400') || accountName.toLowerCase().includes('room')) {
      targetHeader = 'Rooms Revenue'
    }
    // Food Revenue - accounts starting with 401xx or containing 'food' in name
    else if (extractedCode.startsWith('401') || accountName.toLowerCase().includes('food')) {
      targetHeader = 'Food Revenue'
    }
    // Beverage Revenue - accounts starting with 402xx or containing 'beverage' in name
    else if (extractedCode.startsWith('402') || accountName.toLowerCase().includes('beverage')) {
      targetHeader = 'Beverage Revenue'
    }
    // Other Revenue - accounts starting with 403xx, 404xx, 411xx or other patterns
    else if (extractedCode.startsWith('403') || extractedCode.startsWith('404') || 
             extractedCode.startsWith('411') || 
             (!extractedCode.startsWith('400') && !extractedCode.startsWith('401') && !extractedCode.startsWith('402'))) {
      targetHeader = 'Other Revenue'
    }
    
    // Add account to the appropriate group
    if (grouped[targetHeader]) {
      grouped[targetHeader].incomeAccounts.push(account)
    }
  })
  
  return Object.values(grouped)
})

// Calculate totals for each income header category using the grouped data
const getHeaderTotals = (headerCategory) => {
  // Find the section in groupedIncomeData that matches the header category
  const section = groupedIncomeData.value.find(s => s.name === headerCategory)
  
  if (!section || !section.incomeAccounts || !Array.isArray(section.incomeAccounts)) {
    return {
      currentMonth: { lastYear: 0, budget: 0, actual: 0 },
      yearToDate: { lastYear: 0, budget: 0, actual: 0 },
      forecast: { lastYear: 0, budget: 0, actual: 0 }
    }
  }
  
  const totals = {
    currentMonth: { lastYear: 0, budget: 0, actual: 0 },
    yearToDate: { lastYear: 0, budget: 0, actual: 0 },
    forecast: { lastYear: 0, budget: 0, actual: 0 }
  }
  
  section.incomeAccounts.forEach(account => {
    totals.currentMonth.lastYear += Math.abs(account.currentMonth?.lastYear || 0)
    totals.currentMonth.budget += Math.abs(account.currentMonth?.budget || 0)
    totals.currentMonth.actual += Math.abs(account.currentMonth?.actual || 0)
    totals.yearToDate.lastYear += Math.abs(account.yearToDate?.lastYear || 0)
    totals.yearToDate.budget += Math.abs(account.yearToDate?.budget || 0)
    totals.yearToDate.actual += Math.abs(account.yearToDate?.actual || 0)
    totals.forecast.lastYear += Math.abs(account.forecast?.lastYear || 0)
    totals.forecast.budget += Math.abs(account.forecast?.budget || 0)
    totals.forecast.actual += Math.abs(account.forecast?.actual || 0)
  })
  
  return totals
}

// Cost of Sales data - get accounts that are specifically cost of sales related
const costOfSalesData = computed(() => {
  // Get cost of sales accounts based on account codes and names
  const costOfSalesPatterns = [
    '500', '501', '502', '503', '504', '505', '506', '507', '508', '509', // Cost of Sales account codes
    'Cost of Sales', 'Cost of Food', 'Cost of Beverage', 'Beverage Cost', 'Food Cost', 'Stock',
    'Direct Allocation', 'Sundry Cost', 'Kitchen', 'F&B'
  ]
  
  const expenseData = (props.data || []).filter(row => 
    row.type === 'account' && 
    row.root_type === 'Expense' &&
    (costOfSalesPatterns.some(pattern => 
      (row.account && row.account.startsWith(pattern)) ||
      (row.category && row.category.includes(pattern))
    ))
  )
  
  // Group by the most recent header before each account
  const grouped = {}
  let currentHeader = 'Cost of Sales'
  
  ;(props.data || []).forEach(row => {
    if (row.type === 'header' && row.root_type === 'Expense') {
      currentHeader = row.category
    } else if (row.type === 'account' && row.root_type === 'Expense' && expenseData.includes(row)) {
      // Find the most recent header before this account
      let targetHeader = currentHeader
      for (let i = (props.data || []).indexOf(row) - 1; i >= 0; i--) {
        const prevRow = props.data[i]
        if (prevRow.type === 'header' && prevRow.root_type === 'Expense') {
          targetHeader = prevRow.category
          break
        }
      }
      
      if (!grouped[targetHeader]) {
        grouped[targetHeader] = {
          name: targetHeader,
          expenseAccounts: []
        }
      }
      grouped[targetHeader].expenseAccounts.push(row)
    }
  })
  
  return Object.values(grouped)
})

// Salaries and Wages Data - get basic salary accounts (600xx accounts only)
const salariesWagesData = computed(() => {
  return (props.data || []).filter(row => {
    if (row.type !== 'account' || row.root_type !== 'Expense') return false
    
    // Extract account code from the account field
    const accountCode = row.account || ''
    let extractedCode = ''
    
    if (accountCode && typeof accountCode === 'string') {
      if (accountCode.includes(' - ')) {
        extractedCode = accountCode.split(' - ')[0]
      } else {
        extractedCode = accountCode
      }
    }
    
    // Only include accounts starting with 600xx (strict filtering)
    return extractedCode.startsWith('600')
  })
})

// Payroll Burden Data - get specific payroll-related accounts only
const payrollBurdenData = computed(() => {
  return (props.data || []).filter(row => {
    if (row.type !== 'account' || row.root_type !== 'Expense') return false
    
    // Extract account code from the account field
    const accountCode = row.account || ''
    let extractedCode = ''
    
    if (accountCode && typeof accountCode === 'string') {
      if (accountCode.includes(' - ')) {
        extractedCode = accountCode.split(' - ')[0]
      } else {
        extractedCode = accountCode
      }
    }
    
    // Only include specific payroll burden accounts (not all 610xx+)
    // These are accounts that are specifically related to payroll burden
    const payrollBurdenAccounts = [
      '61000', '61100', '61200', '61300', '61400', '61500', '61600', '61700', '61800', '61900', // Marketing & Promotions
      '62000', '62100', '62200', '62300', '62400', '62500', '62600', '62700', '62800', '62900', // Travel & Consultants
      '63000', '63100', '63200', '63300', '63400', '63500', '63600', '63700', '63800', '63900', // Communication & Entertainment
      '64000', '64100', '64200', '64300', '64400', '64500', '64600', '64700', '64800', '64900', // Training & Office
      '65000', '65100', '65200', '65300', '65400', '65500', '65600', '65700', '65800', '65900', // Financial & Banking
      '66000', '66100', '66200', '66300', '66400', '66500', '66600', '66700', '66800', '66900', // IT & Technology
      '67000', '67100', '67200', '67300', '67400', '67500', '67600', '67700', '67800', '67900', // Entertainment & Guest Services
      '68000', '68100', '68200', '68300', '68400', '68500', '68600', '68700', '68800', '68900', // Sales & Marketing
      '69000', '69100', '69200', '69300', '69400', '69500', '69600', '69700', '69800', '69900', // Advertising & Graphics
      '70000', '70100', '70200', '70300', '70400', '70500', '70600', '70700', '70800', '70900'  // Photography & Promotional
    ]
    
    return payrollBurdenAccounts.some(code => extractedCode.startsWith(code))
  })
})

// Combined Other Expenses Data - includes Operating, Administrative, and Other expenses
// Excludes Direct Expenses (500xx), Salaries & Wages (600xx), and Payroll Burden accounts
const combinedOtherExpensesData = computed(() => {
  return (props.data || []).filter(row => {
    if (row.type !== 'account' || row.root_type !== 'Expense') return false
    
    // Extract account code from the account field
    const accountCode = row.account || ''
    let extractedCode = ''
    
    if (accountCode && typeof accountCode === 'string') {
      if (accountCode.includes(' - ')) {
        extractedCode = accountCode.split(' - ')[0]
      } else {
        extractedCode = accountCode
      }
    }
    
    // Exclude Direct Expenses (500xx) and Salaries & Wages (600xx)
    // Also exclude accounts that are in Payroll Burden table
    const excludedPayrollBurdenAccounts = [
      '61000', '61100', '61200', '61300', '61400', '61500', '61600', '61700', '61800', '61900', // Marketing & Promotions
      '62000', '62100', '62200', '62300', '62400', '62500', '62600', '62700', '62800', '62900', // Travel & Consultants
      '63000', '63100', '63200', '63300', '63400', '63500', '63600', '63700', '63800', '63900', // Communication & Entertainment
      '64000', '64100', '64200', '64300', '64400', '64500', '64600', '64700', '64800', '64900', // Training & Office
      '65000', '65100', '65200', '65300', '65400', '65500', '65600', '65700', '65800', '65900', // Financial & Banking
      '66000', '66100', '66200', '66300', '66400', '66500', '66600', '66700', '66800', '66900', // IT & Technology
      '67000', '67100', '67200', '67300', '67400', '67500', '67600', '67700', '67800', '67900', // Entertainment & Guest Services
      '68000', '68100', '68200', '68300', '68400', '68500', '68600', '68700', '68800', '68900', // Sales & Marketing
      '69000', '69100', '69200', '69300', '69400', '69500', '69600', '69700', '69800', '69900', // Advertising & Graphics
      '70000', '70100', '70200', '70300', '70400', '70500', '70600', '70700', '70800', '70900'  // Photography & Promotional
    ]
    
    // Check if this account is excluded from Payroll Burden
    const isExcludedFromPayrollBurden = excludedPayrollBurdenAccounts.some(code => extractedCode.startsWith(code))
    
    // Only include accounts starting with 610xx and above, but exclude Payroll Burden accounts
    const isIndirectExpense = extractedCode.startsWith('61') || 
                             extractedCode.startsWith('62') || 
                             extractedCode.startsWith('63') || 
                             extractedCode.startsWith('64') || 
                             extractedCode.startsWith('65') || 
                             extractedCode.startsWith('66') || 
                             extractedCode.startsWith('67') || 
                             extractedCode.startsWith('68') || 
                             extractedCode.startsWith('69') || 
                             extractedCode.startsWith('70') || 
                             extractedCode.startsWith('71') || 
                             extractedCode.startsWith('72') || 
                             extractedCode.startsWith('73') || 
                             extractedCode.startsWith('74') || 
                             extractedCode.startsWith('75') || 
                             extractedCode.startsWith('76') || 
                             extractedCode.startsWith('77') || 
                             extractedCode.startsWith('78') || 
                             extractedCode.startsWith('79') || 
                             extractedCode.startsWith('80') || 
                             extractedCode.startsWith('81') || 
                             extractedCode.startsWith('82') || 
                             extractedCode.startsWith('83') || 
                             extractedCode.startsWith('84') || 
                             extractedCode.startsWith('85') || 
                             extractedCode.startsWith('86') || 
                             extractedCode.startsWith('87') || 
                             extractedCode.startsWith('88') || 
                             extractedCode.startsWith('89') || 
                             extractedCode.startsWith('90') || 
                             extractedCode.startsWith('91') || 
                             extractedCode.startsWith('92') || 
                             extractedCode.startsWith('93') || 
                             extractedCode.startsWith('94') || 
                             extractedCode.startsWith('95') || 
                             extractedCode.startsWith('96') || 
                             extractedCode.startsWith('97') || 
                             extractedCode.startsWith('98') || 
                             extractedCode.startsWith('99')
    
    return isIndirectExpense && !isExcludedFromPayrollBurden
  })
})

// Validation: Check for duplicate accounts across tables
const validateAccountSeparation = computed(() => {
  const salariesAccounts = salariesWagesData.value.map(acc => acc.account)
  const payrollBurdenAccounts = payrollBurdenData.value.map(acc => acc.account)
  const otherExpensesAccounts = combinedOtherExpensesData.value.map(acc => acc.account)
  
  // Check for duplicates between Salaries and Payroll Burden
  const salariesPayrollDuplicates = salariesAccounts.filter(acc => payrollBurdenAccounts.includes(acc))
  
  // Check for duplicates between Salaries and Other Expenses
  const salariesOtherDuplicates = salariesAccounts.filter(acc => otherExpensesAccounts.includes(acc))
  
  // Check for duplicates between Payroll Burden and Other Expenses
  const payrollOtherDuplicates = payrollBurdenAccounts.filter(acc => otherExpensesAccounts.includes(acc))
  
  return {
    hasDuplicates: salariesPayrollDuplicates.length > 0 || salariesOtherDuplicates.length > 0 || payrollOtherDuplicates.length > 0,
    salariesPayrollDuplicates,
    salariesOtherDuplicates,
    payrollOtherDuplicates,
    totalAccounts: {
      salaries: salariesAccounts.length,
      payrollBurden: payrollBurdenAccounts.length,
      otherExpenses: otherExpensesAccounts.length
    }
  }
})

// Revenue totals calculation
const revenueTotals = computed(() => {
  let totals = {
    currentMonth: { lastYear: 0, budget: 0, actual: 0 },
    yearToDate: { lastYear: 0, budget: 0, actual: 0 },
    forecast: { lastYear: 0, budget: 0, actual: 0 }
  }
  
  groupedDashboardData.value.forEach(section => {
    section.subSections[0]?.accounts?.forEach(account => {
      totals.currentMonth.lastYear += Math.abs(account.currentMonth?.lastYear || 0)
      totals.currentMonth.budget += Math.abs(account.currentMonth?.budget || 0)
      totals.currentMonth.actual += Math.abs(account.currentMonth?.actual || 0)
      totals.yearToDate.lastYear += Math.abs(account.yearToDate?.lastYear || 0)
      totals.yearToDate.budget += Math.abs(account.yearToDate?.budget || 0)
      totals.yearToDate.actual += Math.abs(account.yearToDate?.actual || 0)
      totals.forecast.lastYear += Math.abs(account.forecast?.lastYear || 0)
      totals.forecast.budget += Math.abs(account.forecast?.budget || 0)
      totals.forecast.actual += Math.abs(account.forecast?.actual || 0)
    })
  })
  
  return totals
})

// Cost of Sales totals calculation
const costOfSalesTotals = computed(() => {
  let totals = {
    currentMonth: { lastYear: 0, budget: 0, actual: 0 },
    yearToDate: { lastYear: 0, budget: 0, actual: 0 },
    forecast: { lastYear: 0, budget: 0, actual: 0 }
  }
  
  costOfSalesData.value.forEach(section => {
    section.expenseAccounts?.forEach(account => {
      totals.currentMonth.lastYear += Math.abs(account.currentMonth?.lastYear || 0)
      totals.currentMonth.budget += Math.abs(account.currentMonth?.budget || 0)
      totals.currentMonth.actual += Math.abs(account.currentMonth?.actual || 0)
      totals.yearToDate.lastYear += Math.abs(account.yearToDate?.lastYear || 0)
      totals.yearToDate.budget += Math.abs(account.yearToDate?.budget || 0)
      totals.yearToDate.actual += Math.abs(account.yearToDate?.actual || 0)
      totals.forecast.lastYear += Math.abs(account.forecast?.lastYear || 0)
      totals.forecast.budget += Math.abs(account.forecast?.budget || 0)
      totals.forecast.actual += Math.abs(account.forecast?.actual || 0)
    })
  })
  
  return totals
})

// Direct Expenses Totals - sum of all Direct Expenses (500xx accounts)
const directExpensesTotals = computed(() => {
  let totals = {
    currentMonth: { lastYear: 0, budget: 0, actual: 0 },
    yearToDate: { lastYear: 0, budget: 0, actual: 0 },
    forecast: { lastYear: 0, budget: 0, actual: 0 }
  }
  
  // Sum all Direct Expenses (500xx accounts) from the main data
  ;(props.data || []).forEach(row => {
    if (row.type === 'account' && row.root_type === 'Expense' && row.account && row.account.startsWith('500')) {
      totals.currentMonth.lastYear += Math.abs(row.currentMonth?.lastYear || 0)
      totals.currentMonth.budget += Math.abs(row.currentMonth?.budget || 0)
      totals.currentMonth.actual += Math.abs(row.currentMonth?.actual || 0)
      totals.yearToDate.lastYear += Math.abs(row.yearToDate?.lastYear || 0)
      totals.yearToDate.budget += Math.abs(row.yearToDate?.budget || 0)
      totals.yearToDate.actual += Math.abs(row.yearToDate?.actual || 0)
      totals.forecast.lastYear += Math.abs(row.forecast?.lastYear || 0)
      totals.forecast.budget += Math.abs(row.forecast?.budget || 0)
      totals.forecast.actual += Math.abs(row.forecast?.actual || 0)
    }
  })
  
  return totals
})

// Gross Profit Totals
const grossProfitTotals = computed(() => {
  const revenue = revenueTotals.value
  const costOfSales = costOfSalesTotals.value
  return {
    currentMonth: {
      lastYear: (revenue.currentMonth?.lastYear || 0) - (costOfSales.currentMonth?.lastYear || 0),
      budget: (revenue.currentMonth?.budget || 0) - (costOfSales.currentMonth?.budget || 0),
      actual: (revenue.currentMonth?.actual || 0) - (costOfSales.currentMonth?.actual || 0)
    },
    yearToDate: {
      lastYear: (revenue.yearToDate?.lastYear || 0) - (costOfSales.yearToDate?.lastYear || 0),
      budget: (revenue.yearToDate?.budget || 0) - (costOfSales.yearToDate?.budget || 0),
      actual: (revenue.yearToDate?.actual || 0) - (costOfSales.yearToDate?.actual || 0)
    },
    forecast: {
      lastYear: (revenue.forecast?.lastYear || 0) - (costOfSales.forecast?.lastYear || 0),
      budget: (revenue.forecast?.budget || 0) - (costOfSales.forecast?.budget || 0),
      actual: (revenue.forecast?.actual || 0) - (costOfSales.forecast?.actual || 0)
    }
  }
})

// Salaries and Wages Totals
const salariesWagesTotals = computed(() => {
  let totals = {
    currentMonth: { lastYear: 0, budget: 0, actual: 0 },
    yearToDate: { lastYear: 0, budget: 0, actual: 0 },
    forecast: { lastYear: 0, budget: 0, actual: 0 }
  };
  (salariesWagesData.value || []).forEach(account => {
    totals.currentMonth.lastYear += Math.abs(account.currentMonth?.lastYear || 0)
    totals.currentMonth.budget += Math.abs(account.currentMonth?.budget || 0)
    totals.currentMonth.actual += Math.abs(account.currentMonth?.actual || 0)
    totals.yearToDate.lastYear += Math.abs(account.yearToDate?.lastYear || 0)
    totals.yearToDate.budget += Math.abs(account.yearToDate?.budget || 0)
    totals.yearToDate.actual += Math.abs(account.yearToDate?.actual || 0)
    totals.forecast.lastYear += Math.abs(account.forecast?.lastYear || 0)
    totals.forecast.budget += Math.abs(account.forecast?.budget || 0)
    totals.forecast.actual += Math.abs(account.forecast?.actual || 0)
  })
  return totals
})

// Payroll Burden Totals
const payrollBurdenTotals = computed(() => {
  let totals = {
    currentMonth: { lastYear: 0, budget: 0, actual: 0 },
    yearToDate: { lastYear: 0, budget: 0, actual: 0 },
    forecast: { lastYear: 0, budget: 0, actual: 0 }
  };
  (payrollBurdenData.value || []).forEach(account => {
    totals.currentMonth.lastYear += Math.abs(account.currentMonth?.lastYear || 0)
    totals.currentMonth.budget += Math.abs(account.currentMonth?.budget || 0)
    totals.currentMonth.actual += Math.abs(account.currentMonth?.actual || 0)
    totals.yearToDate.lastYear += Math.abs(account.yearToDate?.lastYear || 0)
    totals.yearToDate.budget += Math.abs(account.yearToDate?.budget || 0)
    totals.yearToDate.actual += Math.abs(account.yearToDate?.actual || 0)
    totals.forecast.lastYear += Math.abs(account.forecast?.lastYear || 0)
    totals.forecast.budget += Math.abs(account.forecast?.budget || 0)
    totals.forecast.actual += Math.abs(account.forecast?.actual || 0)
  })
  return totals
})

// Combined Payroll Totals
const combinedPayrollTotals = computed(() => {
  const salaries = salariesWagesTotals.value
  const burden = payrollBurdenTotals.value
  return {
    currentMonth: {
      lastYear: (salaries.currentMonth?.lastYear || 0) + (burden.currentMonth?.lastYear || 0),
      budget: (salaries.currentMonth?.budget || 0) + (burden.currentMonth?.budget || 0),
      actual: (salaries.currentMonth?.actual || 0) + (burden.currentMonth?.actual || 0)
    },
    yearToDate: {
      lastYear: (salaries.yearToDate?.lastYear || 0) + (burden.yearToDate?.lastYear || 0),
      budget: (salaries.yearToDate?.budget || 0) + (burden.yearToDate?.budget || 0),
      actual: (salaries.yearToDate?.actual || 0) + (burden.yearToDate?.actual || 0)
    },
    forecast: {
      lastYear: (salaries.forecast?.lastYear || 0) + (burden.forecast?.lastYear || 0),
      budget: (salaries.forecast?.budget || 0) + (burden.forecast?.budget || 0),
      actual: (salaries.forecast?.actual || 0) + (burden.forecast?.actual || 0)
    }
  }
})

// Combined Other Expenses Totals
const combinedOtherExpensesTotals = computed(() => {
  let totals = {
    currentMonth: { lastYear: 0, budget: 0, actual: 0 },
    yearToDate: { lastYear: 0, budget: 0, actual: 0 },
    forecast: { lastYear: 0, budget: 0, actual: 0 }
  };
  (combinedOtherExpensesData.value || []).forEach(account => {
    totals.currentMonth.lastYear += Math.abs(account.currentMonth?.lastYear || 0)
    totals.currentMonth.budget += Math.abs(account.currentMonth?.budget || 0)
    totals.currentMonth.actual += Math.abs(account.currentMonth?.actual || 0)
    totals.yearToDate.lastYear += Math.abs(account.yearToDate?.lastYear || 0)
    totals.yearToDate.budget += Math.abs(account.yearToDate?.budget || 0)
    totals.yearToDate.actual += Math.abs(account.yearToDate?.actual || 0)
    totals.forecast.lastYear += Math.abs(account.forecast?.lastYear || 0)
    totals.forecast.budget += Math.abs(account.forecast?.budget || 0)
    totals.forecast.actual += Math.abs(account.forecast?.actual || 0)
  })
  return totals
})

// Row styling functions
const getRowClass = (row) => {
  if (row?.type === 'header') return 'bg-table-header font-semibold'
  if (row?.type === 'total') return 'border-t-2 border-primary bg-primary/10 font-bold'
  return 'hover:bg-muted/50'
}

const getCategoryCellClass = (row) => {
  const baseClass = 'border-r border-table-border sticky left-0 z-10 py-1'
  if (row?.type === 'header') return `${baseClass} bg-table-header font-semibold`
  if (row?.type === 'total') return `${baseClass} bg-primary/10 font-bold`
  return `${baseClass} bg-background`
}

const getCategoryDisplay = (row) => {
  return row?.category || row?.account || 'Unknown'
}

const getPercentageClass = (value) => {
  if (typeof value === 'string' || value === null || value === undefined) return ''
  if (value > 0) return 'text-success'
  if (value < 0) return 'text-destructive'
  return ''
}

const handleSort = (field) => {
  console.log('Sorting by:', field)
  // Sorting logic would go here
}

// Get expense header totals - only for Direct Expenses
const getExpenseHeaderTotals = (headerCategory) => {
  const accounts = []
  
  // Find the header row first
  const headerIndex = (props.data || []).findIndex(row => 
    row.type === 'header' && row.category === headerCategory && row.root_type === 'Expense'
  )
  
  if (headerIndex === -1) {
    console.warn(`Expense header '${headerCategory}' not found`)
    return []
  }
  
  // Look for accounts that belong to this specific header category
  for (let i = headerIndex + 1; i < (props.data || []).length; i++) {
    const row = props.data[i]
    
    // Stop if we hit another header or a different root type
    if (row.type === 'header' || row.root_type !== 'Expense') {
      break
    }
    
    // Only include accounts that actually belong to this header category AND are Direct Expenses
    if (row.type === 'account') {
      const accountCode = row.account || ''
      const accountName = row.category || ''
      
      // Extract account code from the account field
      let extractedCode = ''
      if (accountCode && typeof accountCode === 'string') {
        if (accountCode.includes(' - ')) {
          extractedCode = accountCode.split(' - ')[0]
        } else {
          extractedCode = accountCode
        }
      }
      
      // ONLY include Direct Expenses (500xx accounts)
      if (!extractedCode.startsWith('500')) {
        continue // Skip Indirect Expenses
      }
      
      // For Direct Expenses - check if account code starts with 500 or contains 'direct' in name
      if (headerCategory === 'Direct Expenses') {
        if (extractedCode.startsWith('500') || accountName.toLowerCase().includes('direct')) {
          accounts.push(row)
        }
      }
      // For Cost of Sales - check if account code starts with 500 or contains 'cost' in name
      else if (headerCategory === 'Cost of Sales') {
        if (extractedCode.startsWith('500') || accountName.toLowerCase().includes('cost')) {
          accounts.push(row)
        }
      }
      // For other categories, use the account name to determine if it belongs
      else {
        // Check if the account name contains keywords related to the header category
        const headerKeywords = headerCategory.toLowerCase().split(' ')
        const accountKeywords = accountName.toLowerCase().split(' ')
        
        // If there's any overlap in keywords, include the account
        const hasOverlap = headerKeywords.some(hk => 
          accountKeywords.some(ak => ak.includes(hk) || hk.includes(ak))
        )
        
        if (hasOverlap) {
          accounts.push(row)
        }
      }
    }
  }
  
  console.log(`Found ${accounts.length} Direct Expense accounts for header '${headerCategory}':`, 
    accounts.map(acc => `${acc.account} (${acc.category})`))
  
  const totals = {
    currentMonth: { lastYear: 0, budget: 0, actual: 0 },
    yearToDate: { lastYear: 0, budget: 0, actual: 0 },
    forecast: { lastYear: 0, budget: 0, actual: 0 }
  }
  
  accounts.forEach(account => {
    totals.currentMonth.lastYear += Math.abs(account.currentMonth?.lastYear || 0)
    totals.currentMonth.budget += Math.abs(account.currentMonth?.budget || 0)
    totals.currentMonth.actual += Math.abs(account.currentMonth?.actual || 0)
    totals.yearToDate.lastYear += Math.abs(account.yearToDate?.lastYear || 0)
    totals.yearToDate.budget += Math.abs(account.yearToDate?.budget || 0)
    totals.yearToDate.actual += Math.abs(account.yearToDate?.actual || 0)
    totals.forecast.lastYear += Math.abs(account.forecast?.lastYear || 0)
    totals.forecast.budget += Math.abs(account.forecast?.budget || 0)
    totals.forecast.actual += Math.abs(account.forecast?.actual || 0)
  })
  
  return totals
}

// Expense rows - filtered to remove unwanted sections and only include Direct Expenses
const expenseRows = computed(() => {
  let allExpenseRows = (props.data || []).filter(row => row.root_type === 'Expense')
  
  // Apply hideZeroRows filter if enabled
  if (props.hideZeroRows) {
    allExpenseRows = allExpenseRows.filter(hasData)
  }
  
  console.log('=== EXPENSE FILTERING DEBUG ===')
  console.log('Total expense rows before filtering:', allExpenseRows.length)
  
  // Define exactly what we want to keep
  const keepSections = ['EXPENSES', 'Direct Expenses', 'Cost of Sales']
  const unwantedSections = [
    'Total Food Cost', 'Total Beverage Cost', 'Total Function Cost', 'Total Sundry Cost',
    'Stock Expenses', 'Cost of Food', 'Cost of Sales - Kitchen & F&B', 
    'Cost of Sales - Beverage', 'Cost of Sales - Housekeeping & Laundry', 'Indirect Expenses'
  ]
  
  // Step 1: Find the main structure we want to keep
  const mainStructure = []
  let foundMainHeader = false
  let foundDirectExpenses = false
  let foundCostOfSales = false
  
  for (const row of allExpenseRows) {
    // Keep main header
    if (row.type === 'main_header' && row.category === 'EXPENSES') {
      mainStructure.push(row)
      foundMainHeader = true
      console.log('✓ Keeping main header:', row.category)
      continue
    }
    
    // Keep Direct Expenses header
    if (row.type === 'header' && row.category === 'Direct Expenses') {
      mainStructure.push(row)
      foundDirectExpenses = true
      console.log('✓ Keeping Direct Expenses header:', row.category)
      continue
    }
    
    // Keep Cost of Sales header
    if (row.type === 'header' && row.category === 'Cost of Sales') {
      mainStructure.push(row)
      foundCostOfSales = true
      console.log('✓ Keeping Cost of Sales header:', row.category)
      continue
    }
    
    // Skip all other headers
    if (row.type === 'header') {
      console.log('✗ Skipping unwanted header:', row.category)
      continue
    }
    
    // For account rows, only include Direct Expenses (500xx accounts)
    if (row.type === 'account') {
      // Extract account code
      let accountCode = ''
      if (row.account && typeof row.account === 'string') {
        if (row.account.includes(' - ')) {
          accountCode = row.account.split(' - ')[0]
        } else {
          accountCode = row.account
        }
      }
      
      // Only include 500xx accounts (Direct Expenses)
      if (accountCode.startsWith('500')) {
        mainStructure.push(row)
        console.log('✓ Keeping Direct Expense account:', row.account, 'Code:', accountCode)
      } else {
        console.log('✗ Skipping Indirect Expense account:', row.account, 'Code:', accountCode)
      }
    }
  }
  
  console.log('=== FILTERING RESULTS ===')
  console.log('Main structure found:', foundMainHeader, foundDirectExpenses, foundCostOfSales)
  console.log('Final filtered rows:', mainStructure.length)
  console.log('Sample filtered rows:', mainStructure.slice(0, 5).map(r => ({ type: r.type, category: r.category, account: r.account })))
  
  return mainStructure
})
</script>

