import { createContext, useContext, useEffect, useState } from 'react'
import { jwtDecode } from 'jwt-decode'
import { authService } from '@/services/authService'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    initializeAuth()
  }, [])
  const initializeAuth = async () => {
    try {
      const token = localStorage.getItem('access_token')
      console.log('🔍 Initializing auth, token exists:', !!token)

      if (token) {
        try {
          const decoded = jwtDecode(token)
          console.log('✅ Token decoded successfully, user_id:', decoded.sub)

          // Check if token is expired
          const expiresAt = new Date(decoded.exp * 1000)
          const isExpired = decoded.exp * 1000 < Date.now()
          console.log(`Token expires at: ${expiresAt}, Expired: ${isExpired}`)

          if (isExpired) {
            console.log('⏰ Token is expired, logging out')
            logout()
          } else {
            console.log('✅ Token is valid, loading user profile')
            await loadUserProfile()
          }
        } catch (decodeError) {
          console.error('❌ Failed to decode token:', decodeError)
          logout()
        }
      } else {
        console.log('No token found, user is not authenticated')
      }
    } catch (error) {
      console.error('❌ Auth initialization error:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const loadUserProfile = async () => {
    try {
      const data = await authService.getProfile()
      // Backend returns the user object directly, not wrapped in profile
      setUser(data)
    } catch (error) {
      console.error('Failed to load user profile:', error)
      logout()
    }
  }

  const login = async (credentials) => {
    try {
      const data = await authService.login(credentials)
      // Backend returns: access_token, token_type, expires_in
      localStorage.setItem('access_token', data.access_token)
      // Token type and expires_in are for reference, not needed in storage
      console.log(`✅ Token stored, expires in ${data.expires_in} seconds`)
      await loadUserProfile()
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  const logout = () => {
    console.log('🚪 Logging out user')
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    setUser(null)
  }

  const refreshUser = async () => {
    console.log('🔄 Refreshing user profile')
    await loadUserProfile()
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
