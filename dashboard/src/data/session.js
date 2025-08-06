import apiService from '../services/api'

// Simple session management for the dashboard
export const session = {
  user: null,
  isLoggedIn: false,
  
  // Initialize session
  init() {
    // Check if user is already logged in from localStorage
    const storedUser = localStorage.getItem('frappe_user')
    if (storedUser) {
      this.user = storedUser
      this.isLoggedIn = true
    } else {
      this.user = null
      this.isLoggedIn = false
    }
  },
  
  // Login method
  async login(email, password) {
    console.log('Session.login called with:', email, password)
    try {
      // Call Frappe login endpoint directly without CSRF token for now
      const response = await fetch('/api/method/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Include cookies for authentication
        body: JSON.stringify({
          usr: email,
          pwd: password
        })
      })
      
      console.log('Login response status:', response.status)
      const data = await response.json()
      console.log('Login response data:', data)
      
      if (response.ok && data.message === "Logged In") {
        this.user = data.message
        this.isLoggedIn = true
        // Store user info for persistence
        localStorage.setItem('frappe_user', data.message)
        return { success: true, user: data.message }
      } else {
        return { success: false, error: data.message || 'Login failed' }
      }
    } catch (error) {
      console.error('Login error:', error)
      return { success: false, error: 'Login failed. Please try again.' }
    }
  },
  
  // Get current user
  getUser() {
    return this.user
  },
  
  // Check if user is logged in
  isAuthenticated() {
    return this.isLoggedIn
  },
  
  // Logout
  logout() {
    this.user = null
    this.isLoggedIn = false
    // Clear stored user info
    localStorage.removeItem('frappe_user')
    sessionStorage.removeItem('frappe_user')
    // Redirect to login page
    window.location.href = '/login'
  },
  
  // Clear session (for testing)
  clearSession() {
    this.user = null
    this.isLoggedIn = false
    localStorage.removeItem('frappe_user')
    sessionStorage.removeItem('frappe_user')
  }
}

// Initialize session on load
if (typeof window !== 'undefined') {
  session.init()
}
