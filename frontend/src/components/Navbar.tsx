import React from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const Navbar: React.FC = () => {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  if (!isAuthenticated) {
    return null
  }

  const isActive = (path: string) => location.pathname === path

  return (
    <nav className="bg-gray-800 border-b border-gray-700">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-8">
            <h1 className="text-xl font-bold text-white">Cost Detective</h1>
            <div className="flex gap-4">
              <button
                onClick={() => navigate('/dashboard')}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive('/dashboard')
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => navigate('/history')}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive('/history')
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-300 hover:text-white hover:bg-gray-700'
                }`}
              >
                History
              </button>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <span className="text-gray-300 text-sm">{user?.email}</span>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-medium transition-colors"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
