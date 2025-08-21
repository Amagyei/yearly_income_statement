import { session } from '../data/session'

// Debug flag for development
const DEBUG = false

class ApiService {
  constructor() {
    this.baseUrl = '/api/method'
    this.csrfToken = localStorage.getItem('csrf_token') || null // try load cached token
    this.csrfAttempted = false // avoid repeated failed attempts
    this.inFlight = new Map() // de-duplicate identical concurrent requests
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}/${endpoint}`
    
    const defaultOptions = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      },
      credentials: 'include', // Include cookies for authentication
      ...options
    }

    // Ensure CSRF token for non-GET requests (Frappe requires this)
    const methodUpper = (defaultOptions.method || 'GET').toUpperCase()
    if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(methodUpper)) {
      if (!this.csrfToken && !this.csrfAttempted) {
        // Try to fetch once; on failure, mark attempted to avoid repeated cost
        this.csrfToken = await this.getCSRFToken()
        this.csrfAttempted = true
      }
      if (this.csrfToken) {
        defaultOptions.headers['X-Frappe-CSRF-Token'] = this.csrfToken
      }
    }

    // Build a stable in-flight key for dedupe
    const bodyString = typeof defaultOptions.body === 'string' ? defaultOptions.body : JSON.stringify(defaultOptions.body || {})
    const inFlightKey = `${endpoint}::${methodUpper}::${bodyString}`
    if (this.inFlight.has(inFlightKey)) {
      if (DEBUG) console.log('Reusing in-flight request:', inFlightKey)
      return this.inFlight.get(inFlightKey)
    }

    const fetchPromise = (async () => {
      try {
        if (DEBUG) console.log('API Request:', { url, method: defaultOptions.method, headers: defaultOptions.headers })
        const response = await fetch(url, defaultOptions)
        if (!response.ok) {
          // Redirect to login only on auth errors
          if (response.status === 401 || response.status === 403) {
            window.location.href = '/login'
            return
          }
          // Throw error for caller to handle (e.g., CSRF 400)
          const text = await response.text()
          throw new Error(`Request failed (${response.status}): ${text}`)
        }
        const data = await response.json()
        if (DEBUG) console.log('API Response:', { endpoint, data })
        // Unwrap Frappe response so callers get plain objects/arrays
        return (data && data.message !== undefined) ? data.message : data
      } catch (error) {
        console.error('API request failed:', error)
        // Return mock data for testing
        return this.getMockData(endpoint, options)
      } finally {
        // Clear in-flight entry
        this.inFlight.delete(inFlightKey)
      }
    })()

    // Store and return the shared promise
    this.inFlight.set(inFlightKey, fetchPromise)
    return fetchPromise
  }


  // Dashboard Data Endpoints
  async getDashboardData(filters = {}) {
    return this.request('yearly_income_statement.api.get_dashboard_data', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
  }

  async getDirectRevenueData(filters = {}) {
    return this.request('yearly_income_statement.api.get_direct_revenue_data', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
  }

  async getCostOfSalesData(filters = {}) {
    return this.request('yearly_income_statement.api.get_cost_of_sales_data', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
  }

  async getIndirectExpensesData(filters = {}) {
    return this.request('yearly_income_statement.api.get_indirect_expenses_data', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
  }

  async getDashboardDataWithFramework(filters = {}, reportingFramework = '') {
    const enhancedFilters = { ...filters, reporting_framework: reportingFramework }
    return this.request('yearly_income_statement.api.get_dashboard_data', {
      method: 'POST',
      body: JSON.stringify({ filters: enhancedFilters })
    })
  }

  async getSummaryData(filters = {}) {
    return this.request('yearly_income_statement.api.get_summary_data', {
      method: 'POST',
      body: JSON.stringify({ filters })
    })
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
    if (DEBUG) console.log('API: getCostCenters response:', response)
    return response
  }

  /**
   * Get report classes, optionally filtered by framework
   * @param {string} framework - Optional framework name to filter by
   * @returns {Promise<Array>} Array of report classes
   */
  async getReportClasses(framework = null) {
    const endpoint = framework
      ? `yearly_income_statement.api.get_report_classes_api?framework=${encodeURIComponent(framework)}`
      : 'yearly_income_statement.api.get_report_classes_api'
    return this.request(endpoint)
  }

  /**
   * Get report classes by framework using POST method
   * @param {string} reportingFramework - Framework name
   * @returns {Promise<Array>} Array of report classes for the framework
   */
  async getReportClassesByFramework(reportingFramework) {
    return this.request('yearly_income_statement.api.get_report_classes_api', {
      method: 'POST',
      body: JSON.stringify({ reporting_framework: reportingFramework })
    })
  }

  /**
   * Get list of available reporting frameworks
   * @returns {Promise<Array>} Array of reporting frameworks
   */
  async getReportingFrameworks() {
    try {
      return this.request('frappe.client.get_list', {
        method: 'POST',
        body: JSON.stringify({
          doctype: 'Reporting Framework',
          fields: ['name', 'description'],
          limit_page_length: 100
        })
      })
    } catch (error) {
      if (DEBUG) console.error('Failed to get reporting frameworks:', error)
      // Return empty array as fallback
      return []
    }
  }

  async getCSRFToken() {
    try {
      // Attempt official endpoint; if server lacks module, this will fail once
      const response = await fetch('/api/method/frappe.csrf.get_csrf_token', {
        method: 'GET',
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        const token = data.message
        // Store in both private variable and localStorage
        this.csrfToken = token
        localStorage.setItem('csrf_token', token)
        if (DEBUG) console.log('CSRF Token fetched and stored')
        return token
      }
    } catch (error) {
      if (DEBUG) console.warn('Failed to get CSRF token:', error)
    }
    return ''
  }

  /**
   * Validate if a framework name exists in the system
   * @param {string} frameworkName - Framework name to validate
   * @returns {Promise<boolean>} True if framework exists, false otherwise
   */
  async validateFramework(frameworkName) {
    if (!frameworkName) return true // No framework means all are valid
    
    try {
      const frameworks = await this.getReportingFrameworks()
      return frameworks.some(f => f.name === frameworkName)
    } catch (error) {
      if (DEBUG) console.error('Framework validation failed:', error)
      return false
    }
  }

  /**
   * Get dashboard data with framework validation
   * @param {Object} filters - Dashboard filters
   * @param {string} framework - Optional framework name
   * @returns {Promise<Object>} Dashboard data
   * @throws {Error} If framework is invalid
   */
  async getDashboardDataWithValidation(filters = {}, framework = null) {
    if (framework && !(await this.validateFramework(framework))) {
      throw new Error(`Invalid reporting framework: ${framework}`)
    }
    
    const enhancedFilters = { ...filters }
    if (framework) {
      enhancedFilters.reporting_framework = framework
    }
    
    return this.getDashboardData(enhancedFilters)
  }

  // Export Endpoints
  async exportDashboardData(filters = {}, format = 'excel') {
    const response = await this.request('yearly_income_statement.api.get_dashboard_data', {
      method: 'POST',
      body: JSON.stringify({ filters, format })
    })
    if (DEBUG) console.log('API: exportDashboardData response:', response)
    return response
  }

  // Data Transformation Methods - Updated for new backend structure
  transformDashboardData(response) {
    if (!response || !response.dashboard_data) {
      return []
    }
    
    // Transform backend structured data format to frontend expected format
    // Preserve all new fields: type, indent, root_type, report_class
    return response.dashboard_data.map(item => {
      // Handle different row types from new backend
      const transformedItem = {
        type: item.type || 'account',
        category: item.category || item.account_name || item.account,
        account: item.account || '',
        root_type: item.root_type || '',
        indent: item.indent || 0, // Preserve ERPNext hierarchy indentation
        is_group: item.is_group || false,
        report_class: item.report_class || '', // Preserve report_class for grouping
        
        // Financial data - preserve the new pre-aggregated structure
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

  // Helper methods for data transformation
  transformSummaryData(data) {
    return data || {}
  }

  transformDirectRevenueData(data) {
    if (!data || !Array.isArray(data)) return []
    
    return data.map(item => ({
      account: item.account || item.account_name,
      account_name: item.account_name || item.account,
      report_class: item.report_class || '',
      is_direct: !!item.is_direct,
      monthly: item.monthly || {},
      // Keep full objects like main table
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
    }))
  }

  transformCostOfSalesData(data) {
    if (!data || !Array.isArray(data)) return []
    
    return data.map(item => ({
      account: item.account || item.account_name,
      account_name: item.account_name || item.account,
      report_class: item.report_class || '',
      is_direct: !!item.is_direct,
      monthly: item.monthly || {},
      // Keep full objects like main table
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
    }))
  }

  transformIndirectExpensesData(data) {
    if (!data || !Array.isArray(data)) return []
    
    return data.map(item => ({
      account: item.account || item.account_name,
      account_name: item.account_name || item.account,
      report_class: item.report_class || '',
      is_direct: !!item.is_direct,
      root_type: item.root_type || '',
      monthly: item.monthly || {},
      // Keep full objects like main table
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
    }))
  }

  calculateTotal(data) {
    if (!Array.isArray(data) || data.length === 0) {
      return { 
        currentMonth: { lastYear: 0, budget: 0, actual: 0 },
        yearToDate: { lastYear: 0, budget: 0, actual: 0 },
        forecast: { lastYear: 0, budget: 0, actual: 0 }
      }
    }

    const parseAmount = (value) => {
      if (value === null || value === undefined) return 0
      if (typeof value === 'number') return isNaN(value) ? 0 : value
      const cleaned = String(value).replace(/,/g, '').trim()
      const num = Number(cleaned)
      return isNaN(num) ? 0 : num
    }

    const initTotals = () => ({ lastYear: 0, budget: 0, actual: 0 })

    return data.reduce((total, item) => {
      total.currentMonth.lastYear += parseAmount(item.currentMonth?.lastYear)
      total.currentMonth.budget += parseAmount(item.currentMonth?.budget)
      total.currentMonth.actual += parseAmount(item.currentMonth?.actual)

      total.yearToDate.lastYear += parseAmount(item.yearToDate?.lastYear)
      total.yearToDate.budget += parseAmount(item.yearToDate?.budget)
      total.yearToDate.actual += parseAmount(item.yearToDate?.actual)

      total.forecast.lastYear += parseAmount(item.forecast?.lastYear)
      total.forecast.budget += parseAmount(item.forecast?.budget)
      total.forecast.actual += parseAmount(item.forecast?.actual)

      return total
    }, { currentMonth: initTotals(), yearToDate: initTotals(), forecast: initTotals() })
  }
}

export default new ApiService() 