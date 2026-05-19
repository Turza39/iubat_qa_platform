import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Automatically attach token to every request if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('🔐 Token attached to request:', `${token.substring(0, 20)}...`)
    } else {
      console.log('⚠️  No token in localStorage, request will be unauthenticated')
    }
    return config
  },
  (error) => {
    console.error('❌ Request error:', error)
    return Promise.reject(error)
  }
)

// Automatically handle 401 errors (token expired or invalid)
api.interceptors.response.use(
  (response) => {
    console.log(`✅ Response ${response.status}:`, response.config.url)
    return response
  },
  (error) => {
    const status = error.response?.status
    const url = error.response?.config?.url
    const message = error.message
    
    if (status === 401) {
      console.error(`❌ 401 Unauthorized on ${url}`)
      console.log('Clearing tokens and redirecting to login...')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      window.location.href = '/login'
    } else if (error.response) {
      console.error(`❌ Response error ${status}:`, url, error.response.data)
    } else {
      console.error(`❌ Network error for ${url}:`, message)
    }
    
    return Promise.reject(error)
  }
)

export default api
