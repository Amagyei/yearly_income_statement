// Simple user management for the dashboard
export const user = {
  data: null,
  
  // Get user data
  getUser() {
    return this.data
  },
  
  // Set user data
  setUser(userData) {
    this.data = userData
  },
  
  // Clear user data
  clear() {
    this.data = null
  }
}

// Simple user resource without frappe-ui dependency
export const userResource = {
  data: null,
  loading: false,
  error: null,
  
  async load() {
    this.loading = true
    this.error = null
    
    try {
      // Try to get user from window object or make API call
      if (window.frappe && window.frappe.user) {
        this.data = window.frappe.user
      } else {
        // Fallback: make API call to get logged user
        const response = await fetch('/api/method/frappe.auth.get_logged_user', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': window.csrf_token || '',
          }
        })
        
        if (response.ok) {
          const result = await response.json()
          this.data = result.message
        } else {
          throw new Error('Failed to get user data')
        }
      }
    } catch (error) {
      this.error = error
      console.error('Failed to load user:', error)
    } finally {
      this.loading = false
    }
  },
  
  reset() {
    this.data = null
    this.loading = false
    this.error = null
  },
  
  reload() {
    return this.load()
  }
}

// Initialize user from window object if available
if (typeof window !== 'undefined' && window.frappe && window.frappe.user) {
  user.setUser(window.frappe.user)
  userResource.data = window.frappe.user
}
