import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from '@/context/AuthContext'
import { Toaster } from 'react-hot-toast'
import Navbar from '@/components/layout/Navbar'

// Pages
import HomePage from '@/pages/HomePage'
import LoginPage from '@/pages/LoginPage'
import RegisterPage from '@/pages/RegisterPage'
import AskPage from '@/pages/AskPage'
import QuestionDetailPage from '@/pages/QuestionDetailPage'
import ProfilePage from '@/pages/ProfilePage'
import VerifyPage from '@/pages/VerifyPage'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <div className="min-h-screen bg-slate-50">
          <Navbar />
          <main className="max-w-5xl mx-auto px-4 py-6">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="/ask" element={<AskPage />} />
              <Route path="/questions/:id" element={<QuestionDetailPage />} />
              <Route path="/profile" element={<ProfilePage />} />
              <Route path="/verify" element={<VerifyPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 3000,
              style: {
                background: '#1e293b',
                color: '#f8fafc',
                borderRadius: '8px',
                fontSize: '14px',
              },
            }}
          />
        </div>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
