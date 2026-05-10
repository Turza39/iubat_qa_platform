import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { authService } from '@/services/authService'
import Input from '@/components/ui/Input'
import Button from '@/components/ui/Button'
import Spinner from '@/components/ui/Spinner'
import useRedirectIfAuthenticated from '@/hooks/useRedirectIfAuthenticated'
import { UserPlus } from 'lucide-react'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const { loading: authLoading } = useRedirectIfAuthenticated()

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirm_password: '',
  })

  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  const validate = () => {
    const newErrors = {}

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required.'
    } else if (formData.username.length < 3) {
      newErrors.username = 'Username must be at least 3 characters.'
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required.'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address.'
    }

    if (!formData.password) {
      newErrors.password = 'Password is required.'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters.'
    }

    if (!formData.confirm_password) {
      newErrors.confirm_password = 'Please confirm your password.'
    } else if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match.'
    }

    return newErrors
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    const validationErrors = validate()
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors)
      return
    }

    try {
      setLoading(true)
      console.log('📤 Sending registration data:', {
        username: formData.username,
        email: formData.email,
        password: '***',
        confirm_password: '***',
      })
      
      const registerResponse = await authService.register(formData)
      console.log('✅ Registration successful:', registerResponse)
      
      console.log('🔑 Attempting auto-login...')
      await login({
        email: formData.email,
        password: formData.password,
      })
      console.log('✅ Auto-login successful')
      
      toast.success('Welcome to IUBAT Q&A!')
      navigate('/')
    } catch (error) {
      console.error('❌ Registration error:', error)
      const data = error.response?.data
      if (data) {
        // Handle FastAPI error response format: {"detail": "error message"}
        if (data.detail) {
          console.error('Backend error detail:', data.detail)
          toast.error(data.detail)
        } 
        // Handle Pydantic validation error format (if backend changes)
        else if (data.email || data.username || data.password) {
          const backendErrors = {}
          if (data.email) backendErrors.email = Array.isArray(data.email) ? data.email[0] : data.email
          if (data.username) backendErrors.username = Array.isArray(data.username) ? data.username[0] : data.username
          if (data.password) backendErrors.password = Array.isArray(data.password) ? data.password[0] : data.password
          if (Object.keys(backendErrors).length > 0) {
            setErrors(backendErrors)
          } else {
            toast.error('Registration failed. Please try again.')
          }
        } else {
          toast.error('Registration failed. Please try again.')
        }
      } else if (error.message) {
        toast.error(error.message)
      } else {
        toast.error('Something went wrong. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  // Show spinner while checking auth state
  if (authLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">

        {/* Card */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">

          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-12 h-12 bg-blue-100 rounded-xl mb-4">
              <UserPlus size={22} className="text-blue-600" />
            </div>
            <h1 className="text-2xl font-bold text-slate-800">Create an account</h1>
            <p className="text-slate-500 text-sm mt-1">
              Join the IUBAT student community
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="flex flex-col gap-4">
            <Input
              label="Username"
              name="username"
              type="text"
              value={formData.username}
              onChange={handleChange}
              placeholder="e.g. john_doe"
              error={errors.username}
              required
            />
            <Input
              label="Email Address"
              name="email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="e.g. john@gmail.com"
              error={errors.email}
              required
            />
            <Input
              label="Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Minimum 6 characters"
              error={errors.password}
              required
            />
            <Input
              label="Confirm Password"
              name="confirm_password"
              type="password"
              value={formData.confirm_password}
              onChange={handleChange}
              placeholder="Re-enter your password"
              error={errors.confirm_password}
              required
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              fullWidth
              disabled={loading}
              className="mt-2"
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </Button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3 my-6">
            <div className="flex-1 h-px bg-slate-200" />
            <span className="text-xs text-slate-400">or</span>
            <div className="flex-1 h-px bg-slate-200" />
          </div>

          {/* Login Link */}
          <p className="text-center text-sm text-slate-600">
            Already have an account?{' '}
            <Link
              to="/login"
              className="text-blue-600 font-medium hover:underline"
            >
              Login here
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
