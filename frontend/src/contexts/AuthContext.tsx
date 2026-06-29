import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

interface User {
  id: number
  email: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string) => Promise<void>
  logout: () => void
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')
    if (storedToken && storedUser) {
      setToken(storedToken)
      setUser(JSON.parse(storedUser))
    }
  }, [])

  const login = async (email: string, password: string) => {
    const response = await axios.post('/api/auth/login', { email, password })
    const { access_token, user: userData } = response.data
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(userData))
    setToken(access_token)
    setUser(userData)
  }

  const signup = async (email: string, password: string) => {
    const response = await axios.post('/api/auth/signup', { email, password })
    const { access_token, user: userData } = response.data
    localStorage.setItem('token', access_token)
    localStorage.setItem('user', JSON.stringify(userData))
    setToken(access_token)
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, signup, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  )
}

// Axios interceptor to add JWT token to requests
axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
