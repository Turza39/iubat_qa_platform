import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'

export default function useRedirectIfAuthenticated(redirectTo = '/') {
  const { user, loading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!loading && user) {
      navigate(redirectTo)
    }
  }, [user, loading, navigate, redirectTo])

  return { loading }
}
