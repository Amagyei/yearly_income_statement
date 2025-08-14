import { session } from '../data/session'

class ApiService {
  constructor() {
    this.baseUrl = '/api/method'
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}/${endpoint}`
    
    const defaultOptions = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include cookies for authentication
      ...options
    }

    try {
      const response = await fetch(url, defaultOptions)
      
      if (!response.ok) {
        // If we get a permission error, ask for login
        window.location.href = '/login'
        }
      
      const data = await response.json()
      console.log('API: Raw response data:', data)
      console.log('API: Data type:', typeof data)
      console.log('API: Data keys:', typeof data === 'object' ? Object.keys(data) : 'Not an object')
      
      // Unwrap Frappe response so callers get plain objects/arrays
      return (data && data.message !== undefined) ? data.message : data
    } catch (error) {
      console.error('API request failed:', error)
      // Return mock data for testing
      return this.getMockData(endpoint, options)
    }
  }


  // Dashboard Data Endpoints
  async getDashboardData(filters = {}) {
    return this.request('yearly_income_statement.api.get_dashboard_data', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
  }

  async getComprehensiveDashboardData(filters = {}) {
    const response = await this.request('yearly_income_statement.api.get_dashboard_data', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
    return response
  }

  async getSummaryData(filters = {}) {
    return this.request('yearly_income_statement.api.get_summary_data', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
  }

  // Historical Data Endpoints
  async getHistoricalData(filters = {}) {
    console.log('API: getHistoricalData called with filters:', filters)
    const response = await this.request('yearly_income_statement.api.get_dashboard_data', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
    console.log('API: getHistoricalData response:', response)
    return response
  }

  async getYtdData(filters = {}) {
    const response = await this.request('yearly_income_statement.api.get_dashboard_data', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
    console.log('API: getYtdData response:', response)
    return response
  }

  async getForecastCalculations(filters = {}) {
    const response = await this.request('yearly_income_statement.api.get_dashboard_data', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
    console.log('API: getForecastCalculations response:', response)
    return response
  }

  // Filter Data Endpoints
  async getCompanies() {
    return this.request('yearly_income_statement.api.get_companies')
  }

  async getFiscalYears() {
    return this.request('yearly_income_statement.api.get_fiscal_years')
  }

  async getCostCenters(filters = {}) {
    const response = await this.request('yearly_income_statement.api.get_cost_centers', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
    console.log('API: getCostCenters response:', response)
    return response
  }

  async getExpenseAccounts(filters = {}) {
    const response = await this.request('yearly_income_statement.api.get_expense_accounts', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
    console.log('API: getExpenseAccounts response:', response)
    return response
  }

  async getReportClasses() {
    return this.request('yearly_income_statement.api.get_report_classes_api')
  }

  async getGLEntriesWithReportClass(filters = {}) {
    const response = await this.request('yearly_income_statement.api.get_gl_entries_with_report_class_api', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
    console.log('API: getGLEntriesWithReportClass response:', response)
    return response
  }

  async getCSRFToken() {
    try {
      const response = await fetch('/api/method/frappe.csrf.get_csrf_token', {
        method: 'GET',
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        const token = data.message
        localStorage.setItem('csrf_token', token)
        return token
      }
    } catch (error) {
      console.error('Failed to get CSRF token:', error)
    }
    return ''
  }

  // Export Endpoints
  async exportDashboardData(filters = {}, format = 'excel') {
    const response = await this.request('yearly_income_statement.api.get_dashboard_data', {
      method: 'POST',
      body: JSON.stringify({ filters, format })
    })
    console.log('API: exportDashboardData response:', response)
    return response
  }

                // Data Transformation Methods
              transformDashboardData(response) {
                if (!response || !response.dashboard_data) {
                  return []
                }
                
                // Transform backend structured data format to frontend expected format
                return response.dashboard_data.map(item => {
                  // Handle different row types
                  const transformedItem = {
                    type: item.type || 'account',
                    category: item.category || item.account_name || item.account,
                    account: item.account || '',
                    root_type: item.root_type || '',
                    currentMonth: {
                      lastYear: Math.abs(item.currentMonth?.lastYear || 0),
                      budget: Math.abs(item.currentMonth?.budget || 0),
                      actual: Math.abs(item.currentMonth?.actual || 0),
                      actBudThisYear: item.currentMonth?.actBudThisYear || 'N/A',
                      actVsLastYear: item.currentMonth?.actVsLastYear || 'N/A'
                    },
                    yearToDate: {
                      lastYear: Math.abs(item.yearToDate?.lastYear || 0),
                      budget: Math.abs(item.yearToDate?.budget || 0),
                      actual: Math.abs(item.yearToDate?.actual || 0),
                      actBudThisYear: item.yearToDate?.actBudThisYear || 'N/A',
                      actVsLastYear: item.yearToDate?.actVsLastYear || 'N/A'
                    },
                    forecast: {
                      lastYear: Math.abs(item.forecast?.lastYear || 0),
                      budget: Math.abs(item.forecast?.budget || 0),
                      actual: Math.abs(item.forecast?.actual || 0),
                      actBudThisYear: item.forecast?.actBudThisYear || 'N/A',
                      actVsLastYear: item.forecast?.actVsLastYear || 'N/A'
                    }
                  }
                  
                  return transformedItem
                })
              }

  transformSummaryData(response) {
    if (!response || !response.summary) {
      return {}
    }
    
    // Ensure all summary values are positive
    const summary = response.summary
    return {
      totalBudget: Math.abs(summary.total_budget || 0),
      totalActual: Math.abs(summary.total_actual || 0),
      variance: Math.abs(summary.total_variance || 0),
      variancePercentage: Math.abs(summary.variance_percentage || 0)
    }
  }

  transformCompanies(response) {
    if (!Array.isArray(response)) {
      return []
    }
    return response.map(company => company.company_name || company.name)
  }

  transformFiscalYears(response) {
    if (!Array.isArray(response)) {
      return []
    }
    return response.map(fy => fy.name)
  }

  transformCostCenters(response) {
    if (!Array.isArray(response)) {
      return []
    }
    // Backend returns array of strings, not objects
    return response
  }

  transformExpenseAccounts(response) {
    if (!Array.isArray(response)) {
      return []
    }
    return response.map(account => account.account_name || account.name)
  }
}

export default new ApiService() 